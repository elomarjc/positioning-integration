import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import datetime
import arrow
import rfc3339

import math

# some variables to access and query influxdb
org = "AAU"
token = "hu3K2qr9FMEXZLDWTVuvzEgFXfKjXHUSIY06lGlgrQNdOw0-b-idZnTiH0x8owsa8CdERB6WJeLxNNNvG18SjA=="
url = "http://192.168.100.68:8086"
inf_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
inf_query_api = inf_client.query_api()

bucket = "positioning"
tid = "5336"
experiment_start_time = "2022-07-14T15:41:00Z"
experiment_stop_time = "2022-07-14T16:41:00Z"
filter_uwb = 'fn: (r) => r._measurement == "uwb"'
filter_tid = 'fn: (r) => r.tagid == "{}"'.format(tid)
filter_cv = 'fn: (r) => r._measurement == "cv"'
filter_x = 'fn: (r) => r._field == "x"'
filter_y = 'fn: (r) => r._field == "y"'

# query influxdb every 100ms, from the experiment_start_time to the experiment_stop_time
first_time = arrow.get(experiment_start_time).datetime
last_time = arrow.get(experiment_stop_time).datetime
duration = datetime.timedelta(milliseconds=100)


# every time of query, we record the value and time of cv_x, uwb_x, cv_y, uwb_y, and the distance between the cv position and the uwb position.
class record():

    def __init__(self, query_t, cv_x, cv_xt, cv_y, cv_yt, uwb_x, uwb_xt, uwb_y,
                 uwb_yt, dist):
        self.query_t = query_t
        self.cv_x = cv_x
        self.cv_xt = cv_xt
        self.cv_y = cv_y
        self.cv_yt = cv_yt
        self.uwb_x = uwb_x
        self.uwb_xt = uwb_xt
        self.uwb_y = uwb_y
        self.uwb_yt = uwb_yt
        self.dist = dist


total_results = []

# loop of influxdb query
t = first_time + duration * 10
while t < last_time:
    t_str = rfc3339.format_millisecond(t, utc=True, use_system_timezone=False)
    print("Query influxdb time: {}".format(t_str))

    # query cv_x
    query_cv_x = 'from(bucket:"{bucket}")\
    |> range(start:{start_time}, stop:{stop_time})\
    |> filter({filter1})\
    |> filter({filter2})\
    |> group()\
    |> sort(columns: ["_time"], desc: false)\
    |> last()\
    '.format(bucket=bucket,
             start_time=experiment_start_time,
             stop_time=t_str,
             filter1=filter_cv,
             filter2=filter_x)

    results = []
    results = inf_query_api.query(org=org, query=query_cv_x)
    result_cv_x = results[0].records[0]

    # query cv_y
    query_cv_y = 'from(bucket:"{bucket}")\
    |> range(start:{start_time}, stop:{stop_time})\
    |> filter({filter1})\
    |> filter({filter2})\
    |> group()\
    |> sort(columns: ["_time"], desc: false)\
    |> last()\
    '.format(bucket=bucket,
             start_time=experiment_start_time,
             stop_time=t_str,
             filter1=filter_cv,
             filter2=filter_y)

    results = []
    results = inf_query_api.query(org=org, query=query_cv_y)
    result_cv_y = results[0].records[0]

    # query uwb_x
    query_uwb_x = 'from(bucket:"{bucket}")\
    |> range(start:{start_time}, stop:{stop_time})\
    |> filter({filter1})\
    |> filter({filter2})\
    |> filter({filter3})\
    |> group()\
    |> sort(columns: ["_time"], desc: false)\
    |> last()\
    '.format(bucket=bucket,
             start_time=experiment_start_time,
             stop_time=t_str,
             filter1=filter_uwb,
             filter2=filter_tid,
             filter3=filter_x)

    results = []
    results = inf_query_api.query(org=org, query=query_uwb_x)
    result_uwb_x = results[0].records[0]

    # query uwb_y
    query_uwb_y = 'from(bucket:"{bucket}")\
    |> range(start:{start_time}, stop:{stop_time})\
    |> filter({filter1})\
    |> filter({filter2})\
    |> filter({filter3})\
    |> group()\
    |> sort(columns: ["_time"], desc: false)\
    |> last()\
    '.format(bucket=bucket,
             start_time=experiment_start_time,
             stop_time=t_str,
             filter1=filter_uwb,
             filter2=filter_tid,
             filter3=filter_y)

    results = []
    results = inf_query_api.query(org=org, query=query_uwb_y)
    result_uwb_y = results[0].records[0]

    # calculate the distance between the cv position and the uwb position
    dist = math.sqrt(
        pow((float(result_cv_x.get_value()) -
             float(result_uwb_x.get_value())), 2) +
        pow((float(result_cv_y.get_value()) -
             float(result_uwb_y.get_value())), 2))

    # use the cv_x, uwb_x, cv_y, uwb_y, and distance to make a record
    this_record = record(t_str, result_cv_x.get_value(),
                         result_cv_x.get_time(), result_cv_y.get_value(),
                         result_cv_y.get_time(), result_uwb_x.get_value(),
                         result_uwb_x.get_time(), result_uwb_y.get_value(),
                         result_uwb_y.get_time(), dist)

    # put the record into the total_results
    total_results.append(this_record)

    # in the next loop, we need to query the data after the time of "duration"
    t = t + duration

# write the total_results into the csv file
response = 'query_time,cv_x,cv_xt,cv_y,cv_yt,uwb_x,uwb_xt,uwb_y,uwb_yt,dist\n'
for one_record in total_results:
    response += '{},{},{},{},{},{},{},{},{},{}\n'.format(
        one_record.query_t, one_record.cv_x, one_record.cv_xt, one_record.cv_y,
        one_record.cv_yt, one_record.uwb_x, one_record.uwb_xt,
        one_record.uwb_y, one_record.uwb_yt, one_record.dist)
output = open("every_100ms_uwb_cv_dist.csv", "w+")
output.write(response)
output.close()
