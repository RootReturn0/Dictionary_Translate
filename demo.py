# 功能已初步实现，考虑可拆分代码为不同文件
# 命名略混乱，考虑重新命名
# 注释不规范

from nltk.corpus import wordnet as wn

import itertools
import os
import re

from translateAPI import translateByAPI
from judge import judge

import threading
import rest_server

ORIGENAL_DICTIONARY = os.path.join(os.path.abspath(os.path.dirname(__file__)),'英文字典.txt')
TARGET_DICTIONARY = os.path.join(os.path.abspath(os.path.dirname(__file__)),'中文字典test.txt')
COUNT_DICTIONARY = os.path.join(os.path.abspath(os.path.dirname(__file__)),'count.txt')

# TESTLIST = ['EARLY', 'ELECTIONS']

targetFile = []


# 写文件


def writeFile(block, count):
    global targetFile

    with open(COUNT_DICTIONARY, 'w') as f:
        f.write(block+' '+str(count))
        f.close()

    with open(TARGET_DICTIONARY, 'a',encoding="utf-8") as f:
        print(targetFile)
        f.writelines(targetFile)
        f.close()
    print('Files saved!')

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

    count = -1  # count lines
    countNum = 0
    with open(ORIGENAL_DICTIONARY) as f:
        c=0
        while(rest_server.loading):
            print('loading')
        while(True):
            # for block in range(0, 3):

            blockMeaning = ''
            # 记录块结果，减少去重所需时间
            res = []
            wrongList = []

            fileSlice = ''
            if countNum is 0:
                countNum = 1+ countNum
                try:
                    with open(COUNT_DICTIONARY) as cf:
                        content = cf.readline().split(' ')
                        blockMeaning = content[0]
                        count = int(content[1])
                        for i in range(0, count):
                            f.readline()
                except:
                    print('No counting record')

            while(True):
                line = f.readline()
                comment = '' if len(line.split('#')) ==1 else line.split('#')[-1]
                # print(line)
                cameoCode = str(re.findall(r"\[(.+?)\]", line))
                cameoCode = cameoCode.replace('\'','').replace('[','').replace(']','')

                # 跳过含有明显介词的行
                if '(' in line:
                    continue

                # 块开头
                elif line.startswith('---'):
                    segs = line.split()
                    blockMeaning = segs[1]
                    print(segs, blockMeaning)
                    # block_code = segs[2]
                    res.append(line)

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
                            res.append(tempLine.replace(
                                words.replace('_', ' '), item['Chinese']))
                        else:
                            wrongList.append(item['Chinese'])
                        # judgeResult = judge(
                        #     blockMeaning, 'v. '+words.replace('_', ' '), cameoCode, temp)
                        # if(judgeResult == 'y'):
                        #     res.append(tempLine.replace(words, temp))
                        # elif(judgeResult == 'n'):
                        #     wrongList.append(temp)
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
                    originWords = ' '.join(words)
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

                    if len(words) == 1:
                        isFound = False  # 判断单词是否能被找到
                        for synset in wn.synsets(words[0], lang='eng'):
                            for lemma in synset.lemma_names('cmn'):
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
                            wordList = translateByAPI(words[0])

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
                                res.append(line.replace('&', '').replace(originWords, item['Chinese']))
                            else:
                                wrongList.append(item['Chinese'])
                            # judgeResult = judge(blockMeaning, 'n. '+originWords,
                            #                     cameoCode, result)
                            # if(judgeResult == 'y'):
                            #     temp = line.replace('&', '').replace(
                            #         originWords, result)
                            #     # for i in range(1, len(words)):
                            #     #     temp = temp.replace(words[i], '')
                            #     res.append(temp)
                            # elif(judgeResult == 'n'):
                            #     wrongList.append(result

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
                                res.append(line.replace('&', '').replace(
                                    originWords, item['Chinese']))
                            else:
                                wrongList.append(item['Chinese'])
                            # judgeResult = judge(blockMeaning, 'n. '+originWords,
                            #                     cameoCode, translatedWords)
                            # if(judgeResult == 'y'):
                            #     temp = line.replace('&', '').replace(
                            #         originWords, translatedWords)
                            #     # for i in range(1, len(words)):
                            #     #     temp = temp.replace(words[i], '')
                            #     res.append(temp)
                            # elif(judgeResult == 'n'):
                            #     wrongList.append(translatedWords)

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
                            res.append(line.replace(verb, item['Chinese']))
                        else:
                            wrongList.append(item['Chinese'])

                        # judgeResult = judge(
                        #     blockMeaning, 'v. '+verb, cameoCode, word)
                        # if(judgeResult == 'y'):
                        #     res.append(line.replace(verb, word))
                        # elif(judgeResult == 'n'):
                        #     wrongList.append(word)

                count += 1  # count lines read

                if line == '\n':  # 块结尾，退出循环
                    break

                if rest_server.end_signal():
                    break
            targetFile = targetFile+res
            print('jump?!')
            if rest_server.end_signal():

                writeFile(blockMeaning, count)
                break

            # if count>=20:
            #     break

            if line == '':  # 文件结尾，退出循环
                writeFile(blockMeaning, count)
                break

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
    threading.Thread(target=translateFile, args=()).start()
    rest_server.start()
    # rest_server.start()
    # translateFile()
    # writeFile()
