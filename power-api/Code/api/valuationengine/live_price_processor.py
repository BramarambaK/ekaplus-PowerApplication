from . import trade_details_util
from . import formula_details_util


def process_item_price(headers, item_versions):
    
    latest_item = get_latest_item_version(item_versions)

    item = __get_item_for_price_valuation(headers,latest_item)

    return item


def get_latest_item_version(item_versions):
    versions = item_versions["payLoadData"]["versions"]

    if not versions:
        print("Data not available in versions")
        return None

    latest_item = max(versions, key=lambda x: x["sys__version"])
    return latest_item

def __get_item_for_price_valuation(headers,item):
    item_no = item["powerItemRefNo"]
    contract_no = item["powerContractRefNo"]
    if "expression" not in item:
        print("Formula details not available in Item")
        print("Ignoring item from processing", contract_no, item_no)
        return {"status": "Success", "message": f"{item_no} , Item not applicable for processing"}

    
    contract_details = trade_details_util._get_contract(
        headers, contract_no)

    formula_expression = item["expression"]
    formula_detail = formula_details_util._get_formula_detail(
        headers, formula_expression)

    if not formula_detail:
        print("Formula details not available ", formula_expression)
        return {"status": "Failed", "message": f"{formula_expression} , formula not available in the system"}

    item["formulaDetails"] = formula_detail[0]

    #print(contract_details[0])
    item.update(contract_details[0])
    return item
