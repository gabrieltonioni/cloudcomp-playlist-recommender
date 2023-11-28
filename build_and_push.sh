#!/bin/bash

# Check if the correct number of arguments was passed
if [ "$#" -ne 3 ]; then
    echo "Usage: ./build_and_push.sh image_name build_directory version_type"
    exit 1
fi

# Set the image name, build directory, and version type from the script arguments
image_name=$1
build_directory=$2
version_type=$3

# Get the current version from the Dockerfile
current_version=$(grep "ENV IMAGE_VERSION" $build_directory/Dockerfile | cut -d'=' -f2)

# Increment the version number
IFS='.' read -ra version_parts <<< "$current_version"
if [ "$version_type" == "major" ]; then
    ((version_parts[0]++))
elif [ "$version_type" == "minor" ]; then
    ((version_parts[1]++))
elif [ "$version_type" == "patch" ]; then
    ((version_parts[2]++))
else
    echo "Invalid version type. Please specify major, minor, or patch."
    exit 1
fi
new_version="${version_parts[0]}.${version_parts[1]}.${version_parts[2]}"

# Update the version in the Dockerfile
sed -i "s|ENV IMAGE_VERSION=$current_version|ENV IMAGE_VERSION=$new_version|" $build_directory/Dockerfile

# Build the Docker image
docker build -t $image_name:$new_version $build_directory

# Push the Docker image to the registry
docker push $image_name:$new_version

# Update the version in the corresponding yaml file based on the image name
if [ "$image_name" == "gabrieltonioni/rules-generator" ]; then
    sed -i "s|$image_name:$current_version|$image_name:$new_version|" ./k8s/job.yaml
    # Calculate the hash of the file content
    content_hash=$(sha256sum ./k8s/job.yaml | awk '{ print $1 }')
    # Truncate the hash to the first 10 characters
    truncated_hash=${content_hash:0:10}
    # Define the base job name
    base_job_name="gabrielduarte-recommender-job"
    # Ensure the total job name length does not exceed 63 characters
    max_base_job_name_length=$((63 - ${#truncated_hash} - 1)) # Subtract 1 for the hyphen
    if [ ${#base_job_name} -gt $max_base_job_name_length ]; then
    base_job_name=${base_job_name:0:$max_base_job_name_length}
    fi
    # Use sed to update the job name in the yaml file
    sed -i "s|name: $base_job_name-\?.*|name: $base_job_name-$truncated_hash|g" ./k8s/job.yaml
elif [ "$image_name" == "gabrieltonioni/playlists-recommender" ]; then
    sed -i "s|$image_name:$current_version|$image_name:$new_version|" ./k8s/deployment.yaml
fi

# Push changes to github
git add .
git commit -m "Bumped $image_name to $new_version"
git push -u origin master