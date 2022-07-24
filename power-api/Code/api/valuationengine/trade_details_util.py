import json
from datetime import datetime
from . import connect_api_util as connect_util
from . import config
from . import constants as const


def _get_contract(headers, contract_ref_no):
    contract_ref_nos = [contract_ref_no]
    body = connect_util.form_filter_criteria(
        const.K_CONTRACT_NO, contract_ref_nos, excludes=const.CONTRACT_EXCLUDES)
    response = connect_util._get(
        config.GENERAL_DETAILS_URL, headers, body=body)
    return response


def _get_contract_all(headers):
    body = connect_util.form_filter_criteria(excludes=const.CONTRACT_EXCLUDES)
    response = connect_util._get(
        config.GENERAL_DETAILS_URL, headers, body=body)
    return response


def _get_contracts(headers, contract_ref_nos):
    body = connect_util.form_filter_criteria(
        const.K_CONTRACT_NO, contract_ref_nos, excludes=const.CONTRACT_EXCLUDES)
    response = connect_util._get(
        config.GENERAL_DETAILS_URL, headers, body=body)
    return response


def _get_contract_item(headers, contract_ref_no):
    params = {const.K_CONTRACT_NO: contract_ref_no}
    response = connect_util._get(
        config.ITEM_DETAILS_URL, headers, params=params)
    return response


def _get_contract_items(headers, contract_ref_nos):

    body = connect_util.form_filter_criteria(
        const.K_CONTRACT_NO, contract_ref_nos, excludes=const.CONTRACT_ITEM_EXCLUDES)

    response = connect_util._get(
        config.ITEM_DETAILS_URL, headers, body=body)
    return response


def _get_contract_item_all(headers):
    response = connect_util._get(
        config.ITEM_DETAILS_URL, headers)
    return response


def _get_contract_data_from_json():
    with open("../data/general_detail.json") as general_detail_file:
        data = json.load(general_detail_file)
    return data


def _get_delivery_data_from_json():
    with open("../data/delivery_item_block.json") as delivery_item_block_file:
        data = json.load(delivery_item_block_file)
    return data


def get_contract_ref_nos(contract_details):
    contract_ref_nos = [contract_data[const.K_CONTRACT_NO]
                        for contract_data in contract_details]
    return contract_ref_nos


def get_formula_ids(contract_details, item_details):
    valuation_formula_ids = {contract_data[const.K_VALUATION_FORMULA_ID]
                             for contract_data in contract_details if const.K_VALUATION_FORMULA_ID in contract_data}
    delivery_item_formula_ids = {delivery_data[const.K_EXPRESSION]
                                 for delivery_data in item_details if const.K_EXPRESSION in delivery_data}
    formula_ids = list(valuation_formula_ids.union(delivery_item_formula_ids))
    return formula_ids


def populate_contract_info_in_item_details(item_details, contract_dict, formula_dict, valuation_date):
    for item in item_details:
        item["valuationRunDate"] = valuation_date
        contract_data = contract_dict[item[const.K_CONTRACT_NO]]

        if const.K_EXPRESSION in item.keys() and item[const.K_EXPRESSION]:
            formula = formula_dict[item[const.K_EXPRESSION]]
            item["formulaDetails"] = formula

        if const.K_VALUATION_FORMULA_ID in contract_data.keys():
            valuation_formula = formula_dict[contract_data[const.K_VALUATION_FORMULA_ID]]
            item["valuationFormulaDetails"] = valuation_formula

        item.update(contract_data)


if __name__ == "__main__":
    # print(_get_delivery_data_from_json())

    date = "11-05-2020"
    from_date = datetime.strptime(date, "%d-%m-%Y")
    print(from_date.strftime("%b-%Y"))
