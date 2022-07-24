from kafka import KafkaConsumer
import json
import boto3

lambda_client = boto3.client('lambda')

consumer = KafkaConsumer(
    'foo-group',
     bootstrap_servers=['localhost:9092'],
     #Changing it from earliest
     auto_offset_reset='latest',
     enable_auto_commit=True,
     group_id='foo-consumer-group',
     value_deserializer=lambda x: json.loads(x.decode('utf-8')))

def invoke_lambda(payload):
    lambda_client.invoke(
        FunctionName='deliveryitem-valuation',
        InvocationType='Event',
        Payload=json.dumps(payload),
    )
    print("Event sent to lambda ",payload["body-json"]["powerItemRefNo"])

for message in consumer:
    message = message.value
    invoke_lambda(message)

