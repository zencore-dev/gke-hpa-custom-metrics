FROM python:3.10.8

WORKDIR /app

ENV INSTANCE_HOST ''
ENV DB_USER ''
ENV DB_PASS ''
ENV DB_NAME ''
ENV DB_PORT ''
ENV PROJECT_ID ''
ENV QUERY ''
ENV METRIC_NAME ''

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./src/custom_metrics.py" ]