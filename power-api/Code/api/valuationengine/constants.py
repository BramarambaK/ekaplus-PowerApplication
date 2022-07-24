DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"

COLLECTION_NAME_DELIVERY_UNIT = "Power_Exposure_Delivery_Unit"
COLLECTION_NAME_ITEM = "Power_Exposure_Item"

CONTRACT_EXCLUDES = ["_id","sys__state","refType","refTypeId","sys__UUID","object",
                "sys__createdBy","sys__createdOn","sys__data__state","sys__updatedBy","sys__updatedOn",
                "applicableLawContract","arbitration","cpName","dealType","facilityLocation",
                "paymentTerms","product","profitCenter","strategy","taxScheduleCountryId","taxScheduleId","traderName"]

CONTRACT_ITEM_EXCLUDES = ["_id","sys__state","refType","refTypeId","sys__UUID","object",
                "sys__createdBy","sys__createdOn","sys__data__state","sys__updatedBy","sys__updatedOn",
                "endDateDatePicker","endTimeTimePicker","startDateDatePicker","startTimeTimePicker","weekDays"]
FORMULA_EXCLUDES = ["priceDifferential","contract","refType","refTypeId","sys__UUID","object",
                "sys__createdBy","sys__createdOn","sys__data__state","sys__updatedBy","sys__updatedOn"]

CONTRACT_REQUIRED_KEYS = ["contractType", "traderNameDisplayName", "dealType", "cpNameDisplayName", "powerContractRefNo", 
                          "contractIssueDate", "dealTypeDisplayName", "contractTypeDisplayName", "paymentTermsDisplayName", 
                          "taxScheduleIdDisplayName", "profitCenterDisplayName", "strategyDisplayName", "taxScheduleId", 
                          "facilityLocationDisplayName", "taxScheduleCountryIdDisplayName", "deliveryType", 
                          "deliveryTypeDisplayName", "productDisplayName"
                          ]

DELIVERY_ITEM_REQUIRED_KEYS = ["powerContractRefNo", "quantityUnitDisplayName", "payInCurIdDisplayName",
                               "blockNo", "price", "quantity", "expression", "priceType", "powerItemRefNo", "priceUnitDisplayName", "weekDays"]

DELIVERY_ITEM_REQUIRED_KEYS_ = ["powerContractRefNo", "quantityUnitDisplayName", "payInCurIdDisplayName",
                                "blockNo", "price", "quantity", "expression", "priceType", "powerItemRefNo", "priceUnitDisplayName", "contractType", 
                                "traderNameDisplayName", "dealType", "cpNameDisplayName", "contractIssueDate", "dealTypeDisplayName", "contractTypeDisplayName", 
                                "paymentTermsDisplayName", "taxScheduleIdDisplayName", "profitCenterDisplayName", "strategyDisplayName", "taxScheduleId", 
                                "facilityLocationDisplayName", "taxScheduleCountryIdDisplayName", "deliveryType", "deliveryTypeDisplayName", "productDisplayName"]

K_VALUATION_RUN_DATE = "valuationRunDate"
K_GENERAL_DETAILS = "general_details"
K_ITEM_DETAILS = "item_details"
K_DELIVERY_DATE = "deliveryDate"
K_START_TIME = "startTime"
K_END_TIME = "endTime"
K_PRICE_TYPE = "priceType"
K_FORMULA_EXP = "formulaExpression"
K_PRICE = "price"
K_PAYIN_CUR = "payInCurId"
K_PRICE_UNIT = "priceUnit"
K_CONTRACT_NO = "powerContractRefNo"
K_ITEM_NO = "powerItemRefNo"
K_DELIVERY_FREQ = "deliveryFrequency"
K_QUANTITY = "quantity"
K_QUANTITY_UNIT = "quantityUnit"
K_FORMULA_IDS = "formulaIds"
K_CONTRACT_NOS = "powerContractRefNos"
K_VALUATION_FORMULA_ID = "valuationFormulaId"
K_EXPRESSION = "expression"
K_REALIZED="REALIZED"
K_UNREALIZED="UNREALIZED"
