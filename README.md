# Distributed-database-deployment-exercise
Implemented group exercise on deploying a reliable distributed database system


---

## 1. Подключение к серверу по SSH

```sh
ssh -i <path_to_your_private_ssh> -p 6002 developer@10.100.30.239
```

---

## 2. Установка Minikube и kubectl (установлены)

### Установка kubectl

```sh
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

### Установка Minikube

```sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
```

---

## 3. Перенос конфига на сервер (перенесено)

```sh
scp -i <path_to_your_private_ssh> -P 6002 -r /path/to/your/yaml/folder developer@10.100.30.239:~/config
```
- `/path/to/your/yaml/folder` — путь к папке с yaml-файлами.

---

## 4. Запуск Minikube на сервере

```sh
minikube start --driver=docker --memory=4096 --cpus=2
```

---

## 5. Применение конфига

```sh
kubectl apply -f ~/config/mongodb
```

---

## 6. Проверка 

```sh
kubectl get pods
kubectl get svc
```


## 7. Проверка статуса minikube
```sh
minikube status
```

## 8. Запуск дэшборда 
```sh
minikube dashboard
```
Откроется вкладка в браузере с дэшбордом