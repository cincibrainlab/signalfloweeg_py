docker run -it --rm -p 10314:8888 --user root -e GRANT_SUDO=yes -v /cblstore/srv:/srv quay.io/jupyter/datascience-notebook:2024-03-14