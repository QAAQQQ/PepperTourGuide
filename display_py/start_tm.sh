#!/usr/bin/env sh

python3 webserver_ros.py&
cd web_server
erlc *.erl
escript server.beam

