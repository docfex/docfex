# Prepare Elasticsearch
Docfex uses the ingest attachemnt plugin for Elasticsearch.
Per default, the plugin is not included in the docker image of Elasticsearch.
For that I have created a simple Dockerfile that installs the plugin.
The image can be found at [DockerHub/manuelhatzl](https://cloud.docker.com/repository/docker/manuelhatzl/elasticsearch_ingestattachment).

# Prepare Host
Depending on the OS you want to run docker-elasticsearch
, you need to make changes as described in [Install Elasticsearch with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

## Save elasticsearch data
To save data over a container restart, a directory on the host must be created
and then defined either when using *docker run* or inside the *docker-compose.yml* file.
