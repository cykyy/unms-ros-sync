#!/bin/bash

sudo apt update

sudo apt install unzip

sudo apt install python3

sudo apt install python3-pip

pip3 install pyros_api

wget https://github.com/cykyy/unms-ros-sync/archive/v0.0.1.zip

sudo unzip v0.0.1.zip

# sudo crontab -l > jobs.txt
# sudo echo "*/1 * * * * /usr/bin/python3 `pwd`/unms-ros-sync-0.0.1/main_ucrm.py >> `pwd`/log/unms-crm.log 2>&1" >> jobs.txt
# sudo crontab jobs.txt