#!/bin/bash
app="docker.analyzer"
docker build -t ${app} .
docker run -d -p 8007:80 \
  --name=${app} \
  -v $PWD:/ ${app}
