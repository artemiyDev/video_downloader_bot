import requests
import os
import re
from pytube.exceptions import AgeRestrictedError
from utils.wrappers import async_wrap
from pytube import YouTube
from pytube import innertube
import string
import time
import glob
@async_wrap
def download_youtube_video(youtube_url,message_chat_id):
    def make_valid_filename(input_string):
        # Remove invalid characters
        valid_chars = "-_.() %s%s" % (re.escape(string.ascii_letters), re.escape(string.digits))
        filename = re.sub(r"[^%s]" % valid_chars, "", input_string)

        # Replace spaces with underscores
        filename = filename.replace(" ", "_")

        # Truncate filename if necessary
        max_length = 255  # Maximum filename length (adjust as needed)
        if len(filename) > max_length:
            filename = filename[:max_length]

        return filename

    innertube._cache_dir = '.'
    innertube._token_file = os.path.join(innertube._cache_dir, 'tokens.json')
    # streams = yt.streams.filter()
    # streams = yt.streams.filter(file_extension='mp4', progressive=True)

    # for stream in streams:
    #     print(stream)
    #     print(stream.filesize)

    youtube_obj = YouTube(youtube_url,use_oauth=True, allow_oauth_cache=True)
    thumb_url = youtube_obj.thumbnail_url.replace('sddefault.jpg', 'maxresdefault.jpg')


    # try:
    #     highest_res_video = youtube_obj.streams.get_highest_resolution()
    #     def_filename = highest_res_video.default_filename.replace(' ', '_')
    #     highest_res_video.download(output_path=f'download_services/temp/youtube', filename=def_filename)
    #     thumb_file_path = f'download_services/temp/youtube/{def_filename.replace("mp4", "jpg")}'
    #     resolution = int(highest_res_video.resolution.replace('p', ''))
    # except AgeRestrictedError:
    #     def_filename = make_valid_filename(youtube_obj.title)
    #     os.system(f'yt-dlp {youtube_url} -o download_services/temp/youtube/{def_filename}.webm')
    #     def_filename = def_filename+'.webm'
    #     thumb_file_path = f'download_services/temp/youtube/{def_filename.replace("webm", "jpg")}'
    #     resolution = 720

    def_filename = f'{str(message_chat_id)}_{str(int(time.time()))}'
    thumb_file_path = f'download_services/temp/youtube/{def_filename}_thumb.jpg'
    os.system(f'yt-dlp {youtube_url} -o "download_services/temp/youtube/{def_filename}.%(ext)s"')
    def_filename = glob.glob(f'download_services/temp/youtube/{def_filename}*')[0]
    resolution = 720

    r = requests.get(thumb_url)
    with open(thumb_file_path, 'wb') as f:
        f.write(r.content)


    return def_filename, thumb_file_path, resolution
