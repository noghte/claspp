#!/bin/bash

source_directory="./src/lib/weblogos/eps"
output_directory="./src/lib/weblogos/png"

# Create the output directory if it doesn't exist
mkdir -p "$output_directory"

# Loop through all .eps files in the source directory
for file in "$source_directory"/*.eps; do
    # Get the file name without the extension
    filename=$(basename "$file" .eps)

    # Convert the EPS file to PNG with increased quality
    convert -density 300 "$file" -quality 90 "$output_directory/$filename.png"
done
