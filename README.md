# Agamotto

Agamotto is a open-source stack that uses IoT (Camera, Beacons, etc) to gather data from physical spaces and use it to deliver insights and intelligence.

## Components and Architecture

Agamotto's initial stack have:

1. Agamotto - Is a simple API that is triggered by Prometheus and read from Stream on every scrape
2. Grafana - Grafana is a multi-platform open source analytics and interactive visualization web application. It provides charts, graphs, and alerts for the web when connected to supported data sources (https://grafana.com/)
3. Prometheus - An open-source monitoring system with a dimensional data model, flexible query language, efficient time series database and modern alerting approach. (https://prometheus.io/)
4. Stream - A camera circuit simulator that reads a mp4 file and expose it in a URL

## How to Deploy

Agamotto's  uses docker-compose and docker to run the initial stack.

1. Install Docker - https://www.docker.com/
2. Install docker-compose https://docs.docker.com/compose/
3. Go to Agamotto's root folder and execute: 

``` shell
git clone https://github.com/google/agamotto
mkdir agamotto
docker-compose up
```

## Services

1. Agamotto runs on 0.0.0.0:9097, it only exports metrics for prometheus to scrape
2. Grafana runs on 0.0.0.0:3000, with admin/admin user and password
3. Prometheus runs on 0.0.0.0:9090, with no authentication
4. Stream runs on 0.0.0.0:9098, with the video feed
