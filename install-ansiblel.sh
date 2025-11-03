#!/bin/bash

# Update package lists
sudo apt update

# Install software-properties-common if not already present
# This package provides the add-apt-repository command
sudo apt install -y software-properties-common

# Add the Ansible PPA (Personal Package Archive)
sudo add-apt-repository --yes --update ppa:ansible/ansible

# Install Ansible
sudo apt install -y ansible

# Verify Ansible installation
ansible --version

echo "Ansible installation complete."

