FROM amancevice/pandas:1.0.3-alpine

LABEL maintainer="MaxymVlasov"

WORKDIR /app

COPY main.py requirements-dev.txt ./

ARG ENV="${ENV:-prod}"
RUN if [ "$ENV" != 'prod' ]; then \
        pip3 --no-cache-dir install -r requirements-dev.txt; \
    fi

VOLUME [ "/app/data/" ]

CMD ["python3", "-u", "main.py"]
