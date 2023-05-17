import datetime
import os
import time
import traceback

from data.config import PINTEREST_PROXY_LIST
from loader import root_logger
from utils.wrappers import async_wrap
import json
import requests
from bs4 import BeautifulSoup as bs

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36'


def get_media(url):
    if '/sent/' in url:
        url = url.split('/sent/')[0]
    for retry in range(5):
        try:
            proxy = 'http://' + next(PINTEREST_PROXY_LIST)
            proxies = {'http': proxy, 'https': proxy}
            r = requests.get(url, headers={'User-Agent': UA}, proxies=proxies, timeout=10, allow_redirects=True)
            print(r.url)
            pin_id = r.url.split('/pin/')[1].split('/')[0]
            break
        except IndexError:
            traceback.print_exc()
            pass

    if not pin_id:
        return None

    if '/pin/' not in url:
        r = requests.get(f'https://www.pinterest.com/pin/{pin_id}', headers={'User-Agent': UA}, proxies=proxies,
                         timeout=10, allow_redirects=True)

    soup = bs(r.text, 'html.parser')

    data_json = json.loads(soup.find('script', id="__PWS_DATA__").text)
    # print(data_json)

    title = data_json['props']['initialReduxState']['pins'][pin_id]['grid_title'].strip()
    description = data_json['props']['initialReduxState']['pins'][pin_id]['closeup_unified_description'].strip()
    pin_content = {'title': title, 'description': description, 'media': []}
    story_pin_data = data_json['props']['initialReduxState']['pins'][pin_id]['story_pin_data']
    if story_pin_data:
        for page in story_pin_data['pages']:
            # print(page)
            try:
                video_block = page['blocks'][0]['video']
            except KeyError:
                video_block = None
            if video_block:
                pin_content['media'].append(
                    {'image_url': None, 'video_url': video_block['video_list']['V_EXP7']['url']})
            else:
                pin_content['media'].append(
                    {'image_url': page['blocks'][0]['image']['images']['originals']['url'], 'video_url': None})

        return pin_content
    else:
        try:
            image_url = data_json['props']['initialReduxState']['pins'][pin_id]['images']['orig']['url']
        except TypeError:
            image_url = None
        try:
            video_url = data_json['props']['initialReduxState']['pins'][pin_id]['videos']['video_list']['V_720P']['url']
        except TypeError:
            try:
                video_url = \
                    data_json['props']['initialReduxState']['pins'][pin_id]['story_pin_data']['pages'][0]['blocks'][0][
                        'video'][
                        'video_list']['V_EXP7']['url']
            except TypeError:
                video_url = None
        pin_content['media'].append({'image_url': image_url, 'video_url': video_url})
        return pin_content


@async_wrap
def get_pin_content(url):
    for retry in range(5):
        try:
            result = get_media(url)
            return result
        except KeyError:
            continue
        except:
            root_logger.error('Pinterest error' + url)
            root_logger.error('Pinterest error', exc_info=True)
    else:
        return None


@async_wrap
def save_video(url, user_id):
    r = requests.get(url)
    file_path = f"download_services/temp/pinterest/{str(user_id)}_{str(int(time.time()))}.mp4"
    with open(file_path, 'wb') as f:
        f.write(r.content)
    return file_path


@async_wrap
def get_pin_file(url):
    r = requests.get(url)
    return r.content
