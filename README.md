# docfex
Docfex is a webexplorer that uses Elasticsearch to lookup documents for certain keywords and renders a simple explorer of supported file types.

Currently docfex supports pdf, markdown, video and audio documents. Pdf and markdown documents are indexed, so their content is also searchable. Video and audio documents can only be searched by name.

The backend is using python [Flask](http://flask.pocoo.org/) and [Elasticsearch-Dsl](https://elasticsearch-dsl.readthedocs.io/en/latest/). The frontend is built using [Bootstrap 4](https://getbootstrap.com/), so docfex can be viewed inside a browser at any typical resolution.


## Installation
Docfex needs access to a Elasticsearch database. If you already have one setup
, you can skip the part to setup Elasticsearch.

**Note:** Docfex will create indeces to store its document as soon as you start docfex!
Docfex synchronises Elastic with the OS, so deleting a document on the OS will also remove it in Elastic.


To install docfex, there are currently two major ways:

### 1. Using docker or docker-compose
To get docfex up and running, adapt [docker-compose.yml](./docker-compose.yml) to your needs and then run
```
sudo docker-compose up
```

**Note:** For more information on running docfex using *docker-compose*, see [using docker-compose](doc/Docker/UsingDockerCompose.md).

**Note:** Docfex can also be installed by simply creating an elastic and one docfex docker container.
For more on running docfex using docker containers, see [using docker containers](doc/Docker/UsingContainers.md).


### 2. Installing from source
For instructions on how to run/install docfex from source, go to [InstallFromSource](doc/Installation/InstallFromSource.md).


## Usage
After you have installed docfex and you can see the base directory inside your browser, you can start exploring the document tree, try searching for keywords either globally or local per file or folder, or you can manage docfex settings under [<your path to docfex>/Settings](http://localhost:5000/Settings).
On the settings page you can define if file contents are searched globally or just per sub directory and you can force docfex to update Elasticsearch.



## Contribution
If you like the concept of docfex, you can help by contributing, sharing or leaving feedback.
To contribute, checkout [CONTRIBUTION](CONTRIBUTION.md).

