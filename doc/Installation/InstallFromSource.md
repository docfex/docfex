# Installing docfex from source
Docfex requires a Elasticsearch database to be reachable. You can define the connection to Elastic inside [config.py](/src/config/config.py.example). Since private credentials are stored inside config.py you need to create it yourself. A template is given as [config.py.example](/src/config/config.py.example).

**Note:** Makre sure Elasticsearch is reachable before starting docfex.

**Note:** When installing docfex from source, you need to have at least python **3.7.1** installed!
Otherwise you won't be able to run it!

**Note** You might want to setup a python environment to install those packages.
When using VScode, make sure to name the environment .venv for automatic detection.

(Optional) Run the following command to setup the python environment.
```
python -m venv .venv
```

With python >=3.7.1, install all packages defined under [requirements.txt](/requirements.txt) using
```
pip install -r requirements.txt
```
After all packages have been installed, run
```
python main.py
```
This starts docfex according to the settings defined inside *config.py*.
At first, docfex will index all documents found in the directory that was defined inside *config.py*.
After all documents have been indexed, open a webbrowser and go the address you defined inside *config.py* (per default this is [localhost:5000](http://localhost:5000)).


## Facing errors
If docfex returns with an error, make sure your settings inside *config.py* are correct and Elastic is running. If everything looks good, check out the following links for more help.

See docfex [Gituhub page](https://github.com/docfex/docfex) for known issues.
Since docfex uses Flask and Elasticsearch in the back, there is a good chance to find help on [Stackoverflow](https://stackoverflow.com/) or similar.

