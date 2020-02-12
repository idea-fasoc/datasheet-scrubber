
# Repo for FASOC CRUD, Express and MongoDB

Please note that this repo contains the source code for the **Fasoc web application**
The web application lists some of the components that are stored in a MongoDB cluster hosted on a cloud solution. 
The web application enables a full text search and a filter mechanism for some preperties of the components.

To request an access to the cloud cluster with more than 500k components please submit an inquiry to [Admin](zinebbe@umich.edu) as the access is on invitation only.

To access the web application please visit the link [here](http://fasoc.herokuapp.com/)


For Developpement purposes, please follow the instructions below.

## Installation

1. Install nodejs package as explained [here](https://nodejs.org/en/download/).

In order to make sure the installation has been done successfully please open up a terminal and run
```
  node --version 
```

2. Install dependencies.

Make sure you are in the src/Web-app-db directory.
```
  npm install 
```

## Usage 

1. run the application on the local server.
```
  npm run dev 
```

2. Open a browser and navigate to `localhost:3000`.
