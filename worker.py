# import time
# import random
#
# from celery import Celery
#
# # Wait for rabbitmq to be started
# # time.sleep(15)
#
# app = Celery('tasks', backend='rpc://', broker='pyamqp://')
#
# from TikTokApi import TikTokApi
#
#
#
#
# # @app.task
# # def add2(x, y):
# #     return x + y
# #
# #
# # @app.task(name='tikTok')  # Named task
# # def add():
# #     print('aaa')
# #     url = 'https://www.tiktok.com/@saan_taan/video/7174056351860149506?is_from_webapp=1&sender_device=pc'
# #     # api = TikTokApi()
# #     # video = api.video(
# #     # url='https://www.tiktok.com/@saan_taan/video/7174056351860149506?is_from_webapp=1&sender_device=pc')
# #     # video_url = video.info()['video']['downloadAddr']
# #     print(url)
# #     return url
# #
# # # celery -A worker worker --loglevel=info
#
#
# @app.task
# def add(x, y):
#     print('AAAAAAAAAAAAAAAAAAA')
#     return x + y
import time

from celery import Celery

app = Celery('tasks', broker='amqp://user:QwertyUI@84.46.245.185:5672/myvhost', backend='redis://84.46.245.185:6379/0')

print('done')
proxy_server = 'http://185.239.136.2:8000'
proxy_login = 'ex8YWp'
proxy_pass = 'Xs51yQ'

tiktok_url = 'https://www.tiktok.com/@karisrose01/video/7184449708402806022?is_from_webapp=1&sender_device=pc'

result = app.signature('worker.get_tiktok_video_url', (tiktok_url,proxy_server, proxy_login, proxy_pass), queue='tiktok').delay().get()
print(result)


