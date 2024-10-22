from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'dasitathon'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form.get('text')
    file = request.files.get('file')
    filename = file.filename if file else None

    # Lecture du fichier CSV en utilisant le séparateur approprié
    df = pd.read_csv(file, delimiter=';')

    # Fonction pour catégoriser les achats
    def categoriser(libelle):
        alimentation_keywords = ['CARREFOUR', 'SPAR', 'MONOPRIX', 'SARL TIMES BUR', 'MAISON SARROCH']
        habitat_keywords = ['MAIF', 'RD TPM-RD TOULON VENCE MEDITERRAN']
        shopping_keywords = ['Vinted', 'NYX', 'SAS YES TEA', 'SEPHORA', 'BANFMS', 'SUSHIS ET WOK', 'PORTALIS']
        credit_keywords = ['AGIOS', 'DECOUVERT', 'COTISATION']
        voyages_keywords = ['SNCF']
        transactions_keywords = ['VIREMENT', 'PAYLIB', 'BOURSORAMA']

        if any(keyword in libelle for keyword in alimentation_keywords):
            return 'Alimentation'
        elif any(keyword in libelle for keyword in habitat_keywords):
            return 'Habitat'
        elif any(keyword in libelle for keyword in shopping_keywords):
            return 'Shopping'
        elif any(keyword in libelle for keyword in credit_keywords):
            return 'Crédit'
        elif any(keyword in libelle for keyword in voyages_keywords):
            return 'Voyages'
        elif any(keyword in libelle for keyword in transactions_keywords):
            return 'Transactions'
        else:
            return 'Autres'

    # Appliquer la fonction de catégorisation à la colonne "Libellé"
    df['Categorie'] = df['Libellé'].apply(categoriser)

    # Effectuer les agrégations nécessaires pour les visualisations
    transactions_par_type = df['Categorie'].value_counts().to_dict()
    depenses_par_type = df.groupby('Categorie')['Montant(EUROS)'].sum().to_dict()

    # Stocker les résultats dans la session
    transaction_data = df.to_dict(orient='records')
    session['text'] = text
    session['filename'] = filename
    session['transactions'] = transaction_data
    session['transactions_par_type'] = transactions_par_type
    session['depenses_par_type'] = depenses_par_type

    return redirect(url_for('reslte'))

@app.route('/reslte')
def reslte():
    # Récupérer les résultats stockés dans la session
    text = session.get('text', '')
    filename = session.get('filename', '')
    transactions = session.get('transactions', '')
    transactions_par_type = session.get('transactions_par_type', '')
    depenses_par_type = session.get('depenses_par_type', '')
 # Passer les données au modèle pour l'affichage
    return render_template('reslte.html', transactions=transactions, filename=filename, 
                           transactions_par_type=transactions_par_type, depenses_par_type=depenses_par_type)
if __name__ == '__main__':
    app.run(debug=True)