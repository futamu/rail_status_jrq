# -*- coding:utf-8 -*-
import sys
import hashlib
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from requests_oauthlib import OAuth1Session

from key_shibu_rail import *

oath = OAuth1Session(consumer_key, consumer_secret, access_token, access_token_secret)


def get_data():
    infos = []
    url = "http://www.jrkyushu.co.jp/trains/unkou.php"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",}

    request = urllib.request.Request(url=url, headers=headers)
    html = urllib.request.urlopen(request)
    soup = BeautifulSoup(html, "html.parser")

    tds = soup.find_all("td")

    dic = {"<br>":"","<br/>":"","</br>":"","<td>":"","</td>":"","<td/>":""}

    del tds[len(tds)-1]

    for info in tds:
        info = str(info)
        for key, value in dic.items():
            info = info.replace(key, value)
        #if "td" not in info and "熊本地震" not in info and "平成29年九州北部豪雨" not in info and "大雨等の影響に伴う運転見合わせ" not in info:
        if "td" not in info:
            infos.append(info)

    return infos

def tweet1(status, id=None):
    url = "https://api.twitter.com/1.1/statuses/update.json"
    if id == None:
        params = {"status": status}
    else:
        params = {"status": status, "in_reply_to_status_id": id}

    res = oath.post(url, params = params)

    resj = res.json()
    s_id = resj["id_str"]

    return s_id

def tweet2(status, id=None):
    print(status)
    pass

def parse_info(infos):
    tag = "\n#運行状況\n#JR九州"
    txt = ""
    csv_hashs = []
    new_hashs = []
    if len(infos) != 0:
        with open("info.csv", "r", encoding="utf-8") as f:
            line = f.readline()
            while line:
                csv_hashs.append(line.replace("\n",""))
                line = f.readline()
            for info in infos:
                info_hash = hashlib.md5(info.encode("utf-8")).hexdigest()
                new_hashs.append(info_hash)
                if info_hash not in csv_hashs:
                    info = info.splitlines()
                    id = None
                    cnt = len(tag)
                    main = ""
                    tmp = ""
                    for line in info:
                        tmp = main[:-1]
                        main = main + line + "\n"
                        cnt = cnt + len(line)
                        if cnt > 140:
                            tmp = tmp + tag
                            id = tweet1(tmp, id)
                            main = "@shibuyarinn_810\n" + line
                            cnt = len(main + tag)
                    main = main + tag
                    tweet1(main, id)
        with open("info.csv", "w", encoding="utf-8") as f:
            f.write("\n".join(new_hashs))

if __name__ == "__main__":
    parse_info(get_data())
