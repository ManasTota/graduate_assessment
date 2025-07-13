import requests
import json
import sys

POD_NAME = sys.argv[1] if len(sys.argv) > 1 else ""
PROMETHEUS_URL = "http://localhost:9090"

if not POD_NAME:
    print("Usage: python3 prometheus_query.py <pod-name>")
    sys.exit(1)

# PromQL queries
cpu_query = f'rate(container_cpu_usage_seconds_total{{pod="{POD_NAME}", container!=""}}[1m])'
mem_query = f'container_memory_usage_bytes{{pod="{POD_NAME}", container!=""}}'


def run_query(query):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query", params={'query': query})
    response.raise_for_status()
    return response.json()["data"]["result"]


try:
    cpu_results = run_query(cpu_query)
    mem_results = run_query(mem_query)

    # Use only the first CPU sample for this pod
    if cpu_results:
        cpu = cpu_results[0]
        pod = cpu["metric"].get("pod", POD_NAME)
        namespace = cpu["metric"].get("namespace", "default")
        container_name = cpu["metric"].get("container", "")

        cpu_value = float(cpu["value"][1])

        # Find memory value from matching container
        mem_value = 0.0
        for mem in mem_results:
            if mem["metric"].get("container") == container_name:
                mem_value = float(mem["value"][1])
                break

        result = [{
            "namespace": namespace,
            "pod": pod,
            "cpu_usage_cores": round(cpu_value, 8),
            "memory_usage_bytes": round(mem_value, 2)
        }]
        print(json.dumps(result, indent=2))
    else:
        print(f"⚠️ No metrics found for pod '{POD_NAME}'.")

except Exception as e:
    print(f"❌ Error: {e}")
