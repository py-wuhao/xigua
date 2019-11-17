"""
author: wuaho
email: 15392746632@qq.com
data:2019-11-14
"""
import base64
import json
import os
import random
import re
import time
import urllib.parse
import zlib

import requests
from faker import Faker
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class VideoParse:
    """
    西瓜视频解析
    """

    def __init__(self):
        self._faker = Faker()

    def _get_url(self, url: str) -> str:
        headers = {
            'User-Agent': self._faker.user_agent(),
        }
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.text
        return ''

    def get_video_id(self, url: str) -> str:
        content = self._get_url(url)
        video_id = re.findall(r'"vid":"([\w\d]+)"', content)
        return video_id[0] if video_id else ''

    @staticmethod
    def get_main_url(video_id: str) -> str:
        r = ''.join(random.choices('0123456789', k=16))
        url = "/video/urls/v/1/toutiao/mp4/" + video_id + "?r=" + r
        s = str(zlib.crc32(url.encode()))
        url = "https://ib.365yg.com" + url + '&s=' + s
        return url

    def get_video_url(self, source_url, try_num=3):
        video_id = self.get_video_id(source_url)
        url = self.get_main_url(video_id)
        content = self._get_url(url)
        content_dict = json.loads(content)
        if content_dict.get('code') != 0:
            if try_num > 0:
                time.sleep(2)
                return self.get_video_url(source_url, try_num - 1)
            else:
                print(content_dict.get('message'))
                return ''
        else:
            main_url = content_dict['data']['video_list']['video_1']['main_url']
            video_url = base64.b64decode(main_url).decode()
            return video_url


def download_file(name, url):
    print('开始下载')
    headers = {'Proxy-Connection': 'keep-alive'}
    r = requests.get(url, stream=True, headers=headers)
    length = float(r.headers['content-length'])
    with open(name, 'wb') as f:
        count = 0
        count_tmp = 0
        last_time = time.time()
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - last_time > 2:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count
                    print('{}下载{:.2f}%---{:.2f}M/s'.format(name, p, speed))
                    last_time = time.time()
        print('下载完成')


if __name__ == '__main__':
    print('直接回车测试 https://www.ixigua.com/i6704446868685849092')
    source_url = input('输入西瓜链接：')
    if not source_url:
        source_url = 'https://www.ixigua.com/i6704446868685849092'
    video_name = urllib.parse.urlparse(source_url).path.strip('/') + '.mp4'

    video_parse = VideoParse()
    print('开始解析')
    video_url = video_parse.get_video_url(source_url)
    print(video_url)
    download_file(video_name, video_url)
    # os.system('pause')
