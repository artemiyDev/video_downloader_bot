from TikTokApi import TikTokApi

api = TikTokApi()



video = api.video(url='https://www.tiktok.com/@saan_taan/video/7174056351860149506?is_from_webapp=1&sender_device=pc')

video_url = video.info()['video']['downloadAddr']

print(video_url)
