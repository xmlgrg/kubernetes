



# alertmanager webhook配置教程

step 1: 访问[网站](https://work.weixin.qq.com/) 注册企业微信账号（不需要企业认证）。

step 2: 访问[apps](https://work.weixin.qq.com/wework_admin/loginpage_wx#apps) 创建第三方应用，点击创建应用按钮 -> 填写应用信息：



- 其工作模式如下图：

  Prometheus>alertmanager--webhook-->告警Server



- webhook插件类型：

​	告警 server 负责接收 alertmanager 的 webhook 调用，然后根据一定的业务规则，对具体人员下发通知

​       典型的，可以发送短信、发送邮件，企业微信、阿里钉钉告警等



- 告警 server 代码实现方式

```python
#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
                           ">- 实例: {} \n".format(instance) + \
                           ">- job: {} \n".format(job) + \
                           ">- 级别：{0}\n".format(level) + \
                           ">- 警告类型: **{}** \n".format(alertname) + \
                           ">- 日志: **{}** \n".format(annotations_msg) + \
                           ">- 开始时间: {} \n".format(time_start) + \
                           ">- 最新时间: {} \n".format(time_now) + \
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
            "17679412046"
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
```



- 构建告警 server 镜像

  

  **Dockerfile**

```dockerfile
FROM alpine:latest
WORKDIR /webhook-dingding
COPY . /webhook-dingding/
RUN apk update && \
    apk add curl python3 && \
    pip3 install flask requests  requests -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
EXPOSE 80
CMD ["/bin/sh","run.sh"]
```



​	**run.sh**

```shell
#!/bin/sh

GRAFANA_URL='http://129.150.78.47:32681'
DING_API='https://oapi.dingtalk.com/robot/send?access_token=750a384810bbb8862a780a5abf66323d6c5409821a2f112ad2a4ce795ab62272'
CG_ENV='Kubernetes-oracle云'
PROMETHEUS_URL='http://129.150.125.54:32497'

sed -i "s#{GRAFANA_URL}#$GRAFANA_URL#g" ./webhook-dingding.py
sed -i "s#{DING_API}#$DING_API#g" ./webhook-dingding.py
sed -i "s#{CG_ENV}#$CG_ENV#g" ./webhook-dingding.py
sed -i "s#{PROMETHEUS_URL}#$PROMETHEUS_URL#g" ./webhook-dingding.py
python3 webhook-dingding.py
```

​	**构建镜像**

```shell
docker build -t image.yumben.limaomao:v1 .
```



- 创建Webhook-Service

  **编写webhook yaml**

```yaml
# vi webhook.yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  labels:
    app: webhook-ding
  name: webhook-ding
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: webhook-ding
  template:
    metadata:
      labels:
        app: webhook-ding
    spec:
      containers:
      - env:
        - name: DING_API
#线上
          value: https://oapi.dingtalk.com/robot/send?access_token=750a384810bbb8862a780a5abf66323d6c5409821a2f112ad2a4ce795ab62272
#测试
#          value: https://oapi.dingtalk.com/robot/send?access_token=57f8562a3489757020a75ad8a4cf28a5049e027eb03708d87af6004c3ff94c43
        - name: GRAFANA_URL
          value: http://129.150.78.47:32681
        - name: PROMETHEUS_URL
          value: http://129.150.125.54:32497
        - name: CG_ENV
          value: 'yumben-limaomao'
        image: image.yumben.limaomao:v1
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 3
          initialDelaySeconds: 10
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 5
        name: webhook-ding
        ports:
        - containerPort: 80
          name: webhook-ding
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          initialDelaySeconds: 10
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 5
        resources:
          limits:
            cpu: "1"
            memory: 1000Mi
          requests:
            cpu: 500m
            memory: 500Mi
        volumeMounts:
        - mountPath: /etc/localtime
          name: timezone
      restartPolicy: Always
      volumes:
      - name: timezone
        hostPath:
          path: /etc/localtime

---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: webhook-ding
  name: dingding-svc
  namespace: monitoring
spec:
  clusterIP: None
  ports:
  - name: http
    port: 80
    targetPort: webhook-ding
  selector:
    app: webhook-ding
```



​	**创建webhook service****

```shell
kubectl create -f  webhook.yaml
```



- 配置 alertmanager webhook 地址 

 prometheus alertmanager 支持配置自动发现和更新,只需要重新生成配置即可

  删除原有的配置项

```shell
kubectl delete secret alertmanager-main -n monitoring
```



- 编写一个 webhook 配置文件，命名为 alertmanager.yaml

```yaml
# vi alertmanager.yaml
global:
  resolve_timeout: 5m
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'webhook'
receivers:
- name: 'webhook'
  webhook_configs:
  - url: 'http://dingding-svc.monitoring/v1/alertmanager/post' 
```



- url 要跟  flask-alert-service 提供的服务地址对应上

```
kubectl create secret generic alertmanager-main --from-file=alertmanager.yaml -n monitoring
```



- 登录[Alertmanager](http://129.150.78.47:32072/#)查看statusconfig是否发生变化

```yaml
Config

global:
  resolve_timeout: 5m
  http_config: {}
  smtp_hello: localhost
  smtp_require_tls: true
  pagerduty_url: https://events.pagerduty.com/v2/enqueue
  hipchat_api_url: https://api.hipchat.com/
  opsgenie_api_url: https://api.opsgenie.com/
  wechat_api_url: https://qyapi.weixin.qq.com/cgi-bin/
  victorops_api_url: https://alert.victorops.com/integrations/generic/20131114/alert/
route:
  receiver: webhook
  group_by:
  - alertname
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
receivers:
- name: webhook
  webhook_configs:
  - send_resolved: true
    http_config: {}
    url: http://dingding-svc.monitoring/v1/alertmanager/post
templates: []
```

