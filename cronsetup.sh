sudo crontab -l > jobs.txt

sudo echo "*/1 * * * * /usr/bin/python3 `pwd`/unms-ros-sync-0.0.1/main_ucrm.py >> `pwd`/log/unms-crm.log 2>&1" >> jobs.txt

sudo crontab jobs.txt