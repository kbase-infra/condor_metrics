#!/bin/bash
required_env_vars=("CONDOR_HOST" "SCHEDD_HOST" "COLLECTOR_HOST")

# Check for missing environment variables
for env_var in "${required_env_vars[@]}"; do
    if [[ -z "${!env_var}" ]]; then
        echo "Missing environment variable: $env_var"
        exit 1
    fi
done

# Write to condor_config
config_file="/etc/condor/condor_config"
echo "Creating $config_file"
> "$config_file" # Empty the file before writing
for env_var in "${required_env_vars[@]}"; do
    echo "$env_var = ${!env_var}" >> "$config_file"
done
echo "SEC_PASSWORD_FILE = /etc/condor/password" >> "$config_file"
echo "SEC_CLIENT_AUTHENTICATION_METHODS = PASSWORD" >> "$config_file"

# Use condor_store_cred if POOL_PASSWORD is set
if [[ -n "$POOL_PASSWORD" ]]; then
    condor_store_cred add -f /etc/condor/password -p "$POOL_PASSWORD"
fi

# FastAPI recommends running a single process service per docker container instance as below,
# and scaling via adding more containers. If we need to run multiple processes, use guvicorn as
# a process manager as described in the FastAPI docs
PYTHONPATH=src poetry run uvicorn --host 0.0.0.0 --port 5000 --factory factory:create_app