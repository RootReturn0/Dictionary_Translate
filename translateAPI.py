import requests
import http.client
import hashlib
import urllib
import random
import json

URL_TRANSLATE_API = 'http://fanyi.youdao.com/openapi.do?keyfrom=neverland&key=969918857&type=data&doctype=json&version=1.1&q='


def translateByAPI(word):
    word = word.replace('_',' ')
    res = youdaoTranslate(word)
    # print(res)
    try:
        tempBaiduRes = baiduTranslate(word)
        if tempBaiduRes not in res:
            res.append(tempBaiduRes)
        # print(res)
        return res
    except:
        print('e: ',str(res))
        return res


# Youdao API
def youdaoTranslate(word):
    r = requests.get(url=URL_TRANSLATE_API+word)
    res = r.json()
    try:
        returnedData=res['translation']
    except:
        return []
        print('YouDao ERROR! The word to be translated is '+word,'returned data: '+str(res))

    try:
        return returnedData+res['web'][0]['value']
    except:
        return []
        print('YouDao ERROR! The word to be translated is '+word,'returned data: '+str(res))

# BaiDu API
# 请求词组时形如“CALL OFF”或“CALL_OFF”均可
# 第一种格式更好


def baiduTranslate(word):
    # Google API（可用爬虫实现免费爬取翻译，这里为了代码简洁改用百度API）
    # requestData = [
    #     {
    #         'q': word,
    #         'target': 'zn'
    #     }
    # ]
    # r = requests.post(URL_GOOGLE_API+word)
    # print(r.content.decode('utf-8'))

    #百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
    # coding=utf-8

    appid = '20191022000343458'  # 填写你的appid
    secretKey = 'GS8G45OIguvyE4brZy4S'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'auto'  # 原文语种
    toLang = 'zh'  # 译文语种
    salt = random.randint(32768, 65536)
    q = word
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        # 返回结果示例
        # {'from': 'en',
        #  'to': 'zh',
        #  'trans_result': [
        #      {'src': 'apple',
        #       'dst': '苹果'}
        #  ]}

        # print(result['trans_result'][0]['dst'])
        return result['trans_result'][0]['dst']

    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


