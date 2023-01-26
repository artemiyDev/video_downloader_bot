import requests
import json
from data.config import TIKTOK_PROXY_LIST
from utils.wrappers import async_wrap
from celery import Celery


# @async_wrap
# def get_tiktok_video_url_worker(tiktok_url):
#     app = Celery('tasks', broker='amqp://user:QwertyUI@84.46.245.185:5672/myvhost',
#                  backend='redis://84.46.245.185:6379/0')
#     proxy_server = 'http://185.239.136.2:8000'
#     proxy_login = 'ex8YWp'
#     proxy_pass = 'Xs51yQ'
#     video_url = app.signature('worker.get_tiktok_video_url', (tiktok_url, proxy_server, proxy_login, proxy_pass),
#                               queue='tiktok').delay().get()
#     return video_url


@async_wrap
def save_tiktok(url):
    r = requests.get(url)
    file_path = f"./123.mp4"
    with open(file_path, 'wb') as f:
        f.write(r.content)
    return file_path




@async_wrap
def get_tiktok_video_url(tiktok_url):
    url = "https://downloader.bot/api/tiktok/info"
    proxy = next(TIKTOK_PROXY_LIST)
    payload = json.dumps({
        "url": tiktok_url
    })
    headers = {
        'authority': 'downloader.bot',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,tr;q=0.5',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://downloader.bot',
        'pragma': 'no-cache',
        'referer': 'https://downloader.bot/en',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload, proxies={'https': 'http://'+proxy})
    video_url = response.json()['data']["mp4"]
    return video_url
