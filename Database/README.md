# Database

Our Database content was exported into a json file accessible using [link](https://umich.box.com/s/gmybk8xu1htec9w3z4vse86vtotws22r).



# How to collect data to create our Database?
We use web-scraping in order to collect detailed description of electronic componenets.
The data collected is scrapped from Digikey website using we-scraping libraries in Python.

### prerequisites
1. Use Chrome for the scraping process
2. Download chromedriver [here](https://chromedriver.chromium.org/downloads)
3. Install Selenium package following simple [instructions](https://selenium-python.readthedocs.io/installation.html)
4. Use Python version 3.5 or higher

### Steps

1. Generate 'links_and_type.csv' by running the following script:
```
python digikey_get_urls.py
```

It will be used to perform the next step of the scraping process.

2. Run web scraping script

```
python digikey_web_scraping.py
```
Please note that the script will take from few minutes to several hours depending on the number of components present in a given category.

3. populate your local DB with the files extracted

```
python populate_db_fron_csv.py
```

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

Run the following command
```
mongoimport ––host localhost:27017 ––db mydb ––collection docs digikey.json
```

In this example, *digikey.json* is the file (or the path to the file) we want to import into the database, *mydb* is the name of the database and *docs* is the name of the collection into which the data will be inserted.  
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
