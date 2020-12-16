#!/bin/bash

python /s/init_service.py >> /tmp/init_service.log
nohup python /s/loop_service.py  >> /tmp/loop_service.log 2>&1 &
/usr/bin/tensorflow_model_server --rest_api_port=8080 --port=8081 --model_config_file=/s/model_server_config