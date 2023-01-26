import requests

from utils.wrappers import async_wrap
from pytube import YouTube


@async_wrap
def download_youtube_video(youtube_url):
    # streams = yt.streams.filter()
    # streams = yt.streams.filter(file_extension='mp4', progressive=True)

    # for stream in streams:
    #     print(stream)
    #     print(stream.filesize)

    youtube_obj = YouTube(youtube_url)
    thumb_url = youtube_obj.thumbnail_url.replace('sddefault.jpg', 'maxresdefault.jpg')
    highest_res_video = youtube_obj.streams.get_highest_resolution()
    def_filename = highest_res_video.default_filename.replace(' ', '_')

    r = requests.get(thumb_url)
    thumb_file_path = f'download_services/temp/youtube/{def_filename.replace("mp4", "jpg")}'
    with open(thumb_file_path, 'wb') as f:
        f.write(r.content)

    highest_res_video.download(output_path=f'download_services/temp/youtube', filename=def_filename)
    return f'download_services/temp/youtube/{def_filename}', thumb_file_path, int(
        highest_res_video.resolution.replace('p', ''))
