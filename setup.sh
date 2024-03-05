#!/bin/bash

DOWNLOAD_RAW_DATA=$([[ "$1" == "--parsed-data" ]] && echo true || echo false)

BUCKET="safekids-ml/Url-Categorizer"

declare -A KEY_FOLDER_MAP=(
  ["model/"]="web_app/model_binary/"
  ["url-database/"]="web_app/database/data/"
#  ["training-data/"]="parsed_data/"
)

SKIP_KEYS=("parsed_data/")

# Iterate over the key-folder map to download each specified folder or file
for KEY in "${!KEY_FOLDER_MAP[@]}"; do
  # Skip downloading parsed data if flag is false and key is in the skip list
  if ! $DOWNLOAD_RAW_DATA && [[ " ${SKIP_KEYS[@]} " =~ " ${KEY} " ]]; then
    echo "Skipping $KEY due to flag setting."
    continue
  fi
  LOCAL_PATH="${KEY_FOLDER_MAP[$KEY]}"
  
  # Check if the key ends with a slash '/' indicating it's a directory
  if [[ "$KEY" == */ ]]; then
    # Ensure the local directory exists and download the directory
    mkdir -p "$LOCAL_PATH"
    echo "Syncing directory ${KEY%/} to $LOCAL_PATH"
    aws s3 sync "s3://$BUCKET/${KEY%/}" "$LOCAL_PATH" --no-sign-request --endpoint=https://nyc3.digitaloceanspaces.com
  else
    # Ensure the local directory for the file exists and download the file
    mkdir -p "$(dirname "$LOCAL_PATH")"
    echo "Copying file $KEY to $LOCAL_PATH"
    aws s3 cp "s3://$BUCKET/$KEY" "$LOCAL_PATH" --no-sign-request --endpoint=https://nyc3.digitaloceanspaces.com
  fi
done

echo "All specified files and directories have been downloaded."
