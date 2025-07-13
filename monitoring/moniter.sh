#!/bin/bash

# Configurable thresholds
CPU_THRESHOLD=80
MEM_THRESHOLD=80

# Namespace and pod name
NAMESPACE="default"
POD_NAME=$1

if [ -z "$POD_NAME" ]; then
  echo "Usage: $0 <pod-name>"
  exit 1
fi

echo "Checking resource usage for pod: $POD_NAME"

# Fetch usage
# USAGE=$(kubectl top pod $POD_NAME --no-headers)
USAGE=$(kubectl top pod $POD_NAME -n $NAMESPACE --no-headers)

if [ $? -ne 0 ]; then
  echo "Error: Could not retrieve pod metrics. Is metrics-server running?"
  exit 1
fi

CPU_USAGE=$(echo $USAGE | awk '{print $2}' | sed 's/m//')
MEM_USAGE=$(echo $USAGE | awk '{print $3}' | sed 's/Mi//')

if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
  echo "⚠️ CPU usage alert for $POD_NAME: ${CPU_USAGE}m exceeds ${CPU_THRESHOLD}m"
fi

if [ "$MEM_USAGE" -gt "$MEM_THRESHOLD" ]; then
  echo "⚠️ Memory usage alert for $POD_NAME: ${MEM_USAGE}Mi exceeds ${MEM_THRESHOLD}Mi"
fi

echo "✅ Monitoring completed."
