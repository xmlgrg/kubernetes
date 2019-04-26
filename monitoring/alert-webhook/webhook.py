#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "w.z"
# Date: 2019/3/4

"""
版本：V1
功能：收集警报，发送到不同的钉钉组
TODO：按照team来发送消息到不同的钉钉组
---
版本：V3.2
功能：增加接收grafana 警报的接口
TODO：transform 代码优化
---
版本： V3.7
功能： 琪祥修改 nochangeme
镜像： reg-bj.xiaoneng.cn/k8s/webhook_dingding:v3.7
---
版本： V3.8
功能： 修改报警收敛，alertmanager的报警信息有分组，抑制静默和延时功能
"""

from flask import Flask
from flask import request
import json
import requests
import time
import datetime

app = Flask(__name__)


# 数据转换成钉钉格式  数据来源alertmanager
def transform(data_from_am):
    print("转化成钉钉格式数据-alertmanager:", data_from_am)
    links = []
    for alert in data_from_am['alerts']:
        #    print("从alert_data里取出alert: ", alert)
        fire_msg = {}
        fire_msg['title'] = alert['labels'].get('alertname')
        level = alert["labels"].get("severity")
        instance = alert["labels"].get("ipaddress")
        device = alert["labels"].get("device")
        alertname = alert["labels"].get("alertname")
        job = alert["labels"].get("job")
        if alert.get("annotations"):
            annotations_msg = alert["annotations"].get("message")
        time_start = alert["startsAt"].split(".")[0]
        time_start = datetime.datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=8)
        time_now = time.strftime('%Y-%m-%d %X')
        generatorurl = prometheus_url + "/" + alert["generatorURL"].split('/')[-1]
        # generatorurl = alert["generatorURL"]
        fire_msg['text'] = " ### 环境：{0}\n".format(receiver) + \
                           "--- \n" + \
                           ">- instance: {} \n".format(instance) + \
                           ">- job: {} \n".format(job) + \
                           ">- level：{0}\n".format(level) + \
                           ">- alertname: **{}** \n".format(alertname) + \
                           ">- message: **{}** \n".format(annotations_msg) + \
                           ">- start_time: {} \n".format(time_start) + \
                           ">- new_time: {} \n".format(time_now) + \
                           "\n" + \
                           "--- \n" + \
                           "### 报警url： [url]({}) \n".format(generatorurl)
        links.append(fire_msg)
    return links


# 数据转换成钉钉格式  数据来源grafana
def transform_grafana(data_from_am):
    print("转化成钉钉格式数据-grafana:", data_from_am)
    links = []
    for alert in data_from_am.get('evalMatches'):
        print("wtf alert -----", alert)
        fire_msg = {}
        fire_msg['title'] = data_from_am.get("title")
        receiver = data_from_am.get("ruleName")
        level = data_from_am.get("state")
        instance = alert.get('tags').get('instance')
        pod = alert.get('tags').get('pod')
        alertname = data_from_am.get("message")
        job = alert.get("tags").get("job")
        if alert.get("annotations"):
            annotations_msg = alert["annotations"].get("message")
        else:
            annotations_msg = data_from_am.get('ruleUrl')
        time_now = time.ctime()
        generatorurl = grafana_url + '/' + data_from_am.get('ruleUrl').split("3000")[1]
        status = data_from_am.get("state")

        fire_msg['text'] = "#### **监控报警-G** \n" + \
                           "> #### Labels: \n" + \
                           ">- receiver: {} \n".format(receiver) + \
                           ">- instance: {} \n".format(instance) + \
                           ">- pod: **{}** \n".format(pod) + \
                           ">- alertname: **{}** \n".format(alertname) + \
                           ">- status: {} \n".format(status) + \
                           ">- job: {} \n".format(job) + \
                           "> #### 信息: \n" + \
                           ">- message: **{}** \n".format(annotations_msg) + \
                           ">- time: {} \n".format(time_now) + \
                           "##### {} [url]({}) \n".format(time_now, generatorurl)
        links.append(fire_msg)
    return links


def alert_data(alerts_data):
    url = DING_API
    headers = {'Content-Type': 'application/json'}
    at = {
        "atMobiles": [
            "18600085132"
        ],
        "isAtAll": False
    }
    if "receiver" in alerts_data:
        print("进入alertmanager报警通道")
        for markdown in transform(alerts_data):
            send_data = {"msgtype": "markdown", "markdown": markdown, "at": at}
            print("发送至钉钉数据：", json.dumps(send_data))
            requests.post(url, data=json.dumps(send_data), headers=headers)
    elif "evalMatches" in alerts_data:
        print("进入grafana报警通道")
        for markdown in transform_grafana(alerts_data):
            send_data = {"msgtype": "markdown", "markdown": markdown, "at": at}
            print("发送至钉钉数据：", json.dumps(send_data))
            requests.post(url, data=json.dumps(send_data), headers=headers)
    else:
        print("数据来源不匹配alertmanager 或者 grafana: ", alerts_data)


# grafana接口
@app.route('/v1/grafana/post', methods=['POST'])
def sendgrafana():
    if request.method == 'POST':
        print("开始处理 alertmanager 告警: ")
        post_data = request.get_data()
        post_data = post_data.decode('utf-8')
        post_data = json.loads(post_data)
        print("接收请求数据: ", post_data)
        alert_data(post_data)
    return "succeed"


# alertmanager 接口
@app.route('/v1/alertmanager/post', methods=['POST'])
def send():
    if request.method == 'POST':
        print("开始处理 alertmanager 告警: ")
        post_data = request.get_data()
        post_data = post_data.decode('utf-8')
        post_data = json.loads(post_data)
        print("接收请求数据: ", post_data)
        alert_data(post_data)
    return "succeed"


if __name__ == '__main__':
    # k8s集群任意一节点IP
    grafana_url = 'http://129.150.78.47:32681'
    # 钉钉 机器人 token
    DING_API = '{https://oapi.dingtalk.com/robot/send?access_token=750a384810bbb8862a780a5abf66323d6c5409821a2f112ad2a4ce795ab62272}'
    receiver = '{CG_ENV}'
    prometheus_url = '{http://129.150.125.54:32497}'
    app.run(host='0.0.0.0', port=80)
