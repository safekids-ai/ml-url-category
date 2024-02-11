#!/bin/bash

# Initialize flags
DOWNLOAD_RAW_DATA=false
DOWNLOAD_LARGE_MODEL=false

# Check for flags
for arg in "$@"
do
    if [[ "$arg" == "--parsed-data" ]]; then
        DOWNLOAD_RAW_DATA=true
    elif [[ "$arg" == "--large-model" ]]; then
        DOWNLOAD_LARGE_MODEL=true
    fi
done

# Define your S3 bucket URL without the "https://" prefix
BUCKET="ml-url-category-safekids-ai-large-files"

# Define key-folder pairs for directories and individual files to download
declare -A KEY_FOLDER_MAP=(
  ["tiny_model/"]="web_app/tiny_model/"
  ["mariadb_data.csv"]="web_app/database/data/mariadb_data.csv"
  ["parsed_data/"]="parsed_data/"
  ["large_model/"]="modeling/large_model/"
)

# Optionally, define keys to skip when not downloading everything
SKIP_KEYS=("parsed_data/")

# Add large_model/ to skip keys if DOWNLOAD_LARGE_MODEL is false
if [ "$DOWNLOAD_LARGE_MODEL" = false ]; then
    SKIP_KEYS+=("large_model/")
fi

# Iterate over the key-folder map to download each specified folder or file
for KEY in "${!KEY_FOLDER_MAP[@]}"; do
  # Skip certain downloads if not downloading everything and it's in the skip list
  if { [ "$DOWNLOAD_RAW_DATA" = false ] && [[ " ${SKIP_KEYS[@]} " =~ " ${KEY} " ]]; } || { [ "$DOWNLOAD_LARGE_MODEL" = false ] && [[ " ${KEY} " == " large_model/ " ]]; }; then
    echo "Skipping $KEY due to not downloading everything and it's in the skip list."
    continue
  fi
  LOCAL_PATH="${KEY_FOLDER_MAP[$KEY]}"
  
  # Check if the key ends with a slash '/' indicating it's a directory
  if [[ "$KEY" == */ ]]; then
    # It's a directory, adjust key to remove the trailing slash for naming consistency in s3 sync
    DIR_KEY=${KEY%/}
    # Ensure the local directory exists
    mkdir -p "$LOCAL_PATH"
    # Download the directory
    echo "Syncing directory $DIR_KEY to $LOCAL_PATH"
    aws s3 sync "s3://$BUCKET/$DIR_KEY" "$LOCAL_PATH" --no-sign-request
  else
    # It's a file
    # Ensure the local directory for the file exists
    mkdir -p "$(dirname "$LOCAL_PATH")"
    # Download the file
    echo "Copying file $KEY to $LOCAL_PATH"
    aws s3 cp "s3://$BUCKET/$KEY" "$LOCAL_PATH" --no-sign-request
  fi
done

echo "All specified files and directories have been downloaded."
