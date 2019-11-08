#!flask/bin/python
################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------
# This file implements the REST layer. It uses flask micro framework for server implementation. Calls from front end reaches
# here as json and being branched out to each projects. Basic level of validation is also being done in this file. #
#-------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################
from flask import Flask, jsonify, abort, request, make_response, url_for, redirect, render_template
from flask_httpauth import HTTPBasicAuth
import os
import shutil
import subprocess
import json


app = Flask(__name__)

data = [{
    'class': "123",
    'origin': 'apple',
    'code': '[070]',
    'Chinese': '苹果'
}, {
    'class': "123",
    'origin': 'apple',
    'code': '[070]',
    'Chinese': '苹果果'
}]

res = True

lock = True  # lock for judge process

end = False

def test1():
    global data
    print(data)
    data=[]

def test2():
    global data
    print('sda',data)


def start():
    global end
    end =False
    app.run(debug=True, threaded=True, host='127.0.0.1', port=5000)


def send_data(receive):
    global data
    data = receive
    # print(data)
    global lock
    while(True):
        global lock
        if(not lock):
            break
    lock = True

    global res
    return res

def end_signal():
    global end
    if end:
        print('End pass?!')
    return end

#==============================================================================================================================
#
#  This function is used to push result
#
#==============================================================================================================================
@app.route('/upload', methods=['POST', 'GET'])
def show_results():

    print("show results")
    global data
    print(data)

    if request.method == 'POST' or request.method == 'GET':
        return jsonify(data)

#==============================================================================================================================
#
#  This function is used to limit results
#
#==============================================================================================================================
@app.route('/results', methods=['POST'])
#def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def get_judges():
    print("receive judge results")

    if request.method == 'POST':
        jsonData = json.loads(request.data)
        global res
        res = jsonData
        print(res)
        global lock
        lock = False
        return "succeed!"

#==============================================================================================================================
#
#  This function is used to send end signal
#
#==============================================================================================================================
@app.route('/end', methods=['POST'])
#def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def end():
    print("Ends Manually!")

    if request.method == 'POST':
        global end
        end = True
        global res
        res = []
        global lock
        lock = False
        return "End succeed!"


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
    app.run(debug=True, threaded=True, host='127.0.0.1', port=5000)
