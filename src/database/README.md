# Database

Our Database content was exported into a json file accessible using [link](https://umich.box.com/s/gmybk8xu1htec9w3z4vse86vtotws22r).



# How to collect data to create our Database?
We use web-scraping in order to collect detailed description of electronic components.
The data collected is scrapped from Digikey website using web-scraping libraries in Python.

### Prerequisites
- Use Chrome for the scraping process
- Download [chromedriver](https://chromedriver.chromium.org/downloads)
- Install [Selenium package](https://selenium-python.readthedocs.io/installation.html)
- Use Python version 3.5 or higher

### Steps

 - Generate 'links_and_type.csv' by running the following script:
```
python digikey_get_urls.py
```

It will be used to perform the next step of the scraping process.

 - Run web scraping script

```
python digikey_web_scraping.py
```
Please note that the script will take from few minutes to several hours depending on the number of components present in a given category.

 - Populate your local DB (only one of the following scripts needs to be run in order to populate the database):
    - Populate your local DB with the files extracted (raw version):  `python populate_db_fron_csv.py`

    - Populate your local DB with the files extracted (with data transformation): `python digikey_data_transformation.py`

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
### Import data into MongoDB

Run the following command
```
mongoimport ––host localhost:27017 ––db mydb ––collection docs digikey.json
```

In this example, *digikey.json* is the file (or the path to the file) we want to import into the database, *mydb* is the name of the database and *docs* is the name of the collection into which the data will be inserted.  
Note that *localhost:27017* is the default server and port for MongoDB.


To confirm that the records are now in MongoDB, do the following.

 - Start the Mongo shell by running `mongo`
 - Issue a `show dbs` command to see the available databases.  *mydb* should be listed
 - Issue a `use mydb` command to switch to the *mydb* database
 - Issue a `show collections` command to see the collections in the database.  *docs* should be listed
 - Issue a `db.docs.find()` command to see the records in the “docs” collection.  The first twenty records will be returned.  Type “it” to see additional records


# Compass GUI for MongoDB

To visually explore, query and interact with the data, it is recommended to use [Compass](https://www.mongodb.com/download-center/compass).

# Complete tutorial

This [document](https://umich.box.com/s/7xiozn2tr6e8doikobfntrp7hrykfkjn) gives a step by step guide on how to install MongoDB on other Operating Systems and how to perform queries. By the end of the tutorial you will be able to vizualize documents and search records in the Database using queries.

Please contact [admin](zinebbe@umich.edu) for any question or concern related to this note.
