FROM python:3.12

# https://www.pybootcamp.com/blog/how-to-write-dockerfile-python-apps/
RUN mkdir /app

RUN apt update -y && apt install build-essential python3-dev libxslt-dev libxml2 -y
WORKDIR /app

RUN pip3 install -U \
    pip \
    'setuptools' \
    wheel

# separate copy so the docker cache doesn't get invalidated unless requirements change
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# then copy our code
COPY dashboard.py .

EXPOSE 5000
ENV GRADIO_SERVER_NAME="0.0.0.0"

ENTRYPOINT ["python3", "/app/dashboard.py"]
