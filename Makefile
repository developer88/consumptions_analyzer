# See command line arguments for Jupyter https://jupyter-notebook.readthedocs.io/en/stable/config.html?highlight=no-browser#options
#   and how to use jupyter docker image https://jupyter-docker-stacks.readthedocs.io/en/latest/using/running.html
run:
	docker build ./ -t consumptions_analyzer
	docker run -it -p 8899:8888 -v "${PWD}":/home/jovyan/work consumptions_analyzer  start.sh jupyter notebook --NotebookApp.token='' ./work/Consumption.ipynb