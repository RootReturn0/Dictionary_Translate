from nltk.corpus import wordnet as wn

import itertools
import os
import re

ORIGENAL_DICTIONARY = '英文字典.txt'
TARGET_DICTIONARY = '中文字典.txt'

# TESTLIST = ['EARLY', 'ELECTIONS']

res = []

# 写文件
def writeFile():
    global res
    
    with open(TARGET_DICTIONARY, 'w') as f:
        f.writelines(res)
        f.close()

# 翻译
def translateFile():
    global res

    if not os.path.exists(ORIGENAL_DICTIONARY):
        print('File does not exist!')
        return

    with open(ORIGENAL_DICTIONARY) as f:
        while(True):
            line = f.readline()

            # 跳过含有明显介词的行
            if '(' in line:
                continue

            # +开头的词组暂时无法得到好的解决方案，考虑翻译API
            # 该功能确定思路后完善容易，先暂时略过
            elif line.startswith('+'):
                continue

            # 块开头
            elif line.startswith('---'):
                # print(content)
                segs = line.split()
                # block_meaning = segs[1]
                # block_code = segs[2]
                # print(segs,block_code,block_meaning)
                res.append(line)

            # 名词搭配
            elif line.startswith('-'):
                word = line[1:].split("#")[0].split(
                    '[')[0].replace('*', '')  # 去掉不必要的符号
                words = word.replace('&', '').replace(
                    "}", "").replace("{", "").split()
                # words=TESTLIST
                wordLists = []
                index = 0
                for singleWord in words:
                    wordLists.append([])
                    for synset in wn.synsets(singleWord, lang='eng'):
                        for lemma in synset.lemma_names('cmn'):
                            # wordnet中对形容词翻译含有该符号，清除,如“前面+的”
                            lemma = lemma.replace('+', '')
                            wordLists[index].append(lemma)
                    wordLists[index] = list(set(wordLists[index]))  # 去除重复项
                    # print(wordLists[index])
                    index += 1
                # 笛卡尔积，对词组中每个词的翻译结果进行组合
                for item in itertools.product(*wordLists):
                    temp = line
                    # print(temp,words)
                    for i in range(0, len(words)):
                        temp = temp.replace(words[i], item[i])

                    # print(temp)
                    res.append(temp)

            # 空行
            elif line == '\n':
                res.append(line)  # 加入以得到合适的带有空行的翻译文件

            # 开头无任何特殊标记
            else:
                # 中文无时态区别。若不去除将影响replace结果
                line = re.compile('\{.*?\}').sub('', line)
                # 去除不必要的内容，仅留下动词。
                verb = line.split('#')[0].split('[')[0]
                if 'BUTCHER' in line or 'MASSACRE' in line or 'SLAUGHTER' in line:
                    print('1st',verb,'@')
                # 存在结尾出现空格或换行符的情况
                verb = verb.replace('\n', '').replace(' ', '')
                if 'BUTCHER' in line or 'MASSACRE' in line or 'SLAUGHTER' in line:
                    print('2nd',verb,'@')
                # print(verb)
                # print('verb:',verb)
                wordList = []
                for synset in wn.synsets(verb, lang='eng'):
                    for lemma in synset.lemma_names('cmn'):
                        # wordnet中对形容词翻译含有该符号，如“前面+的”
                        # 此处应全部为动词，不存在形容词，故遇到形容词跳过
                        if '+' in lemma:
                            continue
                        wordList.append(lemma)
                wordList = list(set(wordList))  # 去重
                for word in wordList:
                    res.append(line.replace(verb, word))
                # print(verb)

            if line == '':  # 文件结尾，退出循环，使用'\n'则为块结尾
                break

        f.close()

# 主要用于测试某单词或词组的翻译结果
def test():
    global res
    for synset in wn.synsets('slaughter', lang='eng'):
        print(synset)
        for lemma in synset.lemma_names('cmn'):
            print(lemma)
            res.append(lemma)

    res = list(set(res))
    print(res)


if __name__ == "__main__":
    test()
    # translateFile()
    # writeFile()
