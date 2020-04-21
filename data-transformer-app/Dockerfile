FROM amancevice/pandas:1.0.3-alpine

LABEL maintainer="MaxymVlasov"

WORKDIR /app

COPY main.py .

VOLUME [ "/app/data/" ]

CMD ["python3", "-u", "main.py"]
