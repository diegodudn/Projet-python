import json
import psutil
import platform
import pandas as pd
import socket
import os
from datetime import datetime

# Fonction pour obtenir le fichier source
def get_source_file():
    source_file = input("Entrez le chemin du fichier de log au format .JSON à traiter : ")
    
    if not os.path.exists(source_file):
        print(f"Le fichier {source_file} n'existe pas. Veuillez entrer un chemin valide.")
        return get_source_file()
    
    return source_file

# Charger les logs
def extract_logs(log_file):
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = json.load(file)
        
        # Vérifier si logs est une liste ou un dictionnaire
        if isinstance(logs, dict):
            logs = [logs]  # Convertir en liste si un seul objet est trouvé
        
        if not isinstance(logs, list):
            raise ValueError("Le fichier JSON doit contenir une liste de logs ou un dictionnaire avec des entrées logs.")
        
        filtered_logs = []
        for log in logs:
            if "_source" in log and "log" in log["_source"] and "level" in log["_source"]["log"]:
                log_level = log["_source"]["log"]["level"]
                if log_level in ["warning", "error"]:
                    filtered_logs.append({
                        "log level": log_level,
                        "message": log["_source"].get("message", "N/A"),
                        "station": log["_source"].get("winlog", {}).get("computer_name", "N/A")
                    })
        
        if not filtered_logs:
            print("Aucun log 'warning' ou 'error' trouvé dans le fichier.")
        else:
            print(f"{len(filtered_logs)} logs extraits.")
        
        # Trier les erreurs en premier
        filtered_logs.sort(key=lambda x: x["log level"], reverse=True)
        
        return filtered_logs
    except json.JSONDecodeError:
        print("Erreur : Le fichier JSON est mal formaté.")
        exit(1)
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        exit(1)

# Récupérer les informations système
def get_system_info():
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%H:%M:%S")
    
    system_info = {
        "OS": platform.system() + " " + platform.release(),
        "CPU": platform.processor(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Top 5 Processes": sorted(
            [p.as_dict(attrs=["pid", "name", "cpu_percent", "memory_percent"]) for p in psutil.process_iter()],
            key=lambda x: x["cpu_percent"], reverse=True
        )[:5],
        "Env Variables": dict(platform.uname()._asdict()),
        "Disks": {part.device: psutil.disk_usage(part.mountpoint)._asdict() for part in psutil.disk_partitions()},
        "Network Interfaces": list(psutil.net_if_addrs().keys()),
        "Boot Time": boot_time
    }
    
    return system_info

# Exporter vers Excel
def export_to_excel(logs, system_info, output_file):
    with pd.ExcelWriter(output_file) as writer:
        if logs:
            df_logs = pd.DataFrame(logs)
            df_logs.to_excel(writer, sheet_name="logs", index=False)
        else:
            print("Aucun log à écrire dans le fichier Excel.")
        
        df_sys_info = pd.DataFrame(list(system_info.items()), columns=["Attribute", "Value"])
        df_sys_info.to_excel(writer, sheet_name="System status", index=False)
    
# Exécution du script
log_file = get_source_file()
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
output_file = os.path.join(desktop_path, "system_diagnostic.xlsx")

logs_data = extract_logs(log_file)
system_status = get_system_info()
export_to_excel(logs_data, system_status, output_file)

print(f"Analyse terminée. Fichier Excel généré sur le bureau : {output_file}")
