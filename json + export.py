import json
import pandas as pd
import os
import shutil

def extract_error_logs(json_file):
    if not os.path.exists(json_file):
        print(f"Fichier introuvable : {json_file}. Passage à la suite du script.")
        return []
    
    with open(json_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    extracted_logs = []
    
    for log_entry in logs.get("hits", {}).get("hits", []):  # Adapte selon la structure de ton JSON
        source = log_entry.get("_source", {})
        log_level = source.get("log", {}).get("level", "").lower()
        
        if log_level in ["warning", "error"]:
            extracted_logs.append({
                "message": source.get("message", "N/A"),
                "level": log_level
            })
    
    return extracted_logs

def export_to_excel(json_file):
    if not os.path.exists(json_file):
        print(f"Fichier introuvable : {json_file}. Passage à la suite du script.")
        return
    
    # Copier le fichier JSON pour travailler dessus
    json_copy = json_file.replace(".json", "_copy.json")
    shutil.copy(json_file, json_copy)
    print(f"Fichier JSON copié : {json_copy}")
    
    # Définir le chemin de sortie sur le bureau
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, "output.xlsx")
    
    # Supprimer le fichier Excel existant pour éviter les doublons
    if os.path.exists(output_file):
        os.remove(output_file)
    
    logs = extract_error_logs(json_copy)
    
    if not logs:
        print("Aucun log à exporter.")
        return
    
    # Convertir en DataFrame
    df_logs = pd.DataFrame(logs)
    df_logs = df_logs.sort_values(by=["level"], ascending=False)  # Les erreurs en premier
    
    # Exporter vers Excel
    with pd.ExcelWriter(output_file) as writer:
        df_logs.to_excel(writer, sheet_name="logs", index=False)
    
    print(f"Exportation terminée : {output_file}")
    
    # Supprimer la copie du fichier JSON après traitement
    if os.path.exists(json_copy):
        os.remove(json_copy)
        print(f"Fichier JSON supprimé : {json_copy}")

# Exemple d'utilisation
json_file = input("Entrez le chemin du fichier de log au format .JSON à traiter : ")
export_to_excel(json_file)