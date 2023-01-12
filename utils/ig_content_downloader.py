import asyncio
import os
import traceback
import requests
import instaloader
from instaloader import Post, TopSearchResults, QueryReturnedBadRequestException, TooManyRequestsException, \
    ConnectionException, LoginRequiredException, BadResponseException, BadResponseExceptionMeta
from operator import itemgetter

from accs.login_to_ig_accs import InstaLoaderObjProxy
from data import config
from data.config import DEVELOPER
from utils.wrappers import async_wrap
import loader



def get_proxy():
    pass


def change_proxy():
    for retry in range(10):
        try:
            requests.get(config.proxy_change_url,
                         headers={
                             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'},
                         timeout=10).json()
            break
        except Exception as e:
            print(e)


def change_operator():
    for retry in range(10):
        try:
            url = "https://mobileproxy.space/api.html?command=change_equipment&proxy_id=42807"
            payload = {}
            headers = {
                'Authorization': 'Bearer e16c7622e7d194e7a42eb24fc326ee9d',
                'Cookie': 'a=1a1748065d183e046ce9dccf04223fde; ft=1; lang=ru'
            }
            requests.request("GET", url, headers=headers, data=payload, timeout=30)
            loader.telebot.send_message(DEVELOPER[0], 'The operator was changed')
            break
        except:
            traceback.print_exc()
            pass


@async_wrap
def get_post_content(short_code):
    post = None
    for retry in range(15):
        try:
            io = InstaLoaderObjProxy
            post = Post.from_shortcode(io.context, short_code)
            config.changing_proxy = False
            config.failed_connection_attempts = 0
            break
        except BadResponseExceptionMeta:
            return 'error_link'
        except (QueryReturnedBadRequestException, LoginRequiredException, TooManyRequestsException,
                ConnectionException,BadResponseException):
            traceback.print_exc()
            config.failed_connection_attempts += 1
            print('config.failed_connection_attempts ' + str(config.failed_connection_attempts))
            print('Login required exception')
            if not config.changing_proxy:
                config.changing_proxy = True
                print('Changing proxy')
                change_proxy()
                config.changing_proxy = False
                asyncio.run(sleep_after_bad_connection())
            asyncio.run(sleep_after_bad_connection())
    # else:
    #     print('Posts 3 time retry error')
    #     loader.telebot.send_message(DEVELOPER[0], 'Posts 3 time retry error')
    #     post = get_post_reserve(short_code)

    if post:
        return post

    else:
        return 'error'


async def sleep_after_bad_connection():
    await asyncio.sleep(1)


@async_wrap
def get_hashtags(search_string):
    low_frequency_hashtags = []
    medium_frequency_hashtags = []
    high_frequency_hashtags = []

    def reformat_hashtag(hashtag):
        return f"#{hashtag[0]} - {str(hashtag[1] if hashtag[1] < 1000 else str(int(hashtag[1] / 1000)) + 'к')}"

    hashtags = []
    for retry in range(15):
        try:
            io = InstaLoaderObjProxy
            for hashtag in TopSearchResults(io.context,
                                            '#' + search_string.replace('#', ''))._node.get('hashtags', []):
                hashtag_data = (hashtag.get('hashtag', {}).get('name'), hashtag.get('hashtag', {}).get('media_count'))
                hashtags.append(hashtag_data)
                config.changing_proxy = False
            config.failed_connection_attempts = 0
            break
        except (
                QueryReturnedBadRequestException, LoginRequiredException, TooManyRequestsException,
                ConnectionException):

            config.failed_connection_attempts += 1
            print('config.failed_connection_attempts ' + str(config.failed_connection_attempts))

            print('Login required exception')
            if not config.changing_proxy:
                config.changing_proxy = True
                print('Changing proxy')
                change_proxy()
                config.changing_proxy = False
                asyncio.run(sleep_after_bad_connection())
            asyncio.run(sleep_after_bad_connection())



    # else:
    #     print('Hashtags 3 time retry error')
    #     loader.telebot.send_message(DEVELOPER[0], 'Hashtags 3 time retry error')
    #     hashtags = get_hashtags_reserve(search_string)

    if not hashtags:
        return None

    hashtags = sorted(hashtags, key=itemgetter(1))
    for hashtag in reversed(hashtags):
        if int(hashtag[1]) >= 500000:
            high_frequency_hashtags.append(reformat_hashtag(hashtag))
        elif 100000 <= int(hashtag[1]) < 500000:
            medium_frequency_hashtags.append(reformat_hashtag(hashtag))
        else:
            low_frequency_hashtags.append(reformat_hashtag(hashtag))

    result_hashtags = ""

    if high_frequency_hashtags:
        high_frequency_hashtags = "\n<b>Высокочастотные(от 500к публикаций):</b>\n" + "\n".join(
            high_frequency_hashtags)
        result_hashtags += high_frequency_hashtags
    if medium_frequency_hashtags:
        medium_frequency_hashtags = "\n\n<b>Среднечастотные(от 100к до 500к публикаций):</b>\n" + "\n".join(
            medium_frequency_hashtags)
        result_hashtags += medium_frequency_hashtags
    if low_frequency_hashtags:
        low_frequency_hashtags = "\n\n<b>Низкочастотные(до 100к публикаций):</b>\n" + "\n".join(
            low_frequency_hashtags)
        result_hashtags += low_frequency_hashtags

    result_hashtags = result_hashtags.strip()

    result_hashtags = "<b>Хэштеги и количество публикаций(частотность):</b>\n\n" + result_hashtags
    return result_hashtags


@async_wrap
def save_reel(short_code, url):
    r = requests.get(url)
    file_path = f"./utils/temp_reels/{short_code}.mp4"
    with open(file_path, 'wb') as f:
        f.write(r.content)
    return file_path


@async_wrap
def del_temp_reel(filepath):
    os.remove(filepath)


@async_wrap
def check_is_reel_huge(url):
    for retry in range(3):
        try:
            size = int(requests.get(url, stream=True, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'}).headers[
                           'Content-length'])
            if size > 50000000:
                return True
            else:
                return False
        except:
            traceback.print_exc()
            pass
