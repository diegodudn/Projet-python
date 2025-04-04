import json

def extract_error_logs(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
        print(type(logs))
    
    extracted_logs = []
    
    for log_entry in logs.get("hits", {}).get("hits", []):  # Adapte selon la structure de ton JSON
        source = log_entry.get("_source", {})
        log_level = source.get("log", {}).get("level", "").lower()
        
        if log_level in ["warning", "error"]:
            extracted_logs.append({
                "message": source.get("message", "N/A"),
                "level": log_level,
                "station_name": source.get("host", {}).get("name", "N/A")
            })
    
    return extracted_logs

# Exemple d'utilisation
json_file = input("Entrez le chemin du fichier de log au format .JSON  à traiter : ")
result = extract_error_logs(json_file)

for log in result:
    print(log)