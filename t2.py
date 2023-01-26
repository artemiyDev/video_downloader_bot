from TikTokApi import TikTokApi
from TikTokApi.helpers import extract_video_id_from_url

api = TikTokApi(proxy='http://ex8YWp:Xs51yQ@185.239.136.2:8000')



video = api.video(url='https://www.tiktok.com/@saan_taan/video/7174056351860149506')

video_url = video.info()['video']['downloadAddr']

print(video_url)




