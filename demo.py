# 功能已初步实现，考虑可拆分代码为不同文件
# 命名略混乱，考虑重新命名
# 注释不规范

from nltk.corpus import wordnet as wn

import itertools
import os
import re
import requests

import http.client
import hashlib
import urllib
import random
import json


ORIGENAL_DICTIONARY = '英文字典.txt'
TARGET_DICTIONARY = '中文字典test.txt'
URL_TRANSLATE_API = 'http://fanyi.youdao.com/openapi.do?keyfrom=neverland&key=969918857&type=data&doctype=json&version=1.1&q='

# TESTLIST = ['EARLY', 'ELECTIONS']

targetFile = []

# 写文件


def writeFile():
    global targetFile

    with open(TARGET_DICTIONARY, 'w') as f:
        f.writelines(targetFile)
        f.close()

# 判断是否已存在于本块的翻译内

def ifInBlockRes(item, resList):
    for line in resList:
        if item in line:
            return True
    return False

# 翻译


def translateFile():
    global targetFile

    if not os.path.exists(ORIGENAL_DICTIONARY):
        print('File does not exist!')
        return

    with open(ORIGENAL_DICTIONARY) as f:
        while(True):
        # for block in range(0, 3):

            blockMeaning = ''
            # 记录块结果，减少去重所需时间
            res = []  
            wrongList = []

            while(True):
                line = f.readline()
                cameoCode = str(re.findall(r"\[(.+?)\]", line))

                # 跳过含有明显介词的行
                if '(' in line:
                    continue

                # 块开头
                elif line.startswith('---'):
                    segs = line.split()
                    blockMeaning = segs[1]
                    # block_code = segs[2]
                    res.append(line)

                # +开头的词组使用翻译API
                elif line.startswith('+'):
                    tempLine = re.compile('\{.*?\}').sub('', line)
                    words = tempLine[1:].split()[0]  # 提取词组
                    tempWordList = translateByAPI(words)

                    for temp in tempWordList:
                        # 跳过明显偏离
                        if temp in wrongList:
                            continue
                        # 跳过已含有的词汇，除非本行存在cameo编号
                        if ifInBlockRes(temp, res) and cameoCode == '[]':
                            continue

                        judgeResult = judge(blockMeaning, 'v. '+words.replace('_',' '), cameoCode, temp)
                        if(judgeResult == 'y'):
                            res.append(tempLine.replace(words, temp))
                        elif(judgeResult == 'n'):
                            wrongList.append(temp)
                        # else:
                        #     res.append(line)

                # 名词搭配
                elif line.startswith('-'):
                    # 去掉不必要的符号
                    word = line[1:].split("#")[0].split(
                        '[')[0].replace('*', '')  
                    # 消除开头空格，判断单词个数
                    words = word.replace('&', '').replace(
                        "}", "").replace("{", "").split()
                    originWords=' '.join(words)
                    # words=TESTLIST
                    wordList = []
                    # index = 0
                    # for singleWord in words:
                    #     wordList.append([])
                    #     for synset in wn.synsets(singleWord, lang='eng'):
                    #         for lemma in synset.lemma_names('cmn'):
                    #             # wordnet中对形容词翻译含有该符号，清除,如“前面+的”
                    #             lemma = lemma.replace('+', '')
                    #             wordList[index].append(lemma)
                    #     wordList[index] = list(set(wordList[index]))  # 去除重复项
                    #     index += 1

                    # # 笛卡尔积，对词组中每个词的翻译结果进行组合
                    # # 准确率低，考虑删去中
                    # for item in itertools.product(*wordLists):
                    #     translatedWords = ''
                    #     # 删去英文字典中取同义词集的符号
                    #     temp = line.replace('&', '')
                    #     # 按顺序分别替换对应单词
                    #     for i in range(0, len(words)):
                    #         translatedWords = translatedWords+item[i]
                    #         temp = temp.replace(words[i], item[i])

                    #     # print(temp)
                    #     # 跳过明显偏离
                    #     if translatedWords in wrongList:
                    #         continue
                    #     # 跳过已含有的词汇，除非本行存在cameo编号
                    #     if ifInBlockRes(translatedWords, res) and cameoCode == '[]':
                    #         continue

                    #     judgeResult = judge(
                    #         blockMeaning, 'n. '+originWords, cameoCode, translatedWords)
                    #     if(judgeResult == 'y'):
                    #         res.append(temp)
                    #     elif(judgeResult == 'n'):
                    #         wrongList.append(translatedWords)

                    if len(words)==1:
                        isFound=False # 判断单词是否能被找到
                        for synset in wn.synsets(words[0], lang='eng'):
                            for lemma in synset.lemma_names('cmn'):
                                isFound=True
                                # wordnet中对形容词翻译含有该符号，如“前面+的”
                                # 此处应全部为动词，不存在形容词，故遇到形容词跳过
                                if '+' in lemma:
                                    continue
                                # 比较相似度，去除差距明显过大词汇，但阈值未严格测试
                                if(sim(blockMeaning, lemma) < 0.2):
                                    continue
                                wordList.append(lemma)
                        if isFound:
                            wordList = list(set(wordList))  # 去重
                        else:
                            wordList = translateByAPI(words[0])

                        for result in wordList:
                            judgeResult = judge(blockMeaning, 'n. '+originWords,
                                                cameoCode, result)
                            if(judgeResult == 'y'):
                                temp = line.replace('&', '').replace(
                                    originWords, result)
                                # for i in range(1, len(words)):
                                #     temp = temp.replace(words[i], '')
                                res.append(temp)
                            elif(judgeResult == 'n'):
                                wrongList.append(result)
                            # else:
                            #     res.append(line)

                    else:

                        # 使用API翻译直接翻译词组
                        translatedWordList = translateByAPI(originWords)

                        for translatedWords in translatedWordList:
                            # 跳过明显偏离
                            if translatedWords in wrongList:
                                continue
                            # 跳过已含有的词汇 Cameo是否再判断一次？
                            if ifInBlockRes(translatedWords, res):
                                continue
                            judgeResult = judge(blockMeaning, 'n. '+originWords,
                                                cameoCode, translatedWords)
                            if(judgeResult == 'y'):
                                temp = line.replace('&', '').replace(
                                    originWords, translatedWords)
                                # for i in range(1, len(words)):
                                #     temp = temp.replace(words[i], '')
                                res.append(temp)
                            elif(judgeResult == 'n'):
                                wrongList.append(translatedWords)
                            # else:
                            #     res.append(line)

                # 空行
                elif line == '\n':
                    res.append(line)  # 加入以得到合适的带有空行的翻译文件

                # 开头无任何特殊标记
                else:
                    # 中文无时态区别。若不去除将影响replace结果
                    line = re.compile('\{.*?\}').sub('', line)
                    # 去除不必要的内容，仅留下动词。
                    verb = line.split('#')[0].split('[')[0]
                    # 存在结尾出现空格或换行符的情况
                    verb = verb.replace('\n', '').replace(' ', '')
                    
                    wordList = []

                    isFound=False # 判断单词是否能被找到
                    for synset in wn.synsets(verb, lang='eng'):
                        for lemma in synset.lemma_names('cmn'):
                            isFound=True
                            # wordnet中对形容词翻译含有该符号，如“前面+的”
                            # 此处应全部为动词，不存在形容词，故遇到形容词跳过
                            if '+' in lemma:
                                continue
                            # 比较相似度，去除差距明显过大词汇，但阈值未严格测试
                            if(sim(blockMeaning, lemma) < 0.2):
                                continue
                            wordList.append(lemma)
                    if isFound:
                        wordList = list(set(wordList))  # 去重
                    else:
                        wordList = translateByAPI(verb)

                    for word in wordList:
                        # 跳过明显偏离
                        if word in wrongList:
                            continue
                        # 跳过已含有的词汇，除非本行存在cameo编号
                        if ifInBlockRes(word, res) and cameoCode == '[]':
                            continue

                        judgeResult = judge(
                            blockMeaning, 'v. '+verb, cameoCode, word)
                        if(judgeResult == 'y'):
                            res.append(line.replace(verb, word))
                        elif(judgeResult == 'n'):
                            wrongList.append(word)
                        # else:
                        #     res.append(line)

                if line == '\n':  # 块结尾，退出循环
                    break
            targetFile = targetFile+res

            if line == '':  # 文件结尾，退出循环
                break

        f.close()

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

# 人工检查翻译是否正确


def judge(blockMeaning, originWords, cameoCode, translatedWords):
    return 'y'
    print('原始分类: '+blockMeaning,
          '原始字典: '+originWords,
          'Cameo代码: '+cameoCode,
          '翻译结果: '+translatedWords,
          ' ',
          sep='\n')
    print('翻译结果符合\"分类\"请输入”y“;',
          '翻译结果与\"分类\"明显不符请输入“n”;',
        #   '本词暂不翻译请输入“c:',
          sep='\n')
    while(1):
        ans = input()
        if(ans == 'y' or ans == 'Y'):
            return 'y'
        elif(ans == 'n' or ans == 'N'):
            return 'n'
        # elif(ans == 'c' or ans == 'C'):
        #     return 'c'
        else:
            print('无法识别您的输入，请重新输入: ')


# 主要用于测试某单词或词组的翻译结果


def test():
    res=[]
    for synset in wn.synsets('slaughter', lang='eng'):
        print(synset)
        for lemma in synset.lemma_names('cmn'):
            print(lemma)
            res.append(lemma)

    res = list(set(res))
    print(res)

# 相似度

def sim(word_1, word_2):
    score = -1
    wordList_1 = wn.synsets(word_1, lang='eng')
    wordList_2 = wn.synsets(word_2, lang='cmn')
    for word1 in wordList_1:
        for word2 in wordList_2:
            try:
                tempScore = word1.path_similarity(word2)
                if tempScore > score:
                    score = tempScore
            except:
                continue
    # print(score)
    return score


if __name__ == "__main__":
    # test()
    # baiduTranslate('angered_by')
    # sim('computer','算盘')
    # youdaoTranslate('relief_assistance')
    translateFile()
    writeFile()



