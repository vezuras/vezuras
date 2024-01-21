import json
import csv

# Fonction pour fusionner deux listes en éliminant les doublons basés sur la clé "Courtier"
def fusionner_listes(liste1, liste2):
    # Utiliser un dictionnaire pour stocker les entrées uniques en se basant sur la clé "Courtier"
    courtier_dict = {entry['Courtier']: entry for entry in liste1 + liste2}
    return list(courtier_dict.values())

# Charger les données depuis le premier fichier JSON
with open('oaciq_result.json', 'r', encoding='utf-8') as file1:
    liste1 = json.load(file1)

# Charger les données depuis le deuxième fichier JSON
with open('oaciq_result2.json', 'r', encoding='utf-8') as file2:
    liste2 = json.load(file2)

# Fusionner les deux listes en éliminant les doublons basés sur la clé "Courtier"
liste_fusionnee = fusionner_listes(liste1, liste2)

# Trier la liste par ordre alphabétique basé sur la clé "Agence"
liste_fusionnee = sorted(liste_fusionnee, key=lambda x: x.get('Agence', '').lower())

# Enregistrer la liste fusionnée dans un fichier JSON
with open('oaciq_broker.json', 'w', encoding='utf-8') as fusion_file:
    json.dump(liste_fusionnee, fusion_file, indent=2, ensure_ascii=False)

# Enregistrer la liste fusionnée dans un fichier CSV
with open('oaciq_broker.csv', 'w', newline='', encoding='utf-8') as csv_file:
    # Créer un objet writer CSV
    csv_writer = csv.writer(csv_file)

    # Écrire l'en-tête du fichier CSV
    csv_writer.writerow(liste_fusionnee[0].keys())

    # Écrire les données dans le fichier CSV
    for entry in liste_fusionnee:
        csv_writer.writerow(entry.values())

print("Listes fusionnées, triées et enregistrées au format JSON et CSV avec succès.")


