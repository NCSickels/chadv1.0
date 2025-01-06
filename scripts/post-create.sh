#!/bin/bash

# Install dependencies

pip install -r requirements.txt

# Check if alias already exists in .bashrc
if ! grep -q "alias ls --color=auto" ~/.bashrc; then
    echo "alias ls='ls --color=auto'" >> ~/.bashrc
fi

source ~/.bashrc