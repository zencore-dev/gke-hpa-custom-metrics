import sqlalchemy
import time
import os
from google.cloud import monitoring_v3


def connect_tcp_socket() -> sqlalchemy.engine.base.Engine:
    db_host = os.environ["INSTANCE_HOST"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_port = os.environ["DB_PORT"]

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name,
        ),
    )
    return pool

def get_metric(pool, query):
    with pool.connect() as db_conn:
        result = db_conn.execute(query).fetchall()
        for row in result:
            metric_value=row[0]
    return metric_value

def write_metric(project_id, metric_name, metric_value):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/" + metric_name
    series.resource.type = "global"
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    point = monitoring_v3.Point(
        {"interval": interval, "value": {"double_value": metric_value}}
    )
    series.points = [point]
    client.create_time_series(name=project_name, time_series=[series])


## main
time.sleep(30)  # wait for cloudSql proxy to be ready
while True:
    project_id = os.environ["PROJECT_ID"]
    query = os.environ["QUERY"]
    metric_name = os.environ["METRIC_NAME"]

# create a connection
    conn = connect_tcp_socket()

# get metric
    metric_value = get_metric(conn, query)

# write metric to Cloud Monitoring
    write_metric(project_id, metric_name, metric_value)
    time.sleep(60)  # Cloud Monitoring only allows 1 write per minute for each metric