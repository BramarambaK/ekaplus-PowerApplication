import boto3
import json

lambda_client = boto3.client('lambda')

def invoke_lambda(payload):
    lambda_client.invoke(
        FunctionName='deliveryitem-valuation',
        InvocationType='Event',
        Payload=json.dumps(payload),
    )

if __name__ == "__main__":
    invoke_lambda({"test":"test"})