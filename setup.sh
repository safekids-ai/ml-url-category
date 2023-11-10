#!/bin/bash

# Function to download a file from Google Drive
download_from_google_drive() {
    file_id=$1
    file_path=$2

    # Check if the file already exists
    if [ -f "$file_path" ]; then
        echo "File $file_path already exists, skipping download."
    else
        # Getting the confirmation token needed for large files
        confirm_token=$(curl -sL -c /tmp/cookies.txt "https://drive.google.com/uc?export=download&id=${file_id}" | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')

        # Downloading the file
        curl -Lb /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=${confirm_token}&id=${file_id}" -o ${file_path}

        # Cleaning up
        rm -rf /tmp/cookies.txt
        echo "Downloaded $file_path."
    fi
}

# Download files
download_from_google_drive "1-10_d96h__tLxTdkIk0fmkZdPyBEDWQp" "./model_binary/model.onnx"
download_from_google_drive "1r1rNR6lJRu_Wk3zQpQxoogS7o0u9FxJ1" "./model_binary/encoder.pkl"


echo "All file download attempts completed."
