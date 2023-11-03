#!/bin/bash

ensure_gdown_installed() {
  if ! command -v gdown &> /dev/null; then
    echo "gdown could not be found, attempting to install it."
    pip install gdown || (echo "Failed to install gdown. Please install it manually." && exit 1)
  else
    echo "gdown is already installed."
  fi
}

ensure_gdown_installed

declare -A files_and_paths
# files_and_paths["urls_link"]="./model_data/5m_urls.json"
# files_and_paths["urls_with_cat_link"]="./model_data/5m_url_category.json"
files_and_paths["/content/drive/MyDrive/model_data/data/quantized/model.onnx"]="./model_binary/model.onnx"

download_from_drive() {
    local file_id="$1"
    local destination_path="$2"
    gdown --id "$file_id" --output "$destination_path"
}

for file_id in "${!files_and_paths[@]}"; do
    download_from_drive "$file_id" "${files_and_paths[$file_id]}"
done

echo "All files have been downloaded."