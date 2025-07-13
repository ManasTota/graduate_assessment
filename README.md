# Ericsson Graduate Assessment Project Documentation
This project demonstrates 

* Simple CRUD Application - Task Manager
* Python Flask + PostgreSQL DB
* Deployed on Google Kubernetes Engine (GKE)
* Incorporated monitoring using Prometheus and Grafana
* Includes Shell and Python scripting
* Established a CI/CD Pipeline using GitHub Actions


## Makefile
A [Makefile](https://github.com/ManasTota/graduate_assessment/blob/main/makefile) is provided to automate common tasks like building, tagging, pushing Docker images, and deploying to Kubernetes.

### Commands to be used

#### 1. ```make clean``` - Clean and delete everything (pods, services etc)
#### 2. ```make all``` - Create everything (Build, Install, Push, Deploy)



## Task 1 - Build a Kubernetes Cluster

### Installing Google Cloud CLI
```
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")

& $env:Temp\GoogleCloudSDKInstaller.exe
```

### Creating a GKE cluster
```
gcloud container clusters create ericsson-task-cluster \
    --zone europe-north2-c \
    --num-nodes 2 \
    --machine-type e2-medium \
    --enable-autoscaling \
    --min-nodes 2 \
    --max-nodes 3
```

### Install GKE Gcloud Auth Plugin
```
gcloud components install gke-gcloud-auth-plugin
```


## Task 2 - Simple CRUD Application
### Created ```Task Manager``` Application - http://34.51.213.66:5000
* Frontend and Backend - ```Python Flask```
* Database - ```PostgreSQL```
* [Code](https://github.com/ManasTota/graduate_assessment/blob/main/flask_app/app.py)
* [Video Drive link](https://drive.google.com/file/d/1db9ICi1gmgsh20OoQ4EcR98B1kU7gK7U/view?usp=drive_link)





https://github.com/user-attachments/assets/8c583e7f-98f4-4c60-968b-f9f9f77fe2f9






### Docker
#### 1. Creating PostgreSQL in a Docker container
    
    docker run --name taskmaster \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_DB=mydb \
      -p 5432:5432 \
      -d postgres
    

#### 2. Dockerfile
We have the Dockerfile [here](https://github.com/ManasTota/graduate_assessment/blob/main/Dockerfile)

#### 3. Building Dockerfile and running locally
Building docker image
```
docker build -t flask-app .
```

Running the docker image
```
docker run --env-file flask_app/.env -p 5000:5000 flask-app
```

### Google Artifact Registry Integration

#### 1. Creating a repo
Creates a Docker repository named ```ericsson``` in the ```europe-north2``` region

    gcloud artifacts repositories create ericsson --repository-format=docker --location=europe-north2 --description="Ericsson task repository"

#### 2. Taging Docker image
Tags the local ```flask-app``` image with the full path to your Artifact Registry.

    docker tag flask-app europe-north2-docker.pkg.dev/ericsson-project-465613/ericsson/flask-app:latest


#### 3. Authenticate Docker
Configures Docker to use gcloud credentials for pushing/pulling images from Artifact Registry.
    
    gcloud auth configure-docker europe-north2-docker.pkg.dev


#### 4. Pushing Docker Image
Pushes the tagged Docker image to the Artifact Registry.

    docker push europe-north2-docker.pkg.dev/ericsson-project-465613/ericsson/flask-app:latest


### Kubernetes Deployment

#### 1. Create Secrets
Creates a Kubernetes Secret named ```app-secrets``` from key-value pairs from an ```.env.deployment``` file

    kubectl create secret generic app-secrets --from-env-file=.env.deployment

Example ```.env.deployment``` file

    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=mydb
    POSTGRES_HOST=taskmaster
    POSTGRES_PORT=5432


#### 2. Kubernetes Manifests

We have Kubernetes Manifests like ```deployment.yaml``` [here](https://github.com/ManasTota/graduate_assessment/blob/main/k8s/deployment.yaml)

#### 3. Applying Manifests

    kubectl apply -f deployment.yaml

#### 4. Accessing the Frontend Service
As we are using GKE with a LoadBalancer. We have the application running at ```flask-app-external-ip:port```

    kubectl get svc

We have flask app running at ```http://34.51.213.66:5000```


## Task 3 - Monitoring with Prometheus & Grafana

### 1. Installing Prometheus and Grafana

#### Installing Prometheus

    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

#### Installs the ```kube-prometheus-stack``` chart from the ```prometheus-community``` repository.

#### It uses a custom ```values_prometheus.yaml``` file to override default configurations.

    helm install prometheus prometheus-community/kube-prometheus-stack --values k8s/values_prometheus.yaml

#### Grafana will automatically get installed from the above commands

### 2. Accessing Prometheus and Grafana UI

* #### Prometheus UI
  Forwards local port 9090 to the Prometheus service's port 9090.

  Access Prometheus at ```http://localhost:9090```

      kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

* #### Grafana UI
  Forwards local port 3000 to the Grafana service's port 80.

  Access Grafana at ```http://localhost:3000```

      kubectl port-forward svc/prometheus-grafana 3000:80

  * Default credentials: 

    username - ```admin```

    password - ```admin123```


![Prometheus1](https://github.com/ManasTota/graduate_assessment/blob/main/imgs/Prometheus1.png)
![Prometheus2](https://github.com/ManasTota/graduate_assessment/blob/main/imgs/Prometheus2.png)
![Grafana1](https://github.com/ManasTota/graduate_assessment/blob/main/imgs/Grafana1.png)
![Grafana2](https://github.com/ManasTota/graduate_assessment/blob/main/imgs/Grafana2.png)



## Task 4 - Shell Scripting and Python Automation

### Shell - monitor.sh
Created ```monitor.sh``` to 
* [Code](https://github.com/ManasTota/graduate_assessment/blob/main/monitoring/moniter.sh)
* Check memory & CPU usage of a pod
* Alert if usage exceeds threshold

      chmod +x monitoring/monitor.sh

      ./monitoring/monitor.sh [pod_name]

#### Example outputs

Normal case

    Checking resource usage for pod: flask-app-858c74c57f-k7ndn
    ✅ Monitoring completed.

Alerting (if exceeeds) 

    Checking resource usage for pod: flask-app-858c74c57f-k7ndn
    ⚠️ Memory usage alert for flask-app-858c74c57f-k7ndn: 30Mi exceeds 10Mi
    ✅ Monitoring completed.


### Python - prometheus_query.py
Created ```prometheus_query.py``` using
* [Code](https://github.com/ManasTota/graduate_assessment/blob/main/monitoring/prometheus_query.py)
* Query Prometheus API
* Return current CPU usage of a pod in JSON

      python monitoring/prometheus_query.py [pod_name]

#### Example output - json format

```
[
  {
    "namespace": "default",
    "pod": "flask-app-858c74c57f-k7ndn",
    "cpu_usage_cores": 0.00066727,
    "memory_usage_bytes": 34684928.0
  }
]
```


### ```Note``` : Ensure ```Prometheus``` is running before running the above scripts i.e.

    # Port-forward Prometheus UI
    kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090


## Task 5 - CI/CD Pipeline Github Actions

### GitHub Actions Workflow (.github/workflows/cicd.yml)
CI/CD - Build, Push to Artifact Registry, and Deploy to GKE

* How the pipeline is triggered:
  * Typically, the pipeline is triggered on ```push``` events into ```main``` branch
  * [Code](https://github.com/ManasTota/graduate_assessment/blob/main/.github/workflows/cicd.yml)
  * [Video drive link](https://drive.google.com/file/d/1PATaijuRCVmYLX85j9STBSlYwuFN0E_B/view?usp=drive_link)
 




### OIDC Authentication

"Cloud Workload Identity Federation" is the broader Google Cloud service that enables external identities (like those from GitHub Actions) to authenticate to Google Cloud resources. OpenID Connect (OIDC) is the specific protocol that Workload Identity Federation uses to achieve this.

### 1. Create a Service Account

    gcloud iam service-accounts create github-actions-service-account \
    --description="A service account for use in a GitHub Actions workflow" \
    --display-name="GitHub Actions service account."


### 2. Grant Artifact Registry Push Permissions
This allows the service account to push Docker images to your Artifact Registry.

    gcloud artifacts repositories add-iam-policy-binding ericsson \
      --location=europe-north2 \
      --role=roles/artifactregistry.createOnPushWriter \
      --member=serviceAccount:github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com

### 3. Create a Workload Identity Pool
A pool is a collection of external identities that are trusted to access your Google Cloud resource

    gcloud iam workload-identity-pools create "flask-app-dev-pool" \
      --project=ericsson-project-465613 \
      --location=global \
      --display-name="Identity pool for my flask app"


### 4. Create a Workload Identity Pool Provider
This provider links your GitHub Actions OIDC (OpenID Connect) issuer to the identity pool.

    gcloud iam workload-identity-pools providers create-oidc "github-actions-provider" \
      --location="global" \
      --workload-identity-pool="flask-app-dev-pool" \
      --display-name="Provider for GitHub Actions" \
      --issuer-uri="https://token.actions.githubusercontent.com" \
      --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
      --attribute-condition="attribute.repository_owner=='ManasTota' && attribute.repository=='graduate_assessment'"

### 5. Describing Identity Pool Provider

    gcloud iam workload-identity-pools providers describe github-actions-provider \
      --location=global \
      --workload-identity-pool="flask-app-dev-pool"

```output```:

    name: projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool/providers/github-actions-provider

### 6. Grant the Service Account Token Creator via a gmail

    gcloud iam service-accounts add-iam-policy-binding \
      github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com \
      --role=roles/iam.serviceAccountTokenCreator \
      --member=user:nantota87@gmail.com

### 7. Describing the Flask app Pool

    gcloud iam workload-identity-pools describe "flask-app-dev-pool" \
      --location=global

```output```:

    name: projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool

exporting as env var

    export WIP_POOL=projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool


### 8. Grant Workload Identity User Role:
This binding allows the GitHub Actions identity (from the specific repository) to impersonate your Google Cloud service account

    gcloud iam service-accounts add-iam-policy-binding \
      github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com \
      --role=roles/iam.workloadIdentityUser \
      --member=principalSet://iam.googleapis.com/${WIP_POOL}/attribute.repository/ManasTota/graduate_assessment


### 9. Updating OIDC Permissions:

    gcloud iam workload-identity-pools providers update-oidc \
      github-actions-provider \
      --project=ericsson-project-465613 \
      --location=global \
      --workload-identity-pool=flask-app-dev-pool \
      --attribute-condition="assertion.repository_owner == 'ManasTota'"


### 10. Grant GKE Developer Permissions:
This role allows the service account to deploy and manage resources in your GKE cluster.

    gcloud projects add-iam-policy-binding ericsson-project-465613 \
        --member="serviceAccount:github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com" \
        --role="roles/container.developer"

### 11. Grant Artifact Registry Reader Permissions:
This allows the GKE nodes (when pulling images for deployments) to read images from your Artifact Registry.

    gcloud projects add-iam-policy-binding ericsson-project-465613 \
        --member="serviceAccount:github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com" \
        --role="roles/artifactregistry.reader"
