  
from flask_pymongo import PyMongo

# Setup MongoDB here
uri="mongodb://admin:admin@firstcluster-shard-00-00-nrj8x.mongodb.net:27017,firstcluster-shard-00-01-nrj8x.mongodb.net:27017,firstcluster-shard-00-02-nrj8x.mongodb.net:27017/<dbname>?ssl=true&replicaSet=Firstcluster-shard-0&authSource=admin&retryWrites=true&w=majority"
dbs = {
    "user": "Users",
}
collections = {
    "github": "github",
}