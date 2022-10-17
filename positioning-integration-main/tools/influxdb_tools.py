# we need to write the positions into influxdb, the influxdb related code is according to https://docs.influxdata.com/influxdb/v2.3/api-guide/client-libraries/python/
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "positioning"  # bucket name in influxdb, precreated in influxdb
org = "AAU"  # org name in influxdb, precreated in influxdb

# precreated token that we use to request influxdb, is is generated when creating a user. We can check it through the command "influx auth list" or from a config file. After recreating the user, we need to change this line of code to reset the token.
token = "hu3K2qr9FMEXZLDWTVuvzEgFXfKjXHUSIY06lGlgrQNdOw0-b-idZnTiH0x8owsa8CdERB6WJeLxNNNvG18SjA=="
url = "http://192.168.100.68:8086"  # url of influxdb

# create a client to request influxdb
inf_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# create a influxdb writer, write_options=SYNCHRONOUS is according to the official guidance of influxdb: https://docs.influxdata.com/influxdb/v2.3/api-guide/client-libraries/python/
inf_write_api = inf_client.write_api(write_options=SYNCHRONOUS)