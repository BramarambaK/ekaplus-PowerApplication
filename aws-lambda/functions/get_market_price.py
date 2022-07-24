import csv
import boto3
import json
from datetime import datetime, timedelta
from time import time
import pandas as pd
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from calendar import monthrange
import os

BUCKET_NAME = os.environ['price_s3_bucket_name']
BASE_PATH = "../data/price/"
DATE_FORMAT = "%d-%b-%Y"
TIME_FORMAT = "%H:%M"
MONTH_YEAR_FORMAT = "%b-%Y"
from_s3 = True
execution_data = {}
price_folder = "9c86d836-36e7-41f1-bb6f-71efd7df43aa/marketprices"
hourly_subhourly_list = [
    "Hourly", "30 Mins(Subhourly)", "15 Mins(Subhourly)", "05 Mins(Subhourly)"]


def lambda_handler(event, context):
    print("Payload ", event)
    header, payload = get_header_n_payload_data(event)
    print("Headers ",header)
    print("Payload ",payload)
    price_data = get_market_price_data(header, payload, from_s3)
    print("price data ", price_data)
    return price_data


def get_header_n_payload_data(event):
    input_body = event["body"]
    input_body = input_body.rstrip('\r\n')
    input_body = json.loads(input_body)
    return event["headers"], input_body


def get_market_price_data_(header, price_request_data, from_s3):
    # Monthly-Baseload
    # Daily-Baseload
    # Daily-Peak
    # Daily-OffPeak1
    # Daily-OffPeak2
    # Hourly
    #SubHourly - Exists

    pass


def get_hourly_sub_hourly_price(header, price_request_data, from_s3):
    curve_list = price_request_data["curves"]
    hourly_subhourly_curves = [
        curve for curve in curve_list if curve["priceSubType"] in hourly_subhourly_list]
    if hourly_subhourly_curves:
        print("Getting prices for hourly, subhourly ")
        get_market_price_data(header, price_request_data,
                              from_s3)


def get_market_price_data(header, price_request_data, from_s3):
    """Initialize the Price provider by loading the files based on delivery"""
    price_data = []
    tenant = header["X-TenantID"]
    from_date = price_request_data["startDate"]
    to_date = price_request_data["endDate"]
    month_list = __get_month_list(from_date, to_date)
    #print("MONTH_LIST ", month_list)
    curve_list = price_request_data["curves"]
    #print("Curve list ",curve_list)
    relative_curve_location = []
    for month in month_list:
        for curve in curve_list:
            if curve["priceSubType"] in hourly_subhourly_list:
                relative_curve_location.append(
                    f"{tenant}/{price_folder}/{curve['name']}/{curve['priceSubType']}/{month}.csv")

    relative_curve_location_set = set(relative_curve_location)
    print("CURVE FILES ", relative_curve_location_set)
    price_data_frame = load_price_data_frame(
        relative_curve_location_set, from_s3)
    print("")
    if not price_data_frame.empty:
        price_data = get_price_for_curve(price_data_frame, price_request_data)

    return price_data


def load_price_data_frame(curve_file_path, from_s3=False):
    prices_df = pd.DataFrame(columns=None)
    error_list = []
    data_frame_list = []
    #print("curve_file_path ", curve_file_path)
    for path in curve_file_path:
        try:
            if from_s3:
                df = load_price_from_s3(path)
            else:
                # load price details from directory
                df = pd.read_csv(BASE_PATH + path)
            data_frame_list.append(df)
        except Exception as fnf:
            error_list.append({"error": fnf})

    if data_frame_list:
        prices_df = pd.concat(data_frame_list)

    print("error list - load dataframe ", error_list)
    return prices_df


def load_price_from_s3(path):
    #print("path L ", path)
    s3_client = boto3.client('s3')
    data_frame = pd.read_csv(s3_client.get_object(
        Bucket=BUCKET_NAME, Key=path)["Body"])
    return data_frame

def get_hourly_price_for_curve(prices_df, price_criteria):
    """"get price for a curve"""
    print("Price dataframe len : ", len(prices_df))
    #curves = price_criteria["curves"]
    #curves_names = [curve["name"] for curve in curves]
    #price_sub_types = [curve["priceSubType"] for curve in curves]
    end_time_str = price_criteria["endTime"]
    start_date = datetime.strptime(price_criteria["startDate"], DATE_FORMAT)
    end_date = datetime.strptime(price_criteria["endDate"], DATE_FORMAT)
    start_time = datetime.strptime(price_criteria["startTime"], TIME_FORMAT)
    end_time = datetime.strptime(end_time_str, TIME_FORMAT)

    prompt_date_series = pd.to_datetime(
        prices_df["Prompt Date"], format="%d-%m-%Y")

    date_filter = (prompt_date_series >= start_date) & (
        prompt_date_series <= end_date)

    hour_ending_series = prices_df["Hour Ending"]

    hour_filter = hour_ending_series >= start_time.hour & hourly_subhourly_list <= end_time.hour

    filter = date_filter & hour_filter
    # & curves_names.isin(prices_df["Instrument Name"]) & price_sub_types.isin(prices_df["Price Sub Type"])

    price_data = prices_df.loc[filter, ["Pricing Date", "Instrument Name", "Prompt Date",
                                        "Hour Ending", "Hour Ending", "Price Sub Type", "Price Point", "Settle Price", "Price Unit"]]

    return price_data.values.tolist()  # to_dict(orient="records")


def get_price_for_curve(prices_df, price_criteria):
    """"get price for a curve"""
    print("Price dataframe len : ", len(prices_df))
    #curves = price_criteria["curves"]
    #curves_names = [curve["name"] for curve in curves]
    #price_sub_types = [curve["priceSubType"] for curve in curves]
    end_time_str = price_criteria["endTime"]
    start_date = datetime.strptime(price_criteria["startDate"], DATE_FORMAT)
    end_date = datetime.strptime(price_criteria["endDate"], DATE_FORMAT)
    start_time = datetime.strptime(price_criteria["startTime"], TIME_FORMAT)
    end_time = datetime.strptime(end_time_str, TIME_FORMAT)

    prompt_date_series = pd.to_datetime(
        prices_df["Prompt Date"], format="%d-%m-%Y")

    start_time_series = pd.to_datetime(
        prices_df["Start Time"], format=TIME_FORMAT)
    end_time_series = pd.to_datetime(prices_df["End Time"], format=TIME_FORMAT)

    date_filter = (prompt_date_series >= start_date) & (
        prompt_date_series <= end_date)

    time_filter = (start_time_series >= start_time)

    # race condition on end_time
    race_condition_end_time = datetime.strptime("00:00", TIME_FORMAT)

    if end_time_str != "00:00":
        time_filter = time_filter & (end_time_series <= end_time) & (
            end_time_series != race_condition_end_time)
    else:
        time_filter = time_filter & (end_time_series >= end_time)

    filter = date_filter & time_filter
    # & curves_names.isin(prices_df["Instrument Name"]) & price_sub_types.isin(prices_df["Price Sub Type"])

    price_data = prices_df.loc[filter, ["Pricing Date", "Instrument Name", "Prompt Date",
                                        "Start Time", "End Time", "Price Sub Type", "Price Point", "Settle Price", "Price Unit"]]

    return price_data.values.tolist()  # to_dict(orient="records")


def __get_month_list(from_date_, to_date_):
    from_date = datetime.strptime(from_date_, DATE_FORMAT)
    #print(" from_date ", from_date)
    to_date = datetime.strptime(to_date_, DATE_FORMAT)
    #print(" to_date ", to_date)
    date_delta = relativedelta(to_date, from_date)
    #print("date_delta ", date_delta.months)
    month_list = [datetime.strftime(from_date+relativedelta(from_date, months=+count), MONTH_YEAR_FORMAT)
                  for count in range(date_delta.months+1)]
    return month_list


if __name__ == "__main__":
    price_filter_criteria = {
        "headers": {
            "X-TenantID": "trm910",
            "X-AccessToken": "",
            "X-Platform-URL": "",
            "X-Platform-HOST": ""
        },
        "body": {
            "startDate": "01-Jan-2020",
            "endDate": "02-Jan-2020",
            "startTime": "22:00",
            "endTime": "23:00",
            "curves": [
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Monthly",
                    "monthYear": "Jun-2020",
                    "priceSubType": "Baseload"
                },
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Daily",
                    "priceSubType": "Peak"
                },
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Daily",
                    "priceSubType": "Baseload"
                },
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Daily",
                    "priceSubType": "Hourly"
                },
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Daily",
                    "priceSubType": "30 Mins(Subhourly)"
                },
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Daily",
                    "priceSubType": "15 Mins(Subhourly)"
                },
                {
                    "name": "NYMEX Light Sweet Crude Oil(WTI) Futures",
                    "pricePoint": "Daily",
                    "priceSubType": "05 Mins(Subhourly)"
                }
            ]
        }
    }
    price_data = get_market_price_data(
        price_filter_criteria["headers"], price_filter_criteria["body"], from_s3)
    print("price data len ", len(price_data))
    print(price_data)
