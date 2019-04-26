# Kubernetes 全栈监控

## metric-server 

- 使用metric-server收集数据给kubernetes集群内使用，如kubectl,hpa,scheduler等



github项目官方托管地址为：https://github.com/kubernetes/kube-state-metrics



## operator 

- 使用prometheus-operator部署prometheus，存储监控数据



github项目官方托管地址为：https://github.com/coreos/prometheus-operator



## kube-state-metrics  

- 使用kube-state-metrics收集k8s集群内资源对象数据



github项目官方托管地址为：https://github.com/kubernetes/kube-state-metrics



## node-exporter  

- 使用node_exporter收集集群中各节点的数据

github项目官方托管地址为：https://github.com/prometheus/node_exporter



## prometheus

- 使用prometheus收集apiserver，scheduler，controller-manager，kubelet组件数据



githb项目官方托管地址为：https://github.com/prometheus/prometheus



## alertmanager  

- 使用alertmanager实现监控报警



githb项目官方托管地址为：https://github.com/prometheus/alertmanager



## alert-webhook  

- 定义钉钉webhook，实现钉钉告警



## grafana    

- 使用grafana实现数据可视化



githb官方项目托管地址为：https://github.com/grafana/grafana



## adapter    

- 使用prometheus-adapter实现 pod 的hpa(自动伸缩)   



项目地址：https://github.com/DirectXMan12/k8s-prometheus-adapter



## serviceMonitor

- 使用serviceMonitor实现服务监控





