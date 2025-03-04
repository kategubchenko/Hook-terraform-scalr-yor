#!/usr/bin/env bash
set -e
pip3 install requests click --quiet

export YOR_SIMPLE_TAGS="$(python3 $SCALR_HOOK_DIR/scripts.py get-tags -h $SCALR_HOSTNAME -t $SCALR_TOKEN -r $SCALR_RUN_ID -d $TAG_DELIMITER)"
echo $YOR_SIMPLE_TAGS
# wget https://github.com/bridgecrewio/yor/releases/download/0.1.150/yor_0.1.150_linux_amd64.tar.gz -q
# tar -xvf yor_0.1.150_linux_amd64.tar.gz
# ./yor tag --tag-groups simple -d ./ --skip-tags git*
