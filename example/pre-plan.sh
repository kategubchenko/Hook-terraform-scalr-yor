#!/usr/bin/env bash

pip3 install requests
pip3 install click

export YOR_SIMPLE_TAGS="$(python3 /scripts.py get-tags -h $SCALR_HOSTNAME -t $SCALR_TOKEN -r $SCALR_RUN_ID)"
wget https://github.com/bridgecrewio/yor/releases/download/0.1.150/yor_0.1.150_linux_amd64.tar.gz
tar -xvf yor_0.1.150_linux_amd64.tar.gz
./yor tag --tag-groups simple -d ./ --skip-tags git*