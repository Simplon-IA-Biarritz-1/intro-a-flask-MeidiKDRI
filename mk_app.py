from flask import Flask, render_template, request, jsonify
import mysql.connector as MS
import pandas as pd

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
def formulaire() :
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
@app.route('/prediction')
def pred_page() :
    return render_template('prediction.html')

@app.route('/prediction', methods = ['GET', 'POST'])
def upload_image():
   if request.method == 'POST':
      picture = request.files['file']
      return render_template('prediction.html', image = picture)

if __name__ == "__main__" :
    app.run(debug=True)