# 提取cameo所有类别，初始化翻译状态
import json

ORIGENAL_DICTIONARY = '英文字典.txt'
CAMEO_CODE_FILE = './doc/CameoCode.json'
CAMEO_STATUS_FILE = './CameoStatus.json'

cameoList = []
dictionary = []

codeList = [{'cameo':'','num':0,'status':False}]

def readFile():
    with open(CAMEO_CODE_FILE, 'r') as f:
        global cameoList
        cameoList = json.load(f)
        f.close()
    with open(ORIGENAL_DICTIONARY, 'r') as f:
        global dictionary
        dictionary = f.readlines()
        f.close

def setData():
    global codeList
    for cameo in cameoList:
        codeList.append({'cameo':cameo['cameo'],'num':0,'status':False})

# 数量不再发生变化，故没有考虑性能
def count():
    global codeList
    isAll = False
    tempCode = ''
    index = 0
    for line in dictionary:
        if '(' in line: # 介词不翻译，不计算在哪
            continue
        if line.startswith('---'):
            isAll = False
            index = 0 # 重置
            code = line.split('[')[-1].split(']')[0]
            if code == '---':
                codeList[index]['num'] = codeList[index]['num']+1
            else:
                isAll = True
                tempCode = code
                for i, cameo in enumerate(cameoList):
                    if cameo['cameo'] == code:
                        index = i
                        break
        else:
            if isAll:
                codeList[index]['num'] = codeList[index]['num']+1
            # 动词中含有的暂时不算在，归类为无分类
            if not line.startswith('-'):
                codeList[0]['num'] = codeList[0]['num']+1
            else:
                code = line.split('[')[-1].split(']')[0]
                if code == '':
                    codeList[0]['num'] = codeList[0]['num']+1
                else:
                    for cameo in codeList:
                        if code.startswith(cameo['cameo']):
                            cameo['num'] = cameo['num'] +1
            

def writeFile():
    global codeList
    with open(CAMEO_STATUS_FILE, 'w') as json_file:
        json.dump(codeList, json_file, ensure_ascii=False)
        json_file.close()
        print('JSON File saved!')

if __name__ == "__main__":
    readFile()
    setData()
    count()
    writeFile()