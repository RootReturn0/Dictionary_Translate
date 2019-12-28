from nltk.corpus import wordnet as wn

import itertools
import os
import re

from translateAPI import translateByAPI
from judge import judge

import threading
import time
# import rest_server
import var

ORIGENAL_DICTIONARY = '英文字典.txt'
TARGET_DICTIONARY = '中文字典test.txt'
COUNT_DICTIONARY = 'count.txt'

# TESTLIST = ['EARLY', 'ELECTIONS']



# 写文件


def writeFile(translatedRes):
    var.category=''
    if not var.save:
        print('File is not saved!')
        return
    # with open(COUNT_DICTIONARY, 'w') as f:
    #     f.write(block+' '+str(count))
    #     f.close()
    dictionary=[]
    with open(TARGET_DICTIONARY, 'r') as f: # w+不好使！！于是用了r+w
        dictionary=f.readlines()
    print(dictionary)
    with open(TARGET_DICTIONARY, 'w') as f:
        lineNum = 0
        for res in translatedRes:
            # 不论类别，字典均顺序提取翻译，若该块不存在字典中，则该块下所有翻译均为新增，顺序加入即可
            # 不存在当然加入，若存在则跳过表明类别的行
            isExist = False
            for index, line in enumerate(dictionary):
                if res['category'] == line:
                    isExist = True
                    lineNum = index + 1 # 即将被插入的地方
                    break
            if not isExist:
                dictionary.append('\n') # 换行，分隔块
                dictionary.append(res['category'])
                dictionary.append(res['content'])
            else:
                if not res['content'].startswith('-'): # 如果不是名词
                    dictionary.insert(lineNum,res['content'])
                    # print('1',dictionary,'\n')
                else:
                    while(not dictionary[lineNum].startswith('-') and dictionary[lineNum] != '\n'):
                        lineNum=lineNum+1
                    dictionary.insert(lineNum,res['content'])
                    # print('2',dictionary,'\n')

        f.writelines(dictionary)
        # f.close()
    print('Files saved!')

# 判断是否已存在于本块的翻译内


def ifInBlockRes(item, resList):
    for line in resList:
        if item in line:
            return True
    return False

# 翻译


def translateFile():
    translatedRes = []

    if not os.path.exists(ORIGENAL_DICTIONARY):
        print('File does not exist!')
        return

    count = -1  # count lines

    with open(ORIGENAL_DICTIONARY) as f:
        print('called')
        # while(var.loading):
        #     print('loading')
        while(True):
            # for block in range(0, 3):

            blockMeaning = ''
            blockLine = ''
            isAll = False # 判断是否整块属于类使用
            # 记录块结果，减少去重所需时间
            res = []
            wrongList = []

            # 暂存以翻译内容使用，按类别翻译后不需要
            # try:
            #     with open(COUNT_DICTIONARY) as cf:
            #         content = cf.readline().split(' ')
            #         blockMeaning = content[0]
            #         count = int(content[1])
            #         for i in range(0, count):
            #             f.readline()
            # except:
            #     print('No counting record')

            while(True):
                if var.end:
                    break
                line = f.readline()
                # if (line.split('[')[-1].split(']')[0]=='022'):
                #     print(line.split('[')[-1].split(']')[0].startswith(var.category))
                #     time.sleep(100)
                count=count+1
                print(count,var.end,line.split('[')[-1].split(']')[0])
                if line.startswith('---'):
                    isAll = False # 重置标志
                    segs = line.split()
                    blockMeaning = segs[1]
                    if segs[2].replace('[','').startswith(var.category):
                        isAll = True
                    blockLine = line
                if (not isAll) and (not line.split('[')[-1].split(']')[0].startswith(var.category)):
                    continue
                comment = '' if len(line.split('#')) ==1 else line.split('#')[-1]
                # print(line)
                cameoCode = str(re.findall(r"\[(.+?)\]", line))
                cameoCode = cameoCode.replace('\'','').replace('[','').replace(']','')

                if line.startswith('---'):
                    continue
                # 跳过含有明显介词的行
                elif '(' in line:
                    continue

                # +开头的词组使用翻译API
                elif line.startswith('+'):
                    tempLine = re.compile('\{.*?\}').sub('', line)
                    words = tempLine[1:].split()[0]  # 提取词组
                    tempWordList = translateByAPI(words)

                    tempJudgeList = []
                    for tempTransRes in tempWordList:
                        # 跳过明显偏离
                        if tempTransRes in wrongList:
                            continue
                        # 跳过已含有的词汇
                        if ifInBlockRes(tempTransRes, res):
                            continue

                        tempJudgeList.append({
                            'class': blockMeaning,
                            'origin': 'v. '+words.replace('_', ' '),
                            'code': cameoCode,
                            'Chinese': tempTransRes,
                            'comment': comment
                        })
                    print(tempJudgeList, '111')
                    returnRes = judge(tempJudgeList)

                    for item in tempJudgeList:
                        if item in returnRes:
                            res.append({'category':blockLine,'content':tempLine.replace(
                                words.replace('_', ' '), item['Chinese'])})
                        else:
                            wrongList.append(item['Chinese'])

                # 名词搭配
                elif line.startswith('-'):
                    # 去掉不必要的符号
                    word = line[1:].split("#")[0].split(
                        '[')[0].replace('*', '')
                    # 消除开头空格，判断单词个数
                    words = word.replace('&', '').replace(
                        "}", "").replace("{", "").split()
                    originWords = ' '.join(words)
                    wordList = []

                    if len(words) == 1:
                        isFound = False  # 判断单词是否能被找到
                        for synset in wn.synsets(words[0], lang='eng'):
                            print(wn.synsets(words[0], lang='eng'))
                            print(synset.lemma_names('cmn'))
                            for lemma in synset.lemma_names('cmn'):
                                isFound = True
                                # wordnet中对形容词翻译含有该符号，如“前面+的”
                                # 此处应全部为动词，不存在形容词，故遇到形容词跳过
                                if '+' in lemma:
                                    continue
                                # 比较相似度，去除差距明显过大词汇，但阈值未严格测试
                                if(sim(blockMeaning, lemma) < 0.14):
                                    print('uunlike ',lemma,blockMeaning,sim(blockMeaning, lemma))
                                    continue
                                wordList.append(lemma)
                        if isFound:
                            wordList = list(set(wordList))  # 去重
                            if not wordList: #可能全被过滤了
                                wordList = translateByAPI(words[0])
                            print('isFound')
                        else:
                            print('not founnd')
                            wordList = translateByAPI(words[0])
                        print(wordList)
                        tempJudgeList = []
                        for tempTransRes in wordList:
                            tempJudgeList.append({
                                'class': blockMeaning,
                                'origin': 'n. '+originWords,
                                'code': cameoCode,
                                'Chinese': tempTransRes,
                                'comment': comment
                            })
                        print(tempJudgeList, '222')
                        returnRes = judge(tempJudgeList)

                        for item in tempJudgeList:
                            if item in returnRes:
                                res.append({'category':blockLine,'content':line.replace('&', '').replace(originWords, item['Chinese'])})
                            else:
                                wrongList.append(item['Chinese'])

                    else:

                        # 使用API翻译直接翻译词组
                        translatedWordList = translateByAPI(originWords)

                        tempJudgeList = []
                        for tempTransRes in translatedWordList:
                            # 跳过明显偏离
                            if tempTransRes in wrongList:
                                continue
                            # 跳过已含有的词汇
                            if ifInBlockRes(tempTransRes, res):
                                continue
                            tempJudgeList.append({
                                'class': blockMeaning,
                                'origin': 'n. '+originWords,
                                'code': cameoCode,
                                'Chinese': tempTransRes,
                                'comment': comment
                            })
                        print(tempJudgeList, '333')
                        returnRes = judge(tempJudgeList)

                        for item in tempJudgeList:
                            if item in returnRes:
                                res.append({'category':blockLine,'content':line.replace('&', '').replace(
                                    originWords, item['Chinese'])})
                            else:
                                wrongList.append(item['Chinese'])

                # 空行(分类翻译后不再需要)
                # elif line == '\n':
                #     res.append(line)  # 加入以得到合适的带有空行的翻译文件

                # 开头无任何特殊标记
                else:
                    # 中文无时态区别。若不去除将影响replace结果
                    line = re.compile('\{.*?\}').sub('', line)
                    # 去除不必要的内容，仅留下动词。
                    verb = line.split('#')[0].split('[')[0]
                    # 存在结尾出现空格或换行符的情况
                    verb = verb.replace('\n', '').replace(' ', '')

                    wordList = []

                    isFound = False  # 判断单词是否能被找到
                    for synset in wn.synsets(verb, lang='eng'):
                        for lemma in synset.lemma_names('cmn'):
                            print(blockMeaning, lemma)
                            isFound = True
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

                    tempJudgeList = []
                    for tempTransRes in wordList:
                        # 跳过明显偏离
                        if tempTransRes in wrongList:
                            continue
                        # 跳过已含有的词汇
                        if ifInBlockRes(tempTransRes, res):
                            continue

                        print(blockMeaning, verb, cameoCode, tempTransRes)
                        tempJudgeList.append({
                            'class': blockMeaning,
                            'origin': 'v. '+verb,
                            'code': cameoCode,
                            'Chinese': tempTransRes,
                            'comment': comment
                        })

                    print(wordList, tempJudgeList)
                    returnRes = judge(tempJudgeList)

                    for item in tempJudgeList:
                        if item in returnRes:
                            res.append({'category':blockLine,'content':line.replace(verb, item['Chinese'])})
                        else:
                            wrongList.append(item['Chinese'])

                if line == '\n':  # 块结尾，退出循环
                    break

                if var.end:
                    break
            translatedRes = translatedRes+res
            if var.end:
                print(translatedRes)
                writeFile(translatedRes)
                break
            print('jump?!')

            # if line == '':  # 文件结尾，退出循环
            #     writeFile(translatedRes)
            #     break

        f.close()


# 主要用于测试某单词或词组的翻译结果


def test():
    res = []
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
    # threading.Thread(target = rest_server.start, args =()).start()
    # threading.Thread(target=translateFile, args=()).start()
    # rest_server.start()
    # rest_server.start()
    translateFile()
    # writeFile()
