import sys
import os
import pymongo

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

# -------------------------------- Mis imports ------------------------------- #
from base64 import b64encode
from flask import session
import requests, json



# Variable que se ejecuta desde Procfile
app = Flask(__name__)

# Establecemos la clave de la sesión
# Creo que no es lo mejor pero por ahora sirve
app.secret_key = os.urandom(24)

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
db = client['examenFeb'] # Con esto funciona
# db = client.get_default_database()  

# Seleccionamos la colección que vamos a usar de la base de datos. 
# EXAMEN
publicacion = db['publicacion']
# ads = db['publicaciones']

# --------------------------------- Funciones -------------------------------- #

def subirImagen_imgur(archivo):
    # Client ID: bbcaf01dcb92968
    # Client Secret: a5fb9fabc5afc993dbe214336df64113d8f04e8b
    try:
        dic = {
            'image': b64encode(archivo.read()),
            'type': 'base64'
        }
    except Exception as inst:
        print(type(inst))    # the exception instance
        print(inst.args)     # arguments stored in .args
        print(inst)          # __str__ allows args to be printed directly, 
    j1 = requests.post(
        "https://api.imgur.com/3/image",
        data = dic,
        headers = {
            'Accept': 'application/json', 
            'Authorization': 'Client-ID bbcaf01dcb92968'
        }
    )
    # Devuelve la URL de la imagen
    return json.loads(j1.content)['data']['link']


def login_required():
    if ( not session.get('token')):
        
        return redirect(url_for('login')) 
    print('El token es' + session.get('token'))



# Definicion de metodos para endpoints
@app.route('/probarToken', methods=['POST'])
def probar_token():
    # 
    req = requests.post(
        "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + request.form['idtoken']
    )
    session['token'] = request.form['idtoken']
    print('Respuesta del servidor de Google ' + str(req.json))
    return str('Autentificación completada')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        print('Entramos al login')
        return render_template('login.html') # En principio no le pasamos ningún dato
    else:
        print('Guardamos el token en la sesión')
        
        
        return probar_token()

@app.route('/', methods=['GET'])
def inicio():
    if(not session.get('token')):
        print('No hay token')
        return redirect(url_for('login')) 
    # EXAMEN
    return render_template('inicio.html', dic= list(publicacion.find()))



# def showAds():
#     if(not session.get('token')):
#         print('No hay token')
#         return redirect(url_for('login')) 
    
#     # render template params{
#     # Plantilla html que queremos que se muestre
#     # ads ? le pasamos un json que se obtiene de la base de datos con esa búsqueda
#     # }
#     print('Accedemos a la página principal')
#     return render_template('ads.html', ads = list(ads.find().sort('date',pymongo.DESCENDING)))
    
@app.route('/new', methods = ['GET', 'POST'])
def new():

    if request.method == 'GET' :
        return render_template('new.html')
    else:
        imagen = request.files['imagen']
        url = subirImagen_imgur(imagen)
        # Poner los atributos de los objetos
        # En principio están los básicos
        dic= {
            'titulo': request.form['titulo'],
            'imagen': url, 

        }
        publicacion.insert_one(dic)
        return redirect(url_for('inicio'))

@app.route('/edit/<_id>', methods = ['GET', 'POST'])
def edit(_id):
    print('Entrando a editar')
    if request.method == 'GET' :
        p = publicacion.find_one({'_id': ObjectId(_id)})
        return render_template('edit.html', p = p)
    else:
        p=publicacion.find_one({'_id': ObjectId(_id)})
        dic = { 'titulo': request.form['titulo'],
                'imagen': p['imagen']
            }
        publicacion.update_one({'_id': ObjectId(_id) }, { '$set': dic })    
        return redirect(url_for('inicio'))

@app.route('/delete/<_id>', methods = ['GET'])
def delete(_id):
    
    publicacion.delete_one({'_id': ObjectId(_id)})
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App Engine
    # or Heroku, a webserver process such as Gunicorn will serve the app. In App
    # Engine, this can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)
