
def delivery_units_to_list(delivery_units):
    delivery_units_list = [
        list(delivery_unit.values()) for delivery_unit in delivery_units]
    return delivery_units_list


if __name__ == "__main__":
    delivery_units = [{
        "powerContractRefNo": "PW-14-REF",
        "quantityUnitDisplayName": "MT",
        "payInCurIdDisplayName": "CAD",
        "blockNo": 1,
        "price": 200,
        "quantity": 200,
        "expression": "5eaf6b1de21b840001c59ce6",
        "priceType": "FormulaPricing",
        "powerItemRefNo": "PW-7-ITEM",
        "priceUnitDisplayName": "USD/BBL",
        "deliveryDate": "22-01-2020",
        "startTime": "13:00",
        "endTime": "14:00",
        "formulaDetails": {
            "includedCurves": [
                "NYMEX Light Sweet Crude Oil(WTI) Futures"
            ]
        }
    }, {
        "powerContractRefNo": "PW-14-REF",
        "quantityUnitDisplayName": "MT",
        "payInCurIdDisplayName": "CAD",
        "blockNo": 1,
        "price": 200,
        "quantity": 200,
        "expression": "5eaf6b1de21b840001c59ce6",
        "priceType": "FormulaPricing",
        "powerItemRefNo": "PW-7-ITEM",
        "priceUnitDisplayName": "USD/BBL",
        "deliveryDate": "22-01-2020",
        "startTime": "13:00",
        "endTime": "14:00",
        "formulaDetails": {
            "includedCurves": [
                "NYMEX Light Sweet Crude Oil(WTI) Futures"
            ]
        }
    }]
    print(delivery_units_to_list(delivery_units))
