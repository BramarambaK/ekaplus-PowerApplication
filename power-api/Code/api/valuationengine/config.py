"""Config module to provide application configurations"""

REF_TYPE_ID = "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7"
GENERAL_OBJECT_ID = "73314f69-35dc-43c1-a1db-47d755bafd0d"
ITEM_OBJECT_ID = "0de25ff5-9c68-48fe-abd8-f8e8d4a4132b"
PRICING_REF_TYPE_ID = "84d7b167-1d9f-406d-b974-bea406a25f9a"
FORMULA_OBJECT_ID = "formula"

GENERAL_DETAILS_URL = f"/data/{REF_TYPE_ID}/{GENERAL_OBJECT_ID}"
ITEM_DETAILS_URL = f"/data/{REF_TYPE_ID}/{ITEM_OBJECT_ID}"
FORMULA_DETAILS_URL = f"/data/{PRICING_REF_TYPE_ID}/{FORMULA_OBJECT_ID}"
VALUATION_API_URL = "https://7es0je4527.execute-api.us-east-2.amazonaws.com/dev/deliveryitem-valuation"
PLATFORM_URL = "https://trm910.ekaplus.com"

AUTHORIZATION_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicmVzdF9hcGkiXSwidXNlcl9uYW1lIjoicG9vamFAZWthcGx1cy5jb20iLCJzY29wZSI6WyJ0cnVzdCIsInJlYWQiLCJ3cml0ZSJdLCJleHAiOjE1ODA5OTQ2NTQsImF1dGhvcml0aWVzIjpbIjEyNy4wLjAuMSJdLCJqdGkiOiJlOWVhMWFkNC1kMTNjLTQ1MTQtOTYzOC1iNzJiZTIyOGUxZDciLCJjbGllbnRfaWQiOiI3NGQ3ZTFlNC03MzhlLTM3NmMtYTQ3ZC0xNmFlNzM2OWNiODEiLCJ0aWQiOiI3ZjI0ZDI0MC01MjFkLTM5MDctOWM5My1hZjM5MTcyMTVlZjcifQ.dPmB9Vwkul4slSPjPoOKZrx_JbOxme83DTiziD-ihK8"
TENANT_ID = "trmga"

BUCKET_NAME = "srini-power-data-files"
CONTRACT_FILE_NAME = "contract_data_api.json"
CONTRACT_FILE_PATH = "../data/tmp/"

SQS_QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/789305513040/delivery_unit_queue"

PRICE_DATA_FILE_NAME = "price_generated.csv"
PRICE_DATA_FILE_PATH = "../data/"

DATE_FORMAT = "%d-%b-%Y"


