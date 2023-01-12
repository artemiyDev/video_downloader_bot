from TikTokApi import TikTokApi
from utils.wrappers import async_wrap
from celery import Celery




@async_wrap
def get_tiktok_video_url(tiktok_url):
    app = Celery('tasks', broker='amqp://user:QwertyUI@84.46.245.185:5672/myvhost',
                 backend='redis://84.46.245.185:6379/0')
    proxy_server = 'http://185.239.136.2:8000'
    proxy_login = 'ex8YWp'
    proxy_pass = 'Xs51yQ'
    video_url = app.signature('worker.get_tiktok_video_url', (tiktok_url, proxy_server, proxy_login, proxy_pass),
                           queue='tiktok').delay().get()
    return video_url
