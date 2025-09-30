# Base Airflow image
FROM apache/airflow:2.7.2

# System deps for MySQL client libs
USER root
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        gcc \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python deps: MySQL provider + PyMySQL driver
USER airflow
RUN pip install "apache-airflow-providers-mysql==5.1.0" && \
    pip install PyMySQL

