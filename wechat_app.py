from flask import Flask
from flask import request
import hashlib
from flask import render_template
import xml.etree.ElementTree as ET
import logging
import requests
import time

app = Flask(__name__)

@app.route("/wechat", methods=['GET', 'POST'])
def index():
    if request.method == "GET":  # 判断请求方式是GET请求
        my_signature = request.args.get('signature')  # 获取携带的signature参数
        my_timestamp = request.args.get('timestamp')  # 获取携带的timestamp参数
        my_nonce = request.args.get('nonce')  # 获取携带的nonce参数
        my_echostr = request.args.get('echostr')  # 获取携带的echostr参数

        logger.warning("signature=%s&timestamp=%s&noce=%s&echostr=%s" % (my_signature,my_timestamp,my_nonce,my_echostr))

        token = 'lxdemon'  # 一定要跟刚刚填写的token一致

        # 进行字典排序
        data = [token, my_timestamp, my_nonce]
        data.sort()

        # 拼接成字符串
        temp = ''.join(data)

        # 进行sha1加密
        mysignature = hashlib.sha1(temp.encode('utf-8')).hexdigest()

        # 加密后的字符串可与signature对比，标识该请求来源于微信
        if my_signature == mysignature:
            return my_echostr
        else:
            return "get token failed"

    else:
        # 读取接收到的xml
        rec = request.stream.read()
        xml_rec = ET.fromstring(rec)

        return reply(xml_rec)

'''
解析微信用户请求并回复
'''
def reply(xml_rec):
    # 解析xml
    toUser = xml_rec.find('ToUserName').text
    fromUser = xml_rec.find('FromUserName').text
    createTime = str(int(time.time()))
    msgType = xml_rec.find('MsgType').text
    logger.warning("received message type -> %s" % msgType)
    logger.warning("from <- %s" % fromUser)
    logger.warning("to -> %s" % toUser)

    if msgType == 'text':
        content = xml_rec.find('Content').text
        reply = '''<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>'''
        response = app.make_response(reply % (fromUser, toUser, createTime, msgType, content))
        response.content_type = 'application/xml'
        return response

    elif msgType == 'image':
        # mediaId = 'wvwLS3TL27KDwQ9O5c_6oO_2p9IJoavFez3KnPRsERobd2ViGxPawj4k0LvIpme9'
        mediaId = xml_rec.find('MediaId').text
        reply = '''<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Image><MediaId><![CDATA[%s]]></MediaId></Image>
                </xml>'''
        response = app.make_response(reply % (fromUser, toUser, createTime, msgType, mediaId))
        response.content_type = 'application/xml'
        return response

    elif msgType == 'voice':
        # content = 'success'
        # reply = '''<xml>
        #         <ToUserName><![CDATA[%s]]></ToUserName>
        #         <FromUserName><![CDATA[%s]]></FromUserName>
        #         <CreateTime>%s</CreateTime>
        #         <MsgType><![CDATA[%s]]></MsgType>
        #         <Content><![CDATA[%s]]></Content>
        #         </xml>'''
        # response = app.make_response(reply % (fromUser, toUser, createTime, msgType, content))
        return "success"

    elif msgType == 'video':
        return "success"
    elif msgType == 'shortvideo':
        return "success"
    elif msgType == 'location':
        return "success"
    elif msgType == 'link':
        return "success"


# https请求方式: GEThttps://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
def getWechatAccessToken():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential'
    appid = 'wx267dbb8ed2f283cd'
    secret = 'a5b96746089ea0c5860cbcdd65365f35'
    paras = {'appid':appid, 'secret':secret}

    res = requests.get(url, paras)
    logger.warning('Access_token url:%s', res.url)
    obj = res.json()
    logger.warning('JSON decode status_code:%s', res.status_code)
    logger.warning('JSON body:%s', obj)
    logger.warning('Access_token:%s', obj['access_token'])
    logger.warning('expires_in:%s', obj['expires_in'])


if __name__ == "__main__":
    # logfile = 'log.txt'
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # hdlr = logging.FileHandler(logfile)
    # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # hdlr.setFormatter(formatter)
    # logger.addHandler(hdlr)
    app.run()
    # getWechatAccessToken()


