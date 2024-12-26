# <%= baseName %> prototype

This is a fastapi prototype generated using WeDAA, you can find documentation and help at [WeDAA Docs](https://www.wedaa.tech/docs/introduction/what-is-wedaa/)

## Prerequisites

- python version >= 3
<%_ if (auth && eureka) { _%>
- For Keycloak to work with Service Discovery in local(docker) environment, following line must be added to your hosts file `/etc/hosts`
  ```
  127.0.0.1	keycloak
  ```
<%_ } _%>

## Project Structure


<%_ if (auth || eureka || postgresql || mongodb || rabbitmq) { _%>
## Dependencies

This application is configured to work with external component(s).

Docker compose files are provided for the same to get started quickly.

Component details:
<%_ if (auth) { _%>
- Keycloak as Identity Management: `docker compose -f docker/keycloak.yml up -d`
- Open [http://localhost:9080](Keycloak Administration Console) to view it in your browser.
- Default Username: `admin`, Password: `admin`. 
<%_ } _%>
<%_ if (eureka) { _%>
- Eureka Service Discovery: `docker compose -f docker/jhipster-registry.yml up -d`
- Open [http://localhost:8761](Eureka Service Discovery) to view it in your browser.
- Default Username: `admin`, Password: `admin`. 
<%_ } _%>
<%_ if (postgresql) { _%>
- Postgresql DB: `docker compose -f docker/postgresql.yml up -d`
<%_ } _%>
<%_ if (mongodb) { _%>
- mongoDB: `docker compose -f docker/mongodb.yml up -d`
<%_ } _%>
<%_ if (rabbitmq) { _%>
- RabbitMQ message broker: `docker compose -f docker/rabbitmq.yml up -d`
<%_ } _%>

On launch, <%= baseName %> will refuse to start if it is not able to connect to any of the above component(s).
<%_ } _%>


## Get Started

Run the `./start.sh` script to quickly get started.

Or 

Manually Step: 

1. Create a new virtual env
```
python -m venv .venv
```

2. Activate the virtual environment
```
for mac/linux : source .venv/bin/activate
for windows : .venv\Scripts\activate
```

3. Install the requirements for project
```
pip install -r requirements.txt
```

4. Enter the `app/` directory, Run the FastAPI application: 
```
gunicorn -c gunicorn_dev_config.py main:app
```


Open [http://localhost:<%= serverPort %>/management/health/readiness](http://localhost:<%= serverPort %>/management/health/readiness) to view it in your browser.

## Containerization

Build the docker image: `docker build -t <%= baseName %>:latest .`

Start the container: `docker run -d -p <%= serverPort %>:<%= serverPort %> <%= baseName %>:latest`

<%_ if ( restServer?.length > 0 || rabbitmqClient?.length > 0 ){ _%>
## Communication
Refer [COMMUNICATION.md](./COMMUNICATION.md)
<%_ } _%>
