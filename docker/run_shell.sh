#!/bin/bash

# original: quay.io/jupyter/datascience-notebook:latest \

docker run \
  -v /Users/ernie/Documents:/home/jovyan/srv \
  -e DISPLAY="host.docker.internal:0" \
  -e GRANT_SUDO=yes \
  -p 13500:8888 \
  --user root \
  -it \
  --rm \
  --name signalfloweeg-jdatascience \
  ghcr.io/cincibrainlab/signalfloweeg-jdatascience:latest /bin/bash


