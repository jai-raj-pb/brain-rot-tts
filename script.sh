
#!/bin/bash
# Set S3 bucket name and prefix
BUCKET_NAME="mt-picasso-us-east"
PREFIX="1069834390334531305/"
# Local directory where files will be downloaded
LOCAL_DIR="s3_downloads"
# Maximum number of files to download
LIMIT=2
COUNT=0
# Create local directory if it doesn't exist
mkdir -p "\$LOCAL_DIR"
# List files matching "final_tran" and download them
aws s3 ls "s3://\$BUCKET_NAME/\$PREFIX" --recursive | grep "final_tran" | awk '{print \$4}' | while read -r FILE_PATH; do
    if [ "\$COUNT" -ge "\$LIMIT" ]; then
        echo "Download limit reached (\$LIMIT files)."
        break
    fi
    # Extract the file extension (e.g., .json, .pdf)
    EXTENSION="\${FILE_PATH##*.}"
    
    # Set a unique filename using count
    NEW_FILENAME="final_transcription_\$((COUNT + 1)).\$EXTENSION"
    echo "Downloading: \$FILE_PATH as \$NEW_FILENAME"
    aws s3 cp "s3://\$BUCKET_NAME/\$FILE_PATH" "\$LOCAL_DIR/\$NEW_FILENAME"
    
    COUNT=\$((COUNT + 1))
done
echo "Download complete! Files saved in: \$LOCAL_DIR"
EOF