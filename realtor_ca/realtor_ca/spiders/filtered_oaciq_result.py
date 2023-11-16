import json

def filter_entries(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Filtrer les données
        filtered_data = [entry for entry in data if all(value == "N/A" for key, value in entry.items() if key not in ["Title", "Courtier", "Date", "URL"])]

        return filtered_data

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return []

def write_filtered_data(filtered_data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(filtered_data, json_file, ensure_ascii=False, indent=4)
        print(f"Données filtrées écrites dans {output_file}")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier: {e}")

# Chemin vers le fichier JSON existant
input_file = 'oaciq_result.json'
# Chemin vers le fichier de sortie
output_file = 'filtered_oaciq_result.json'

# Filtrer et écrire les données
filtered_entries = filter_entries(input_file)
write_filtered_data(filtered_entries, output_file)
