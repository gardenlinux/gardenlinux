#!/bin/bash

BASE_DIR="$(dirname "$(which "$0")")"

sudo apt-get update
xargs sudo apt-get install -y < "$BASE_DIR"/deps.list


# --  Install Docker
# add dockers official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg


# setup stable docker repo
echo \
	  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
	    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

# Run docker without sudo
sudo groupadd docker
sudo usermod -aG docker "$USER"

