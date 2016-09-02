# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib
from flask import *
import json
import requests
from ua_parser import user_agent_parser
import xmltodict

application = app = Flask(__name__)

@app.before_request
def before_request():
    headers = request.headers
    print(headers)
    if 'Python' in headers.get('User-Agent'):
        return '自己去虾米抓数据 http://www.xiami.com/app/iphone/song/id/123 123换成ID'
    if 'curl' in headers.get('User-Agent'):
        return '自己去虾米抓数据 http://www.xiami.com/app/iphone/song/id/123 123换成ID'
    if 'wget' in headers.get('User-Agent'):
        return '自己去虾米抓数据 http://www.xiami.com/app/iphone/song/id/123 123换成ID'

@app.route('/')
def index():
    return redirect('http://answ.me/', code=301)

@app.route('/xiami/<id>.mp3')
def xiami(id):
    headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
    'Referer':'http://www.xiami.com/song/playlist/id/' + id
    }
    url = 'http://www.xiami.com/song/playlist/id/' + id
    try:
        r = requests.get(url,headers=headers)
        r.encode='uft-8'
    except:
        return '连接虾米服务器失败'
    try:
        info = xmltodict.parse(r.text)
        #print r.text
        songurl=info['playlist']['trackList']['track']['location']
    except:
        return '获取歌词信息失败，请检查是否有该歌曲ID'
    songurl=xiamidecode(songurl)
    return redirect(songurl, code=303)


@app.route('/xiami/json/<id>.mp3')
def xiami_json(id):
    headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
    'Referer':'http://www.xiami.com/song/playlist/id/' + id
    }
    url = 'http://www.xiami.com/song/playlist/id/' + id
    try:
        r = requests.get(url,headers=headers)
        r.encode='uft-8'
    except:
        return jsonify(
            success='False',
            log='连接虾米服务器失败'
        )
    try:
        info = xmltodict.parse(r.text)
        #print r.text
        songurl=info['playlist']['trackList']['track']['location']
    except:
        return jsonify(
            success='False',
            log='获取歌词信息失败，请检查是否有该歌曲ID'
        )
    songurl=xiamidecode(songurl)
    return jsonify(
        success='True',
        song_url=songurl
    )


def xiamidecode(location):
    num = int(location[0])
    avg_len, remainder = int(len(location[1:]) / num), int(len(location[1:]) % num)
    result = [location[i * (avg_len + 1) + 1: (i + 1) * (avg_len + 1) + 1] for i in range(remainder)]
    result.extend([location[(avg_len + 1) * remainder:][i * avg_len + 1: (i + 1) * avg_len + 1] for i in range(num-remainder)])
    url = urllib.unquote(''.join([''.join([result[j][i] for j in range(num)]) for i in range(avg_len)]) + \
                        ''.join([result[r][-1] for r in range(remainder)])).replace('^','0')
    return url

@app.route('/xiamiplayer/<id>')
def xiamiplayer(id):
    ua = user_agent_parser.Parse(request.headers.get('User-Agent'))
    try:
        version = int(ua['user_agent'].get('major'))
    except:
        version = 9
    if ua['user_agent'].get('family') == 'IE' and version < 9:
        flashurl = 'http://www.xiami.com/res/app/img/swf/weibo.swf?dataUrl=http://www.xiami.com/app/player/song/id/{0}/type/7/uid/0'.format(id)
        return redirect(flashurl, code=303)
    headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
    'Referer':'http://www.xiami.com/song/playlist/id/' + id
    }
    url = 'http://www.xiami.com/song/playlist/id/' + id
    try:
        r = requests.get(url,headers=headers)
        r.encode='uft-8'
    except:
        return '连接虾米服务器失败'
    try:
        info = xmltodict.parse(r.text)
        #print r.text
        songurl=info['playlist']['trackList']['track'].get('location')
        songurl=xiamidecode(songurl)
        songpic = info['playlist']['trackList']['track'].get('album_pic').replace('.jpg','_2.jpg')
        title = info['playlist']['trackList']['track'].get('title')
        singer = info['playlist']['trackList']['track'].get('artist')
        lyricurl = info['playlist']['trackList']['track'].get('lyric')
    except:
        return '获取歌词信息失败，请检查是否有该歌曲ID'
    try:
        lyric = requests.get(lyricurl,headers=headers)
        #print r.text
        if '[' not in lyric:
            lyric = "[00:00.00]" + title        
        lyric = lyric.replace('''\'''',''' \\\' ''').replace('\n','#').replace('\r','').replace('######','#').replace('######','#').replace('####','#').replace('###','#').replace('##','#')
    except:
        lyric = "[00:00.00]" + title
    return render_template('xiamiplayer.html',songurl=songurl,songpic=songpic,title=title,singer=singer,lyric=lyric,id=id)

@app.route('/m163/<id>.mp3')
def m163(id):
    headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    }
    url = 'http://music.163.com/api/song/detail?ids=[' + id + ']'
    try:
        #print url
        r = requests.get(url,headers=headers)
        #print r.text
    except:
        return '连接网易音乐服务器失败'
    try:
        info = xmltodict.parse(r.text)
        info = r.json()
    except:
        return '获取歌词信息失败，请检查是否有该歌曲ID'
    songurl=info['songs'][0].get('mp3Url','http://answ.me').replace('http://m','http://p')
    return redirect(songurl, code=303)

@app.route('/m163player/<id>')
def m163player(id):
    headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    }
    url = 'http://music.163.com/api/song/detail?ids=[' + id + ']'
    try:
        #print url
        r = requests.get(url,headers=headers)
        #print r.text
    except:
        return '连接网易音乐服务器失败'
    try:
            info = r.json()
            songurl=info['songs'][0].get('mp3Url','http://answ.me').replace('http://m','http://p')
            songpic = info['songs'][0]['album'].get('picUrl','http://answ.me')
            title = info['songs'][0].get('name','歌曲名称')
            singer = info['songs'][0]['artists'][0].get('name','演唱者')
            singerid = info['songs'][0]['artists'][0].get('id','1')
    except:
        return '获取歌词信息失败，请检查是否有该歌曲ID'
    lyricurl = 'http://music.163.com/api/song/media?id=' + id
    ua = user_agent_parser.Parse(request.headers.get('User-Agent'))
    try:
        version = int(ua['user_agent'].get('major'))
    except:
        version = 9
    if ua['user_agent'].get('family') == 'IE' and version < 9:
        singer = urllib.quote(singer.encode('utf-8'))
        title = urllib.quote(title.encode('utf-8'))
        flashurl = 'http://ting.weibo.com/public/swf/cardPlayer2.swf?v=1129&singer={0}&song={1}&songurl={2}&logo=http://p1.music.126.net/Acw7AiuWncQS3PkxrmkJXA==/5828511138862377.jpg&source=%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90&slink=http%3A%2F%2Fmusic.163.com/&autoPlay=false&target_url=http%3A%2F%2Fmusic.163.com%2Fsong%3Fid%3D{3}&image={4}%3Fparam%3D150y150&artists_uid=http%3A%2F%2Fmusic.163.com%2Fartist%3Fid%3D{5}'.format(singer,title,songurl,id,songpic,singerid)
        return redirect(flashurl, code=303)
    try:
        r = requests.get(lyricurl,headers=headers)
        lyric = r.json()['lyric']
        #print lyric
        if '[' not in lyric:
            lyric = "[00:00.00]" + title
        lyric = lyric.replace('''\'''',''' \\\' ''').replace('\n','#').replace('\r','').replace('######','#').replace('######','#').replace('####','#').replace('###','#').replace('##','#')
    except:
        lyric = "[00:00.00]" + title
    return render_template('m163player.html',songurl=songurl,songpic=songpic,title=title,singer=singer,lyric=lyric,id=id,singerid=singerid)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
