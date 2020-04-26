const express = require('express')
const app = express()
const bodyParser = require('body-parser')
const MongoClient = require('mongodb').MongoClient

var db

// Remember to change YOUR_USERNAME and YOUR_PASSWORD to your username and password! 
MongoClient.connect('mongodb+srv://admin:admin@clusterdigikey-dt6y1.mongodb.net/digikey?retryWrites=true&w=majority', (err, database) => {
  if (err) return console.log(err)
  db = database.db('digikey')
  app.listen(process.env.PORT || 3000, () => {
    console.log('listening on 3000')
  })
})


/* const MongoClient = require('mongodb').MongoClient;
const uri = "mongodb+srv://admin:admin@clusterdigikey-dt6y1.mongodb.net/test?retryWrites=true&w=majority";
const client = new MongoClient(uri, { useNewUrlParser: true });
client.connect(err => {
  const collection = client.db("test").collection("devices");
  // perform actions on the collection object
  client.close();
}); */




app.set('view engine', 'ejs')
app.use(bodyParser.urlencoded({extended: true}))
app.use(bodyParser.json())
app.use(express.static('public'))

var options = {
  "limit": 10000,

}


app.get('/', (req, res) => {
  db.collection('digikey').find({"Subcategory" : /.*adc.*/}, options).toArray((err, result) => {
    if (err) return console.log(err)
    res.render('index.ejs', {digikey: result}, );
  })
})

app.post('/digikey', (req, res) => {
  db.collection('digikey').save(req.body, (err, result) => {
    if (err) return console.log(err)
    console.log('saved to database')
    res.redirect('/')
  })
})

app.put('/digikey', (req, res) => {
  db.collection('digikey')
  .findOneAndUpdate({name: 'Description'}, {
    $set: {
      name: req.body.name,
      quote: req.body.quote
    }
  }, {
    sort: {_id: -1},
    upsert: true
  }, (err, result) => {
    if (err) return res.send(err)
    res.send(result)
  })
})

app.delete('/digikey', (req, res) => {
  db.collection('digikey').findOneAndDelete({name: req.body.name}, (err, result) => {
    if (err) return res.send(500, err)
    res.send('A record got deleted')
  })
})
