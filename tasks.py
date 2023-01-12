import asyncio

from celery import Celery
from TikTokApi import TikTokApi
from selenium import webdriver
from bs4 import BeautifulSoup as bs


app = Celery('tasks', broker='redis://84.46.245.185:6379/0')


@app.task
def tik():
    # driver = webdriver.Chrome()
    #
    # driver.get('https://www.tiktok.com/@saan_taan/video/7174056351860149506?is_from_webapp=1&sender_device=pc')
    #
    # soup = bs(driver.page_source, 'lxml')
    # video = soup.find('video')
    # driver.close()
    # print(video)
    asyncio.new_event_loop()
    with TikTokApi() as api:
        api = TikTokApi()
        video = api.video(url='https://www.tiktok.com/@saan_taan/video/7174056351860149506?is_from_webapp=1&sender_device=pc')
        video_url = video.info()['video']['downloadAddr']
    return video_url

