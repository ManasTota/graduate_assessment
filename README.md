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
<!-- helm install prometheus prometheus-community/kube-prometheus-stack --values k8s/values_prometheus.yaml -->

helm install tutorial bitnami/kube-prometheus --version 8.2.2 --values k8s/values_prometheus.yaml


# Accessing Prometheus and Grafana

### Promotheus
<!-- kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -->
kubectl port-forward svc/tutorial-kube-prometheus-prometheus 9090:9090
website - http://localhost:9090

### Grafana
kubectl port-forward svc/prometheus-grafana 3000:80
website - http://localhost:3000
username - admin
password - admin123






# Task 4 - Shell scripting and Python automation

### Monitoring - moniter.sh
chmod +x moniter.sh
./monitoring/moniter.sh [pod_name]


### Prometheus_query.py

#### First make sure prometheus is running in http://localhost:9090
kubectl port-forward svc/tutorial-kube-prometheus-prometheus 9090:9090

#### Run the py script
python monitoring/prometheus_query.py [pod_name]




# Task 5 - CI/CD Pipeline Jenkins

### Insalling Jenkins via Helm
helm repo add jenkins https://charts.jenkins.io
helm repo update

helm install jenkins jenkins/jenkins -f k8s/jenkins_values.yaml --wait

Get your 'admin' user password by running:
kubectl exec --namespace default $(kubectl get pods --namespace default -l app.kubernetes.io/component=jenkins-controller -o jsonpath='{.items[0].metadata.name}') -- sh -c 'cat /run/secrets/additional/chart-admin-password'

Username = admin
PWD = AFfOaYWg8iyfNM6j9ZtbF3

accessing jenkins
externalip:8080




# Create service account for ci cd artifact
gcloud iam service-accounts create github-actions-service-account \
 --description="A service account for use in a GitHub Actions workflow" \
 --display-name="GitHub Actions service account."


### adding permission to service account
gcloud artifacts repositories add-iam-policy-binding ericsson \
  --location=europe-north2 \
  --role=roles/artifactregistry.createOnPushWriter \
  --member=serviceAccount:github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com

### Create a workload identity pool
gcloud iam workload-identity-pools create "flask-app-dev-pool" \
  --project=ericsson-project-465613 \
  --location=global \
  --display-name="Identity pool for my flask app"


### Create a workload identity pool provider
gcloud iam workload-identity-pools providers create-oidc "github-actions-provider" \
  --location="global" \
  --workload-identity-pool="flask-app-dev-pool" \
  --display-name="Provider for GitHub Actions" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="attribute.repository_owner=='ManasTota' && attribute.repository=='graduate_assessment'"

### describing identity pool
gcloud iam workload-identity-pools providers describe github-actions-provider \
  --location=global \
  --workload-identity-pool="flask-app-dev-pool"

output:
name: projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool/providers/github-actions-provider

### grant the Service Account Token Creator via a gmail
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountTokenCreator \
  --member=user:nantota87@gmail.com

### describing pool
gcloud iam workload-identity-pools describe "flask-app-dev-pool" \
  --location=global

output:
name: projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool

### exporting as env
export WIP_POOL=projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool


### binding
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-service-account@ericsson-project-465613.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member=principalSet://iam.googleapis.com/${WIP_POOL}/attribute.repository/ManasTota/graduate_assessment


### updating oidc for final check
gcloud iam workload-identity-pools providers update-oidc \
  github-actions-provider \
  --project=ericsson-project-465613 \
  --location=global \
  --workload-identity-pool=flask-app-dev-pool \
  --attribute-condition="assertion.repository_owner == 'ManasTota'"

Output:
name: projects/1086847771245/locations/global/workloadIdentityPools/flask-app-dev-pool/providers/github-actions-provider/operations/bigar7h2zxbqmehy7hzm2aq000000000