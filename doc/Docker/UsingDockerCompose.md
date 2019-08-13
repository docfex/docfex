# Setting up Docfex using docker-compose
Docfex can be started using the [docker-compose.yml](../../docker-compose.yml) file in the root directory.
This file is based on the Elasticsearch *docker-compose.yml* file from their installation instructions found [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

## Docker networking
For docfex to be able to communicate with Elasticsearch and Redis, a docker network called *docfex-net* is defined. This allows all containers to communicate.

**Note:** es_hosts list inside *config.py* must include containernames defined for the Elasticsearch containers (*elastic* and *elastic2* in this example). Otherwise docfex can't connect to Elasticsearch.

For more info on docker networking, see [Docker Networking](https://docs.docker.com/network/)

## Changes to the Elasticsearch services
Instead of the base Elasticsearch images, a docker image of Elasticsearch must be used where the ingest attachment plugin is installed.
In this docker-compose file, the image from [manuelhatzl/elasticsearch_ingestattachment](https://cloud.docker.com/u/manuelhatzl/repository/docker/manuelhatzl/elasticsearch_ingestattachment) gets used.

Since docfex should be able to handle big pdfs, the environment settings for Elasticsearch were also increased.
For that, the heap size was increased by changing the JVM options *-Xms* and *-Xmx* from 512 MB to 2 GB respectively. 
Additionally, also the maximal http content lenght was increased to 1700 MB to be able to send large files.

**Note:** Per default, both Elasticsearch services store their values in docker volumes.
If this is not wanted, you must change the service volumes for both services to bind mount.
An example of a bind mount can be seen in the docfex service.

**Note:** For large pdf files (>100 MB), or a directory with many documents, a heap size of 2 GB is probably not sufficient anymore.
Docfex was tested with around 1000 pdfs with pdfs up to 500 MB of size. In this case, the heap size had to be increased to 10 GB.
(This was tested on a single node!) 

## Configuring the Redis service
As described in [UsingContainers.md](UsingContainers.md), Redis is used as session interface for Flask.
For that, a Redis service must be added that has access to the docfex-net network. The URL to the Redis service must be set in *config.py*, otherwise Flask can't store session informations.

## Configuring the Docfex service
Docfex is the service that runs the Flask part and synchronises Elasticsearch with the given base path on the OS.
As it depends on Elasticsearch and Redis to be available, the container will be started after both Elasticsearch containers and Redis are running.

**Note:** As described in the docker-compose reference documentation [here](https://docs.docker.com/compose/compose-file/)
, *depend_on* is not waiting for a program inside a container to be ready, so docfex will return connection errors at first!

### Docfex volumes
There are two volumes you need to define for the docfex service.

1. /opt/docfex/src/config
</br>
This volume is used to configure docfex. For that, place a *config.py* file inside the directory that is mounted to this volume.
An example of such a config file can be found under [src/config/config.py.example](/src/config/config.py.example).

1. /mnt/basepath
</br>
Mount the directory you want to be searched by docfex here.

### Connecting to docfex
After starting docker-compose using
```
sudo docker-compose up
```
docfex should be reachable at the port specied in *config.py* and *docker-compose.yml*. For example at [localhost:5000](http://localhost:5000).

**Note:** The port defined in *config.py* and *docker-compose.py* must match!

**Note:** The first time docfex starts, it synchronises the whole base path with Elasticsearch. This can take several minutes, so you might see no documents on the webpage!


## Finishing up
When docfex finished synchronizing and all docuemnts can be viewed, you can rerun docker-compose to serve docfex as a daemon service using
```
sudo docker-compose up -d
```

## Facing errors
Running docker-compose without -d will print all logs to the terminal, so you can see what errors are returned.

See docfex [Gituhub page](https://github.com/docfex/docfex) for known issues.
For docker related issues, checkout dockers [user manuels](https://docs.docker.com/compose/compose-file/)
Since docfex uses Flask and Elasticsearch in the back, there is a good chance to find help on [Stackoverflow](https://stackoverflow.com/) or similar.

