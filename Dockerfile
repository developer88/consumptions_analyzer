# Use base-notebook to build our image on top of it
# See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/running.html
FROM jupyter/base-notebook

LABEL Andrey Eremin <dsoft88@gmail.com>

# Install necessary libraries
COPY requirements_docker.txt ./
RUN echo 'Install additional python libraries...' && pip install -r ./requirements_docker.txt    

USER $NB_UID
