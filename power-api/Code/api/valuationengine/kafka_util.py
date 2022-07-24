from json import dumps
from kafka import KafkaProducer
from . import kafka_constants as k_consts



class Kafka_Producer():

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))
        print(self.producer)
        

    def send(self,message):
        print("Sending message to Topic")
        self.producer.send(k_consts.KAFKA_TOPIC, value=message)
        print("Message posted successfully")
