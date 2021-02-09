import sys
import os
import pymongo

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

# Variable que se ejecuta desde Procfile
app = Flask(__name__)

#uri conexión a la base de datos en MongoDBAtlas
# uri = 'mongodb+srv://canal:canal@cluster0.vodgj.mongodb.net/appsNube?retryWrites=true&w=majority'
uri = 'mongodb+srv://admin:admin@cluster0.up6fc.mongodb.net/examenFeb?retryWrites=true&w=majority'
# uri = os.environ['MONGODB_URI'] + '?retryWrites=true&w=majority' 

# Llámamos a un cliente Mongo que accede a partir de la uri
client = pymongo.MongoClient(uri)

#Para acceder a la base de datos lo haremos con esta línea (entra a la base de datos por defecto)
# Para coger una base de datos concreta tendremos que escribir lo siguiente
# db = client.examenFeb
# o en su defecto
db = client['examenFeb']
# db = client.get_default_database()  

# Seleccionamos la colección que vamos a usar de la base de datos. 
ads = db['ads']
# ads = db['publicaciones']

# --------------------------------- Funciones -------------------------------- #

# Definicion de metodos para endpoints

# URL desde donde llaman a esta función
@app.route('/', methods=['GET'])
def showAds():
    # render template params{
    # Plantilla html que queremos que se muestre
    # ads ? le pasamos un json que se obtiene de la base de datos con esa búsqueda
    # }
    return render_template('ads.html', ads = list(ads.find().sort('date',pymongo.DESCENDING)))
    
@app.route('/new', methods = ['GET', 'POST'])
def newAd():

    if request.method == 'GET' :
        return render_template('new.html')
    else:
        ad = {'author': request.form['inputAuthor'],
              'text': request.form['inputText'], 
              'priority': int(request.form['inputPriority']),
              'date': datetime.now()
             }
        ads.insert_one(ad)
        return redirect(url_for('showAds'))

@app.route('/edit/<_id>', methods = ['GET', 'POST'])
def editAd(_id):
    
    if request.method == 'GET' :
        ad = ads.find_one({'_id': ObjectId(_id)})
        return render_template('edit.html', ad = ad)
    else:
        ad = { 'author': request.form['inputAuthor'],
               'text': request.form['inputText'],
               'priority' : int(request.form['inputPriority'])
             }
        ads.update_one({'_id': ObjectId(_id) }, { '$set': ad })    
        return redirect(url_for('showAds'))

@app.route('/delete/<_id>', methods = ['GET'])
def deleteAd(_id):
    
    adds.delete_one({'_id': ObjectId(_id)})
    return redirect(url_for('showAds'))

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App Engine
    # or Heroku, a webserver process such as Gunicorn will serve the app. In App
    # Engine, this can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)
