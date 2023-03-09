<center><img src="https://raw.githubusercontent.com/colav/colav.github.io/master/img/Logo.png"/></center>

# HunabKu  
Modular APIs creation using plugins system/  Maya - father of all gods

# Description
Package to create APIs endpoints using flask behind.
The package is handling the endpoints  using a customized plugin system designed by us.

# Plugin
Take a look on plugins examples in the repository
https://github.com/colav/HunabKu_plugins 

# Installation

## Dependencies
* Install nodejs >=10.x.x ex: 10.13.0
    * Debian based system: `apt-get install nodejs`
    * Redhat based system: `yum install nodejs`
    * Conda: `conda install nodejs==10.13.0`
* Install Apidocjs `npm install -g apidoc` as root!
* The other dependecies can be installed with pip installing this package.

NOTE:

To start mongodb server on conda please run the next steps

`
mkdir -p $HOME/data/db 
`

`
mongodb mongod --dbpath $HOME/data/db/
`

## Package
`pip install hunabku`

# Usage

Let's start creating a config file
```.sh
hunabku_server --generate_config config.py --overwrite
```

Let's start the server executing
```.sh
hunabku_server --config config.py
```


you can access to the apidoc documentation for the endpoints for example on: http://127.0.1.1:8888/apidoc/index.html

if depends of the ip and port that you are providing to hunabku.


# License
BSD-3-Clause License 

# Links
http://colav.udea.edu.co/



