#!/bin/bash

# Check if DS_URL value is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 DS_URL"
    exit 1
fi

new_ds_url=$1

# Update DS_URL value in the configmap file
sed -i "s|DS_URL:.*|DS_URL: \"$new_ds_url\"|g" ./k8s/configmap.yaml

# Calculate the hash of the updated configmap file
content_hash=$(sha256sum ./k8s/configmap.yaml | awk '{ print $1 }')

# Truncate the hash to the first 10 characters
truncated_hash=${content_hash:0:10}

# Define the base names
base_deployment_name="gabrielduarte-recommender-deployment"
base_job_name="gabrielduarte-recommender-job"

# Ensure the total name length does not exceed 63 characters
max_base_name_length=$((63 - ${#truncated_hash} - 1)) # Subtract 1 for the hyphen
if [ ${#base_deployment_name} -gt $max_base_name_length ]; then
  base_deployment_name=${base_deployment_name:0:$max_base_name_length}
fi
if [ ${#base_job_name} -gt $max_base_name_length ]; then
  base_job_name=${base_job_name:0:$max_base_name_length}
fi

# Update the names in the deployment and job files
sed -i "s|name: $base_deployment_name|name: $base_deployment_name-$truncated_hash|g" ./k8s/deployment.yaml
sed -i "s|name: $base_job_name|name: $base_job_name-$truncated_hash|g" ./k8s/job.yaml

# Push changes to github
git add .
git commit -m "Changed playlists dataset to $new_ds_url"
git push -u origin master