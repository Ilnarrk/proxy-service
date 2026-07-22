FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

ENV PROXY_HOST=0.0.0.0
ENV PROXY_PORT=8080
ENV TARGET_HOST=http://localhost:9000
ENV SOAP_TARGET_HOST=http://localhost:9001

EXPOSE 8080

CMD ["python", "proxy.py"]
