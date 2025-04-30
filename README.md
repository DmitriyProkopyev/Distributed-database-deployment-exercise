# Distributed-database-deployment-exercise

This repository contains a group exercise on deploying a reliable distributed database system using Kubernetes.

---

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/DmitriyProkopyev/Distributed-database-deployment-exercise.git
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
A browser tab will open at [http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/](http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/).  
Here you can view all your Kubernetes resources, check pod logs, and monitor the cluster status.  
- The **"Workloads"** tab shows all running pods and deployments.
- The **"Services"** tab lists all exposed services and their cluster IPs.
- You can use the **"Logs"** button next to any pod to view its logs.

---

### 8. Access the application UI

After deployment, the application is available at [http://localhost:3000](http://localhost:3000) (replace with your actual port if different).  
..............ADD INFORMATION...................

---

### 9. Access Jaeger dashboard

If Jaeger is deployed, you can access the tracing dashboard at [http://localhost:16686](http://localhost:16686).  
- Here you can view traces of requests passing through your distributed system.
- Use the search panel to select a service and see detailed traces.

---

## Project Structure

- `config/` — Kubernetes manifests for deploying the distributed database and related services.
