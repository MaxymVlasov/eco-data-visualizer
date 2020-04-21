FROM influxdb:1.8.0-alpine

LABEL maintainer="MaxymVlasov"

COPY add_influx_data.sh /add_influx_data.sh

VOLUME [ "/influx-data/" ]

ENTRYPOINT [ "/add_influx_data.sh" ]
