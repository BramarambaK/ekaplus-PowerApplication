"""Ütility module to generate market price"""
import csv
import random
from string import Template
import datetime
import boto3
from . import config

PRICE_DATA_FILE = "../data/price_generated.csv"
DATE_FORMAT = "%d-%b-%Y"

instrument_names = [
    "Platts Arab Gulf Gasoil 500 ppm", "Platts Arab Gulf Naphtha", "NYMEX Light Sweet Crude Oil(WTI) Futures"]
from_date, to_date = "01-Jan-2020", "30-May-2020"

header_data = """RIC,Trade Date,Security Description,Universal Close Price,Settlement Price,Currency Code,Lot Units,
        Asset SubType,Asset SubType Description,Asset Type,Asset Type Description,Expiration Date,Exchange Description,
        Open Price,Close Price,Ask Price,Bid Price,Derivative Type,Name,Trade Type,Price Unit,Price Source,Price Point,
        Price Sub Type,Published Extrapolated,Hour Ending,Minute Ending"""

price_data_template = Template("""${price_date}_${minute},${price_date},${instrument_name},${price},,EUR,MWh,COMM,Commodities,COMM,
    Commodities,,Epex Spot SE,,${price},,,Spot,${instrument_name},OTC,EUR/MWh,Thomson Reuters,
    Minutely,Peak,Published,${hour},${minute}""")


def generate_5min_price():

    price = ""
    minute = ""

    with open(PRICE_DATA_FILE, "w+") as price_data_file:

        # Splitting multiple line to single line
        price_data_file.write("".join(line.strip()
                                      for line in header_data.splitlines())+"\n")

        pricing_dates = __get_dates_list(from_date, to_date)

        for instrument_name in instrument_names:
            for price_date in pricing_dates:
                __write_hourly_price(
                    price_date, price_data_file, instrument_name)


def generate_and_upload_5min_price_to_s3():
    # generate 5 minutes price
    generate_5min_price()

    s3_resource = boto3.resource("s3")

    # Uploading file in s3 bucket
    file_path = config.PRICE_DATA_FILE_PATH+config.PRICE_DATA_FILE_NAME
    response = s3_resource.Object(
        config.BUCKET_NAME, config.PRICE_DATA_FILE_NAME).upload_file(file_path)
    print("Response ", response)


def __write_5min_price(price_date, price_data_file, instrument_name):
    mins_in_a_day = 60 * 24
    # generate 5 mins price
    for every_5_min in range(0, mins_in_a_day, 5):
        minute = str(every_5_min)
        price = str(10*random.random())
        price_data = price_data_template.substitute(price_date=price_date,
                                                    price=price, minute=minute, instrument_name=instrument_name)
        price_data_file.write("".join(line.strip()
                                      for line in price_data.splitlines())+"\n")


def __write_hourly_price(price_date, price_data_file, instrument_name):
    hours_in_a_day = 24
    # generate 5 mins price
    for every_hour in range(1, hours_in_a_day, 1):
        hour = str(every_hour)
        price = str(10*random.random())
        price_data = price_data_template.substitute(price_date=price_date,
                                                    price=price, hour=hour, minute=0, instrument_name=instrument_name)
        price_data_file.write("".join(line.strip()
                                      for line in price_data.splitlines())+"\n")


def __get_dates_list(from_date_, to_date_):

    from_date = datetime.datetime.strptime(from_date_, DATE_FORMAT)
    to_date = datetime.datetime.strptime(to_date_, DATE_FORMAT)
    date_delta = to_date - from_date
    date_list = [datetime.datetime.strftime(from_date +
                                            datetime.timedelta(days=d), DATE_FORMAT) for d in range(date_delta.days+1)]
    return date_list


if __name__ == "__main__":
    generate_and_upload_5min_price_to_s3()
    # generate_5min_price()
    #__get_dates_list("01-Aug-2019", "31-Aug-2019")
