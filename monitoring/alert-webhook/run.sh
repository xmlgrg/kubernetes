#!/bin/sh

GRAFANA_URL='http://129.150.78.47:32681'
DING_API='https://oapi.dingtalk.com/robot/send?access_token=750a384810bbb8862a780a5abf66323d6c5409821a2f112ad2a4ce795ab62272'
CG_ENV='bj-v4-n1'
PROMETHEUS_URL='http://129.150.125.54:32497'

sed -i "s#{GRAFANA_URL}#$GRAFANA_URL#g" ./webhook-dingding.py
sed -i "s#{DING_API}#$DING_API#g" ./webhook-dingding.py
sed -i "s#{CG_ENV}#$CG_ENV#g" ./webhook-dingding.py
sed -i "s#{PROMETHEUS_URL}#$PROMETHEUS_URL#g" ./webhook-dingding.py
python3 webhook-dingding.py
