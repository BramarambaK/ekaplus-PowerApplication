import copy
from datetime import datetime, timedelta
from time import time
from . import trade_details_util as util
from . import constants as const


def get_contract(contract_ref_no: str):
    """Get Contract general details of contract with contract_ref_no"""
    return util._get_contract_data_from_json()


def get_items(contract_ref_no: str):
    """Get Delivery item details of contract with contract_ref_no"""
    return util._get_delivery_data_from_json()


def get_all_contracts():
    """Get all contracts from the System"""
    pass


def generate_item_delivery_units(item_details):
    """Generate delivery units for item"""
    pass


def _generate_block_delivery_units(block_item_details):
    """Generate delivery units for item for a Block delivery items"""
    start = time()
    delivery_units = []
    [delivery_units.extend(_generate_block_delivery_unit(item))
     for item in block_item_details]
    print("executed time ", (time()-start))
    return delivery_units


def _generate_block_delivery_unit(block_item):
    """Generate delivery units for item for a Block delivery item"""
    delivery_units = []
    startDate = datetime.strptime(block_item["startDate"], const.DATE_FORMAT)
    endDate = datetime.strptime(block_item["endDate"], const.DATE_FORMAT)
    start_time = datetime.strptime(block_item["startTime"], const.TIME_FORMAT)
    end_time = datetime.strptime(block_item["endTime"], const.TIME_FORMAT)

    dateDelta = endDate - startDate
    totalDays = dateDelta.days + 1

    weekDays = block_item["weekDays"]
    validDays = [key for key, value in weekDays.items() if value]

    one_hour = timedelta(hours=1)

    for d in range(totalDays):
        delivery_date = startDate + timedelta(days=d)
        day = delivery_date.strftime("%A")
        # Filter days selected by user
        if day not in validDays:
            continue

        # delivery unit with fields from block item
        default_delivery_unit = {key: block_item[key]
                                 for key in const.DELIVERY_ITEM_REQUIRED_KEYS}

        st_time = start_time
        while st_time != end_time:
            ed_time = st_time + one_hour

            delivery_unit = copy.deepcopy(default_delivery_unit)
            #delivery_unit[const.K_GENERAL_DETAILS] = general_details

            delivery_unit[const.K_DELIVERY_DATE] = delivery_date.strftime(
                const.DATE_FORMAT)
            delivery_unit[const.K_START_TIME] = st_time.strftime(
                const.TIME_FORMAT)
            delivery_unit[const.K_END_TIME] = ed_time.strftime(
                const.TIME_FORMAT)
            st_time = ed_time
            delivery_units.append(delivery_unit)

    return delivery_units


def _generate_shape_delivery_units(shape_item_details):
    """Generate delivery units for item for a Shape delivery item"""
    pass


if __name__ == "__main__":
    contract_ref_no = ""
    items = get_items(contract_ref_no)
    print(_generate_block_delivery_units(items))
