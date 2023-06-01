# Use base-notebook to build our image on top of it
# See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/running.html
FROM jupyter/base-notebook:2023-04-03

LABEL Andrey Eremin <dsoft88@gmail.com>

# Install necessary libraries
COPY requirements.txt ./
RUN echo 'Install additional python libraries...' && pip install -r ./requirements.txt    

USER $NB_UID