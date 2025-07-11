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