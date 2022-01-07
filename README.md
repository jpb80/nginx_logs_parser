# Nginx Logs Parser
## About
Parses nginx log file to dictionary objects using Grok pattern matching.  Run tests that record the number of occurrences of remote ip addresses and identify the remote addresses
that belong to specified subnets.

## Pre-requisites for building image
- Install python3.9 & pip
- Install Docker
- (optional) Install python virutalenv in the app directory `python -m venv venv`
- (optional) Activate python venv `. venv/bin/activate`
- Install the requirements.txt dependecies.  `pip install -r requirements.txt`

## Building image
`docker build . -t nginx-log-parser`

## Running container
### Default Enviornment variables
`docker run -it -d -p 8080:8080 -v "$(pwd)"/nginx_logs:/app/nginx_logs --env-file env nginx-log-parser`

### Environment file
Environment variables for nginx log location and subnets to check. If log location env is changed then the docker volume mount location will need updated.
The nginx application uses these environment variables upon start.

#### Debug Mode
Enviornment variable LOGLEVEL indicated by an integer.
20=INFO
10=DEBUG

Set the variable LOGLEVEL=10 then start the container.
View logs by using `docker logs <containerId>`.

## Running the application
Make a get request to the api endpoint such as `curl localhost:8080/`.
Api returns a json of 'buckets' of subnets occurrences and 'remote_addresses_occurrences'.
