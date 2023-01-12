FROM mcr.microsoft.com/playwright/python

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt
#RUN playwright install
#RUN playwright install-deps

COPY . .

ENTRYPOINT celery -A worker worker --loglevel=info
