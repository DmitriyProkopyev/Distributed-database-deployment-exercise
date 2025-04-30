# Distributed-database-deployment-exercise

This repository contains a group exercise on deploying a reliable distributed database system using Kubernetes.

---

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/<your-org>/Distributed-database-deployment-exercise.git
cd Distributed-database-deployment-exercise
```

---

## Installation

### 2. Install Minikube and kubectl

#### Install kubectl

```sh
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

#### Install Minikube

```sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
```

---

## Usage

### 3. Start Minikube

```sh
minikube start --driver=docker --memory=4096 --cpus=2
```

---

### 4. Deploy the configuration

```sh
kubectl apply -f ./config/mongodb
```

---

### 5. Check deployment status

```sh
kubectl get pods
kubectl get svc
```

---

### 6. Check Minikube status

```sh
minikube status
```

---

### 7. Launch the Kubernetes dashboard

```sh
minikube dashboard
```
A browser tab with the dashboard will open.

---

## Project Structure

- `config/` — Kubernetes manifests for deploying the distributed database and related services.
