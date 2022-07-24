"""Ütility module to generate market price"""
import csv
import random
from string import Template
import datetime
from datetime import timedelta
import boto3
from . import config
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from calendar import monthrange
import os

BASE_FOLDER = "../data/price"
DATE_FORMAT = "%d-%b-%Y"
DATE_FORMAT_ = "%d-%m-%Y"
MONTH_YEAR_FORMAT = "%b-%Y"
TENANT_NAME = "trmga"
price_folder = "9c86d836-36e7-41f1-bb6f-71efd7df43aa/marketprices"

instrument_names = [
    "Platts Arab Gulf Gasoil 500 ppm", "Platts Arab Gulf Naphtha","NYMEX Light Sweet Crude Oil(WTI) Futures"]
from_date, to_date = "01-Jul-2020", "31-Dec-2020"

header_data = """Pricing Date,Prompt Date,Derivative Type,Exchange,Instrument Name,Start Time,End Time,Month Year,
            Trade Type,Settle Price,Premium,Price Unit,Option Type,Delta,Price Source,Price Point,Price Sub Type,
            Open,Close,Ask,Bid,High,Low,Price Symbol,Published Extrapolated,Publisher"""

header_data_hourly = """Pricing Date,Prompt Date,Derivative Type,Exchange,Instrument Name,Month Year,
            Trade Type,Settle Price,Premium,Price Unit,Option Type,Delta,Price Source,Price Point,Price Sub Type,
            Open,Close,Ask,Bid,High,Low,Price Symbol,Published Extrapolated,Publisher,Hour Ending"""

price_data_template = Template("""${pricing_date},${prompt_date},Physical,Exchange,${instrument_name},
                                ${start_time},${end_time},MonthYear,Physical,${price},0.0,EUR/MWh,
                                Option,Delta,Market,Daily,${price_sub_type},,,,,,,Settlement,Settlement,Exchange""")


price_data_template_hourly = Template("""${pricing_date},${prompt_date},Physical,Exchange,${instrument_name},
                                MonthYear,Physical,${price},0.0,EUR/MWh,
                                Option,Delta,Market,Daily,${price_sub_type},,,,,,,Settlement,Settlement,Exchange,${hourEnding}""")

price_sub_types_config = {
    "60m": {"price_sub_type": "Hourly", "hours": 24},
    "30m": {"price_sub_type": "30 Mins(Subhourly)", "mins": 30},
    "15m": {"price_sub_type": "15 Mins(Subhourly)", "mins": 15},
    "05m": {"price_sub_type": "05 Mins(Subhourly)", "mins": 5}
}


def generate_sub_hourly_price():
    """Generate 5 minutes price for the duration and instrument list"""
    month_list = __get_month_list(from_date, to_date)
    file_list = []
    for instrument_name in instrument_names:
        print("Generating price for ", instrument_name)
        for month in month_list:
            print("Generating price for month ", month)
            data_dir = f"{BASE_FOLDER}"
            #os.makedirs(data_dir, exist_ok=True)
            # file_name = f"{data_dir}/{TENANT_NAME}/{instrument_name}/{month}.csv"
            
            pricing_dates = __get_dates_in_month(month)
            for key in price_sub_types_config.keys():
                price_sub_type = price_sub_types_config[key]["price_sub_type"]
            
                directory = f"{data_dir}/{TENANT_NAME}/{price_folder}/{instrument_name}/{price_sub_type}"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                price_file_name = f"{directory}/{month}.csv"
            
                file_list.append(price_file_name)

                with open(price_file_name, "w+") as price_data_file:
                    # Splitting multiple line to single line
                    header = header_data
                    if key =="60m":
                        header = header_data_hourly
                    price_data_file.write("".join(line.strip()
                                            for line in header.splitlines())+"\n")
                    for price_date in pricing_dates:
                        if key =="60m":
                            __write_hourly_price(
                                price_date, price_data_file, instrument_name)
                        else:
                            __write_subhourly_price_for_a_day(
                                price_date, price_data_file, instrument_name, key)
                    price_data_file.close()
    return file_list


def generate_and_upload_5min_price_to_s3():
    # generate sub hourly prices
    file_list = generate_sub_hourly_price()
    create_s3_folders(file_list)
    upload_files(file_list)

def upload_files(file_list):
    s3_resource = boto3.resource("s3")
    for file_ in file_list:
        source_file_path = file_
        s3_file_path = source_file_path.replace(BASE_FOLDER+"/","")
        print(source_file_path, "\n",s3_file_path)
        upload_file_to_s3(s3_resource, s3_file_path, source_file_path)
        
    
def create_s3_folders(file_list):
    s3 = boto3.client('s3')
    bucket_name = config.BUCKET_NAME
    s3_folder_set= set([])
    for file_ in file_list:
        directory_name = file_.rsplit("/",1)
        s3_key_directory = directory_name[0]
        s3_directory = s3_key_directory.replace(BASE_FOLDER+"/","")
        # print(s3_directory)
        s3_folder_set.add(s3_directory)
    
    for s3_folder in s3_folder_set:
        #print("s3_folder ",s3_folder)
        response = s3.put_object(Bucket=bucket_name, Key=(s3_folder+'/'))
        #print("Response - Create Folder ",response)

def upload_file_to_s3(s3_resource, s3_file_path, source_file_path):
    """Uploading file in s3 bucket"""
    print("Source file_path ", source_file_path)
    print("S3 file_path ", s3_file_path)
    response = s3_resource.Object(
        config.BUCKET_NAME, s3_file_path).upload_file(source_file_path)
    print("Response ", response)


def __write_subhourly_price_for_a_day(price_date, price_data_file, instrument_name, sub_hour_mins):
    
    price_sub_type_config = price_sub_types_config[sub_hour_mins]
    sub_hr_mins = price_sub_type_config["mins"]
    price_sub_type = price_sub_type_config["price_sub_type"]
    # generate 5 mins price
    sub_hour_list = get_sub_hour_list(sub_hr_mins)
    for index in range(len(sub_hour_list)-1):
        start_time = sub_hour_list[index]
        end_time = sub_hour_list[index+1]
        price = str(10*random.random())
        price_data = price_data_template.substitute(pricing_date=price_date, prompt_date=price_date,
                                                    price=price, start_time=start_time, end_time=end_time,
                                                    instrument_name=instrument_name, price_sub_type=price_sub_type)
        price_data_file.write("".join(line.strip()
                                      for line in price_data.splitlines())+"\n")
    

def __write_hourly_price(price_date, price_data_file, instrument_name):
    hours_in_a_day = 24
    price_sub_type = "Hourly"
    # generate 5 mins price
    for every_hour in range(1, hours_in_a_day+1, 1):
        hour = str(every_hour)
        price = str(10*random.random())
        price_data = price_data_template_hourly.substitute(pricing_date=price_date, prompt_date=price_date,
                                                    price=price,hourEnding = hour, 
                                                    instrument_name=instrument_name, price_sub_type=price_sub_type)
        price_data_file.write("".join(line.strip()
                                      for line in price_data.splitlines())+"\n")


def __get_dates_in_month(month_date):
    date_ = datetime.datetime.strptime(month_date, MONTH_YEAR_FORMAT)
    days_in_month = monthrange(date_.year, date_.month)[1]
    dates_in_a_month = [datetime.datetime.strftime(
        date_, DATE_FORMAT_) for date_ in rrule(DAILY,  dtstart=date_, count=days_in_month)]
    return dates_in_a_month


def __get_dates_list(from_date_, to_date_):

    from_date = datetime.datetime.strptime(from_date_, DATE_FORMAT)
    to_date = datetime.datetime.strptime(to_date_, DATE_FORMAT)
    date_delta = to_date - from_date
    date_list = [datetime.datetime.strftime(from_date +
                                            datetime.timedelta(days=d), DATE_FORMAT) for d in range(date_delta.days+1)]
    return date_list


def __get_month_list(from_date_, to_date_):
    from_date = datetime.datetime.strptime(from_date_, DATE_FORMAT)
    to_date = datetime.datetime.strptime(to_date_, DATE_FORMAT)
    date_delta = relativedelta(to_date, from_date)
    month_list = [datetime.datetime.strftime(from_date+relativedelta(from_date, months=+count), MONTH_YEAR_FORMAT)
                  for count in range(date_delta.months+1)]
    return month_list

def get_sub_hour_list(sub_hour_mins):
    from_date = datetime.datetime.strptime("01-Jan-2020", DATE_FORMAT)
    mins_in_a_day = 60 * 24
    range_ = int(mins_in_a_day/sub_hour_mins)

    sub_hour_list = [td.strftime("%H:%M") for td in (from_date+timedelta(minutes=sub_hour_mins*it) for it in range(int(range_+1)))]
    
    return sub_hour_list

def get_sub_folders_from_s3():
    
    bucket = config.BUCKET_NAME
    # Make sure you provide / in the end
    prefix = 'trm910/'  
    client = boto3.client('s3')
    #resp = client.put_object(Bucket=bucket, Key=('trm910/test/'))
    #print(resp)
    result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
    for o in result.get('CommonPrefixes'):
        print('sub folder : ', o.get('Prefix'))

if __name__ == "__main__":
    generate_and_upload_5min_price_to_s3()
    # generate_sub_hourly_price()
    # get_sub_hour_list(30)
    # walk_to_price_files()
    #get_sub_folders_from_s3()
