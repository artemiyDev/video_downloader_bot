FROM python:3.11
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/artemiyDev/instaloader.git
CMD tail -f /dev/null