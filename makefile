# Define variables for easier modification
PROJECT_ID := ericsson-project-465613
REGION := europe-north2
REPOSITORY := ericsson
IMAGE_NAME := flask-app
IMAGE_TAG := latest
FULL_IMAGE_NAME := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPOSITORY)/$(IMAGE_NAME):$(IMAGE_TAG)
ENV_FILE := flask_app/.env.deployment
SECRETS_NAME := app-secrets
DEPLOYMENT_FILE := k8s/deployment.yaml

.PHONY: all build tag push deploy create-secrets delete-secrets clean

all: build tag push deploy ## Builds, tags, pushes the Docker image, and applies the Kubernetes deployment

build: ## Builds the Docker image
	@echo "--- Building Docker image: $(IMAGE_NAME) ---"
	docker build -t $(IMAGE_NAME) .

tag: ## Tags the Docker image
	@echo "--- Tagging Docker image: $(FULL_IMAGE_NAME) ---"
	docker tag $(IMAGE_NAME) $(FULL_IMAGE_NAME)

push: ## Pushes the Docker image to the registry
	@echo "--- Pushing Docker image: $(FULL_IMAGE_NAME) ---"
	docker push $(FULL_IMAGE_NAME)

deploy: ## Applies the Kubernetes deployment
	@echo "--- Applying Kubernetes deployment: $(DEPLOYMENT_FILE) ---"
	kubectl apply -f $(DEPLOYMENT_FILE)

create-secrets: ## Creates Kubernetes secrets from the .env file
	@echo "--- Creating Kubernetes secret: $(SECRETS_NAME) from $(ENV_FILE) ---"
	kubectl create secret generic $(SECRETS_NAME) --from-env-file=$(ENV_FILE) --dry-run=client -o yaml | kubectl apply -f -

delete-secrets: ## Deletes Kubernetes secrets
	@echo "--- Deleting Kubernetes secret: $(SECRETS_NAME) ---"
	kubectl delete secret $(SECRETS_NAME)

clean: ## Deletes the Kubernetes deployment and secrets
	@echo "--- Deleting Kubernetes deployment: $(DEPLOYMENT_FILE) ---"
	kubectl delete -f $(DEPLOYMENT_FILE)
# 	$(MAKE) delete-secrets

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

