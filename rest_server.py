#!flask/bin/python
################################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------------
# This file implements the REST layer. It uses flask micro framework for server implementation. Calls from front end reaches
# here as json and being branched out to each projects. Basic level of validation is also being done in this file. #
# -------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################
from flask import Flask, jsonify, abort, request, make_response, url_for, redirect, render_template, send_file
from flask_httpauth import HTTPBasicAuth
import os
import shutil
import subprocess
import json
import threading

import var
import demo

app = Flask(__name__)

CAMEO_CODE_FILE = os.path.join(os.path.abspath('.'), 'doc/CameoCode.json')
CAMEO_STATUS_FILE = os.path.join(os.path.abspath('.'), 'CameoStatus.json')
cameo_code_list = []
cameo_status_list = []


lock = True  # lock for judge process
demoStart=False


def start():
    global cameo_code_list
    var.end =False
    var.save=True
    print(CAMEO_CODE_FILE)
    print(demo.ORIGENAL_DICTIONARY)
    print(CAMEO_STATUS_FILE )
    with open(CAMEO_CODE_FILE, 'r') as f:
        cameo_code_list = json.load(f)
        f.close()
    with open(CAMEO_STATUS_FILE, 'r') as f:
        global cameo_status_list
        cameo_status_list = json.load(f)
        f.close()

    var.loading = False
    threading.Thread(target=checkData, args=()).start()
    app.run(debug=True, threaded=True, host='127.0.0.1', port=5050)


def checkData():
    while(True):
        if(var.toBeTranslated):
            # print(data)
            global lock
            while(True):
                global lock
                if(not lock):
                    break
            lock = True
            var.translating = False


# ==============================================================================================================================
#
#  This function is used to send file
#
# ==============================================================================================================================
@app.route('/return_file', methods=['GET'])
def return_file():
    file_name = 'Cameo中文字典.txt'
    file_path = os.path.join(os.path.abspath('.'), file_name)
    # 首先定义一个生成器，每次读取512个字节

    return send_file(file_path)

# ==============================================================================================================================
#
#  This function is used to init menu
#
# ==============================================================================================================================
@app.route('/init', methods=['GET'])
def init():
    if request.method == 'GET':
        # print(cameo_status_list)
        return jsonify(cameo_status_list)

# ==============================================================================================================================
#
#  This function is used to set category
#
# ==============================================================================================================================
@app.route('/setCategory', methods=['POST'])
def receiveCategory():
    print("receive category")
    global demoStart
    if request.method == 'POST':
        jsonData = json.loads(request.data)
        var.category = jsonData['category']
        # print(var.category)
        var.end=False
        if not demoStart:
            demoStart=True
            threading.Thread(target=demo.translateFile, args=()).start()
        return jsonify({'flag':True})

# ==============================================================================================================================
#
#  This function is used to push result
#
# ==============================================================================================================================
@app.route('/upload', methods=['POST', 'GET'])
def show_results():

    # print("show results")

    if request.method == 'POST' or request.method == 'GET':
        # print(data)

        cameoData = []

        for item in var.toBeTranslated:
            flag = False
            for i in cameoData:
                if i['code'] == item['code']:
                    flag = True
                    break
            if flag:
                continue
            for cameo in cameo_code_list:
                if cameo['cameo'] == item['code']:
                    # print(cameo)
                    cameoData.append({
                        'code': item['code'],
                        'content': cameo
                    })
                    break

        return jsonify({'transData': var.toBeTranslated, 'cameoData': cameoData})

# ==============================================================================================================================
#
#  This function is used to limit results
#
# ==============================================================================================================================
@app.route('/results', methods=['POST'])
# def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def get_judges():
    print("receive judge results")

    if request.method == 'POST':
        jsonData = json.loads(request.data)
        var.translatedRes = jsonData
        # print(res)
        global lock
        lock = False
        return "succeed!"

# ==============================================================================================================================
#
#  This function is used to send end signal
#
# ==============================================================================================================================
@app.route('/end', methods=['POST'])
# def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def end():
    print("Ends Manually!")

    if request.method == 'POST':
        var.toBeTranslated=[]
        jsonData = json.loads(request.data)
        print(jsonData)
        var.save = False
        for cameo in cameo_status_list:
            if jsonData['category']==cameo['cameo']:
                cameo['status']=True
                var.save=True
                break
        var.end = True
        var.translating=False
        print(cameo_status_list)
        with open(CAMEO_STATUS_FILE, 'w') as json_file:
            json.dump(cameo_status_list, json_file, ensure_ascii=False)
            json_file.close()
            print('Status JSON File saved!')
        global demoStart
        demoStart = False
        if var.save:
            return jsonify({'flag':True,'res':'成功保存结果'})
        else:
            return jsonify({'flag':False,'res':'未保存结果'})


# #==============================================================================================================================
# #
# #                                           Main function                                                        	            #
# #
# #==============================================================================================================================
# @app.route("/")
# def main():

#     return render_template("main.html")


if __name__ == '__main__':
    # print(demo.TARGET_DICTIONARY)
    start()
    # app.run(debug=True, threaded=True, host='127.0.0.1', port=5000)
