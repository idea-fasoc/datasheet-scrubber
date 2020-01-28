# Database

Our Database content was exported into a json file accessible using the following [link](https://umich.box.com/s/gmybk8xu1htec9w3z4vse86vtotws22r).


# How to create a local MongoDB instance from a JSON file
**What’s MongoDB?**

MongoDB is a document database which belongs to a family of databases called NoSQL - not only SQL. In MongoDB, records are documents which behave a lot like JSON objects in JavaScript. Values in documents can be looked up by their field’s key. Documents can have some fields/keys and not others, which makes Mongo extremely flexible.


### Homebrew

Homebrew is a package manager for the Mac\Linux – it makes installing most open source software (like MongoDB) as simple as writing brew install mongodb.
Follow the instructions in the How to Install Homebrew on a Mac instruction guide.


### Install and Run MongoDB with Homebrew
```
brew update
brew install mongodb
mkdir -p /data/db
sudo chown -R `id -un` /data/db
# Enter your password
mongod
```

=> This should start the Mongo server.

### Import data into MongoDB

If the imported file is *digikey.json* (or replace with path if in a different folder)

```
mongoimport ––host localhost:27017 ––db mydb ––collection docs digikey.json
```

In this example, *mydb* is the name of the database and *docs* is the name of the collection into which the data will be inserted.  
Note that *localhost:27017* is the default server and port for MongoDB.


To confirm that the records are now in MongoDB, do the following.

1. Start the Mongo shell by running `mongo`.

2. Issue a `show dbs` command to see the available databases.  *mydb* should be listed.

3. Issue a `use mydb` command to switch to the *mydb* database.

4. Issue a `show collections` command to see the collections in the database.  *docs* should be listed.

5. Issue a `db.docs.find()` command to see the records in the “docs” collection.  The first twenty records will be returned.  Type “it” to see additional records.

# Compass GUI for MongoDB

To visually explore, query and interact with the data, it is recommended to use [Compass](https://www.mongodb.com/download-center/compass).

Please contact [admin](zinebbe@umich.edu) for any question or concern related to this note.
