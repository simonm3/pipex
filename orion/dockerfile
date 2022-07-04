FROM python:3.7-slim-buster

# requirements separate so prefect can be updated without reinstalling everything
COPY requirements.txt .
RUN pip install -r requirements.txt
# uvloop pinned due to bug
RUN pip install -U "prefect>=2.0b2" "uvloop>=0.16.0"

# used for orion_setup container
RUN mkdir -p /v1/storage
COPY orion_setup.sh .

CMD ["prefect", "orion", "start", "--host", "0.0.0.0"]