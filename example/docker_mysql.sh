#!/bin/bash

sudo docker run --name mysql -e MYSQL_ROOT_PASSWORD=secret -p 3306:3306 -d mysql:latest
