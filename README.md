# graduate_assessment
Ericsson Graduate Assessment Project


# Installed Google Cloud CLI using

(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")

& $env:Temp\GoogleCloudSDKInstaller.exe


# Created a K8s cluster using
gcloud container clusters create ericsson-task-cluster \
    --zone europe-north2-c \
    --num-nodes 2 \
    --machine-type e2-medium \
    --enable-autoscaling \
    --min-nodes 2 \
    --max-nodes 3

# Gcloud Auth Plugin
gcloud components install gke-gcloud-auth-plugin



# docker with postgres and poetry
docker run --name taskmaster \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=mydb \
  -p 5431:5432 \
  -d postgres


# Dockerfile - build and run

### Building docker image
docker build -t flask-app .

### Running the docker image
docker run --env-file flask_app/.env -p 5000:5000 flask-app





# Creating a Google Artifact Repository

### Creating a repo
gcloud artifacts repositories create ericsson --repository-format=docker --location=europe-north2 --description="Ericsson task repository"

### Taging Docker image
docker tag flask-app europe-north2-docker.pkg.dev/ericsson-project-465613/ericsson/flask-app:latest

### Auth
gcloud auth configure-docker europe-north2-docker.pkg.dev

### Pushing image
docker push europe-north2-docker.pkg.dev/ericsson-project-465613/ericsson/flask-app:latest



# K8s

### Build and Run deployments.yaml
kubectl apply -f deployment.yaml
kubectl get svc --> use external ip and port for flask app

### Creating Secrets file using .env
kubectl create secret generic app-secrets --from-env-file=.env.deployment



# Created Makefile
using all the important commands from above - like Build, tag, push, deploy etc




# Helm for Prometheus and Grafana

### Installing prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

### Adding promethues 
helm install prometheus prometheus-community/kube-prometheus-stack --values values_prometheus.yaml



# Accessing Prometheus and Grafana

### Promotheus
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
website - http://localhost:9090

### Grafana
kubectl port-forward svc/prometheus-grafana 3000:80
website - http://localhost:3000
username - admin
password - admin123