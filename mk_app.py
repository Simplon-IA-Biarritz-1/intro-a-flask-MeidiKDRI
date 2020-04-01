from flask import Flask, render_template, request, jsonify, redirect, send_from_directory, url_for
import mysql.connector as MS

from werkzeug.utils import secure_filename
import os
import base64

import pandas as pd
import numpy as np

from keras.datasets import mnist
from sklearn.linear_model import LogisticRegression

from skimage.color import rgb2gray
import matplotlib.image as mpimg

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression 

# Mnist dataset
(X_train, y_train), (X_test, y_test) = mnist.load_data()
X_train = X_train.reshape(60000,-1)
X_test = X_test.reshape(10000,-1)

# Gestion de la connection à MariaSQL
connection = MS.connect(user='root', password='root', host='127.0.0.1', buffered=True)
cursor = connection.cursor()
utiliser_bd = "USE flask_app"
cursor.execute(utiliser_bd)

app = Flask(__name__)
app.config.update(DEBUG=True)

@app.route('/')
def home() :
    return render_template("index.html")

# Q 3-4 : Faire un lien vers une seconde page/ formulaire
@app.route('/formulaire')
def form() :
    return render_template('formulaire.html')

# Q 5 : Enregistrement dans une base SQL
@app.route('/formulaire', methods = ['POST'])
def save_user() :    
    result = request.form
    prenom = result['prenom']
    nom = result['nom']
    sexe = result['sexe']
    pseudo = result['pseudo']    
    if sexe == 'masculin' :
        texte = f'Bienvenue Mr {prenom}, {nom}. Votre pseudo est {pseudo}'
    else :
        texte = f'Bienvenue Mme {prenom}, {nom}. Votre pseudo est {pseudo}'

    # Gestion des pseudos déjà existants
    user_existant = "SELECT * FROM users WHERE pseudo = '%s' "
    cursor.execute(user_existant % pseudo)
    resultat_user_existant= cursor.fetchall()

    # Si déjà utilisé
    if len(resultat_user_existant) > 0:
        error = 'Ce pseudo est deja utilisé, veuillez en choisir un nouveau'
        return render_template("formulaire.html", error = error)

    # Sinon, inscription dans la BDD
    else:
        req_save_user = "INSERT INTO users (nom, prenom, sexe, pseudo)VALUES(%s,%s,%s,%s);"
        cursor.execute(req_save_user, (nom, prenom, sexe, pseudo))
        connection.commit()
        return render_template('member.html', message = texte)

# Q 6 : Affichage de tous les membres
@app.route("/users")
def users_page():

    query = "SELECT nom FROM users"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('users.html', data = data)

# Q 7 : Afficher les stats d'un fichier chargé par l'utilisateur
@app.route('/stats')
def stat_page() :
    return render_template('statistics.html')

@app.route('/stats', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      df = pd.read_csv(f)
      desc = df.describe()
      return render_template('statistics.html', tables = [desc.to_html(classes = 'data')], titles = desc.columns.values)

# Q 8 : Afficher une prediction à partir d'un modèle
@app.route('/pred')
def pred_page() :
    return render_template('prediction.html')

@app.route('/pred', methods=['GET', 'POST'])
def mnist_pred():
    
    # Image upload
    img = request.files['image_uploaded']
    # image saving
    base64img = "data:image/png;base64,"+base64.b64encode(img.getvalue()).decode('ascii')

    # Image preprocessing
    img3d = mpimg.imread(img)
    img3dgray = rgb2gray(img3d)
    img3d = np.resize(img3dgray, (28, 28, 1))
    img2d = img3d.reshape(1,-1)

    #Random Forest
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(img2d)

    # Logistic Regression
    reg_log = LogisticRegression()
    reg_log.fit(X_train, y_train)
    y_pred_reglog = reg_log.predict(img2d)

    return render_template(
        'prediction.html', base64img = base64img,
        reg_logistic = f'Logistic Regression prediction : {y_pred_reglog}',
        randomForest = f'Random Forest prediction: {y_pred_rf}')

if __name__ == "__main__" :
    app.run(debug=True)
