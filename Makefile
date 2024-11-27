PROJECT_HOME_DIR := ${CURDIR}

build:
	# Build workflow using Docker image
	docker build -t workflow ${PROJECT_HOME_DIR}

run:
	# Run workflow using Docker image
	docker run --rm -it --name workflow -v ${PROJECT_HOME_DIR} workflow /bin/bash