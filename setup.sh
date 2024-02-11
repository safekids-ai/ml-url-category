#!/bin/bash

# Initialize download flag
DOWNLOAD_ALL=false

# Check for "--rawdata true" flag
if [[ "$1" == "--parsed-data" && "$2" == "true" ]]; then
  DOWNLOAD_ALL=true
fi

# Define your S3 bucket URL
BUCKET_URL="https://ml-url-category-safekids-ai-large-files.s3.amazonaws.com"

# Define key-file pairs
declare -A KEY_FILE_MAP=(
  ["mariadb_data.csv"]="web_app/database/data"
  ["tiny_model"]="web_app/tiny_model"
  ["parsed_data"]="parsed_data/"
  ["large_model"]="modeling/large_model"
)

# Optionally, define keys to skip when not downloading everything
SKIP_KEYS=("s3-key-path-2")

# Iterate over the key-file map and download each file
for KEY in "${!KEY_FILE_MAP[@]}"; do
  # Skip certain downloads if not downloading everything
  if [ "$DOWNLOAD_ALL" = false ] && [[ " ${SKIP_KEYS[@]} " =~ " ${KEY} " ]]; then
    echo "Skipping $KEY"
    continue
  fi
  FILE="${KEY_FILE_MAP[$KEY]}"
  # Create directory if it doesn't exist
  mkdir -p "$(dirname "$FILE")"
  # Download the file
  echo "Downloading $KEY to $FILE"
  curl "${BUCKET_URL}/${KEY}" -o "$FILE"
done

echo "All files have been downloaded."