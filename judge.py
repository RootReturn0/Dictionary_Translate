# 人工检查翻译是否正确

import var
import time

def judge(tempDictList):
    print(tempDictList)
    if tempDictList == []:
        return []
    var.toBeTranslated=tempDictList
    var.translating=True
    while(var.translating):
        # print('waiting')
        continue

    var.toBeTranslated = []
    print(var.translatedRes)
    res=var.translatedRes
    return res

# def judge(blockMeaning, originWords, cameoCode, translatedWords):
#     data={
#         'class': blockMeaning,
#         'origin': originWords,
#         'code': cameoCode,
#         'Chinese': translatedWords
#     }
#     res=rest_server.send_data(data)
#     return res
    # return 'y'
    # print('原始分类: '+blockMeaning,
    #       '原始字典: '+originWords,
    #       'Cameo代码: '+cameoCode,
    #       '翻译结果: '+translatedWords,
    #       ' ',
    #       sep='\n')
    # print('翻译结果符合\"分类\"请输入”y“;',
    #       '翻译结果与\"分类\"明显不符请输入“n”;',
    #       #   '本词暂不翻译请输入“c:',
    #       sep='\n')
    # while(1):
    #     ans = input()
    #     if(ans == 'y' or ans == 'Y'):
    #         return 'y'
    #     elif(ans == 'n' or ans == 'N'):
    #         return 'n'
    #     # elif(ans == 'c' or ans == 'C'):
    #     #     return 'c'
    #     else:
    #         print('无法识别您的输入，请重新输入: ')
