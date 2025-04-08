from kafka import KafkaConsumer
from prometheus_client import Counter, Histogram, start_http_server

topic = 'movielog20'

start_http_server(8765)

# Metrics like Counter, Gauge, Histogram, Summaries
# Refer https://prometheus.io/docs/concepts/metric_types/ for details of each metric
# Define metrics to show request count. Request count is total number of requests made with a particular HTTP status.
REQUEST_COUNT = Counter(
    'request_count', 'Recommendation Request Count',
    ['http_status']
)

# Define a separate counter for requests with HTTP status 200
REQUEST_COUNT_200 = Counter(
    'request_count_200', 'Count of Requests Returning HTTP 200'
)

REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')


def main():
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        group_id=topic,
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )

    for message in consumer:
        event = message.value.decode('utf-8')
        values = event.split(',')
        if 'recommendation request' in values[2]:
            # Extract the status code from the message and use it as a label for the metric.
            status = values[3].split(" ")[1]
            REQUEST_COUNT.labels(status).inc()

            # Increment the counter for HTTP 200 responses if applicable
            if status == "200":
                REQUEST_COUNT_200.inc()

            # Updating request latency histogram
            time_taken = float(values[-1].strip().split(" ")[0])
            REQUEST_LATENCY.observe(time_taken / 1000)

            print(event)


if __name__ == "__main__":
    main()
