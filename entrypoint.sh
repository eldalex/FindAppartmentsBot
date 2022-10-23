#!/usr/bin/env bash

# create /var/log/auth.log if not exist
if [[ ! -f /var/log/auth.log ]]
then
    touch /var/log/auth.log
fi

# start ssh service
service ssh start

# sleep forever
#sleep infinity

# link auth.log to container log
python3 $APP_HOME/HelperFindAppatrmentsBot.py
#python3 $APP_HOME/main.py
