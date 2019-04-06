# Setting up Docfex using docker containers
Docfex can be setup using two docker containers.
* One for Elasticsearch
* One for docfex/Flask

Since Elasticsearch is on a separate container, a connection must be setup so both containers can communicate.
For that a docker bridge network is used.

## 1. Setup the docker network
Create a new docker bridge network using
```
sudo docker network create --driver bridge docfex-net
```
**Note:** docfex-net in the example above is the name of the newly created network

Run the following command to make sure the network was created
```
sudo docker network ls
```
In the resulting list of networks, you should see **docfex-net**

## 2. Start the Elasticsearch container
Docfex needs the ingest attachment plugin for Elasticsearch, since Pdf and Markdown documents are stored in Elasticsearch. The official docker image of Elasticsearch doesn't ship with this plugin, so you need to use a image that does. This example uses the image from [manuelhatzl/elasticsearch_ingestattachment](https://cloud.docker.com/u/manuelhatzl/repository/docker/manuelhatzl/elasticsearch_ingestattachment). The image is based on Elasticsearch 6.7.1.

There are many different options on how to run the Elasticsearch docker image. Below is a simple one that creates a daemon container and connects to the previously generated network. To keep data over a container restart, a docker volume is mounted to */home/user/elastic* in which all Elasticsearch data will be saved.

```
sudo docker run -d -e "discovery.type=single-node" \
--name elastic --network docfex-net \
-v /home/user/elastic:/usr/share/elasticsearch/data \
manuelhatzl/elasticsearch_ingestattachment:6.7.1
```

**Note:** Depending on document sizes, you most definitely need to increase the heap size Elasticsearch can use. Checkout [Elasticsearch configuring the heap size](https://www.elastic.co/guide/en/elasticsearch/reference/current/heap-size.html) for more information.

## 3. Start the Docfex/Flask container
This container holds the main application. It synchronises the OS with Elasticsearch and serves the website using Flask.

**Note:** This container requires that the Elasticsearch container is up and Elasticsearch is running!

To create the docker image for Docfex, you can either create it yourself by using the main Dockerfile, or you can use the image under [manuelhatzl/docfex:latest](https://cloud.docker.com/repository/list)

The following command sets up a docker container as daemon providing port 5000 to the host. The previously created docker network is provided so docfex can connect to the elastic container. Since connection and port of Flask and Elasticsearch as well as the secret session key should/must be configurable, you must specify your own *config.py* file and place it in a folder that is mounted to */opt/docfex/src/config*.
An example of a possible *config.py* file can be found under [src/config/config.py.example](/src/config/config.py.example). The use of docfex is to parse a large directory, that can then be searched using Elasticsearch. As before with config.py, you can provide the mount point to the directory that will be parsed, by mounting it to */mnt/basepath*.

```
sudo docker run -d -p 5000:5000 --name docfex \
--network docfex-net \
-v /home/user/config:/opt/docfex/src/config -v /home/user/BigDirectory:/mnt/basepath \
manuelhatzl/docfex:latest
```

After that, you can verify that all containers are running using
```
sudo docker container ls
```

You can now access Docfex at [localhost:5000](http://localhost:5000).

**Note:** Docfex will first write all documents found in the directory to Elasticsearch. This can take a long time depending on the amount/size of documents, so you might not be able to load Docfex at first. Try again after several minutes.

## Facing problems
In case something went wrong on the way, you can try to read the logs of the two docker containers, using
```
sudo docker logs docfex
```

**Note:** Replace *docfex* with *elastic* to see the logs of the elastic container.
