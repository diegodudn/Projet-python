import json
import pandas as pd
import os
import shutil
import platform
import psutil
import time
from datetime import datetime

class LogExtractor:
    #Extract logs
    @staticmethod
    def extract_error_logs(json_file):
        if not os.path.exists(json_file):
            print(f"Fichier introuvable : {json_file}. Veuillez indiquer un chemin valide.")
            return []

        with open(json_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)

        extracted_logs = []

        for log_entry in logs.get("hits", {}).get("hits", []):
            source = log_entry.get("_source", {})
            log_level = source.get("log", {}).get("level", "").lower()

            if log_level in ["warning", "error"]:
                extracted_logs.append({
                    "message": source.get("message", "N/A"),
                    "level": log_level
                })

        return extracted_logs

class SystemInfo:
    @staticmethod
    def get_system_status_dict():
        # Infos système
        return {
            "OS": platform.platform(),
            "CPU": platform.processor(),
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%H:%M:%S"),
            "Interfaces Réseau": ", ".join(psutil.net_if_addrs().keys()),
            "Partition des disques": " | ".join(
                f"{part.device} ({part.mountpoint}) - {part.fstype}"
                for part in psutil.disk_partitions()
                if os.access(part.mountpoint, os.R_OK)
            ),
            "Espace disque": " | ".join(
                f"{part.mountpoint} - {round(psutil.disk_usage(part.mountpoint).free / (1024**3), 2)} GB libres"
                for part in psutil.disk_partitions()
                if os.access(part.mountpoint, os.R_OK)
            )
        }

    #GET ENV VAR
    @staticmethod
    def get_environment_variables_df():
        return pd.DataFrame(list(os.environ.items()), columns=["Clé", "Valeur"])

class ProcessAnalyzer:
    #GET TOP PROC 
    @staticmethod
    def get_top_processes_df():
        cpu_count = psutil.cpu_count(logical=True)

        # Initialiser les valeurs CPU
        for p in psutil.process_iter():
            try:
                p.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(1)  # Pause pour permettre l’échantillonnage (fonctionnement de cpu_percent qui nécessite un laps de temps pour récupérer la valeur)

        processes = []
        for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                if p.info['name'] == "System Idle Process":  #process de windows qui  indique le pourcentage du cpu non utilisé 
                    continue
                cpu = p.cpu_percent(interval=None)
                mem = p.info['memory_percent']
                processes.append((p.info['name'], p.info['pid'], cpu / cpu_count, mem))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: (x[2] + x[3]), reverse=True) #trie process en fonction de la somme de l'utilisation CPU + RAM
        top_processes = processes[:5]

        data = []
        total_cpu = 0.0

        for name, pid, cpu_percent, mem_percent in top_processes:
            total_cpu += cpu_percent
            data.append({
                "Nom du processus": name,
                "PID": pid,
                "CPU (%)": round(cpu_percent, 2),
                "Mémoire (%)": round(mem_percent, 2)
            })

        cpu_unused = max(0, 100 - total_cpu)
        data.append({
            "Nom du processus": "Total CPU inutilisé", #petite fonctionnalité rajoutée depuis System Idle Process
            "PID": "",
            "CPU (%)": round(cpu_unused, 2),
            "Mémoire (%)": ""
        })

        return pd.DataFrame(data)

class ExcelExporter:
    #Export Excel
    @staticmethod
    def export_to_excel(json_file):
        if not os.path.exists(json_file):
            print(f"Fichier introuvable : {json_file}. Veuillez indiquer un chemin valide.")
            return

        json_copy = json_file.replace(".json", "_copy.json")
        shutil.copy(json_file, json_copy)
        print(f"Fichier JSON copié : {json_copy}")

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_file = os.path.join(desktop_path, "output.xlsx")

        if os.path.exists(output_file):
            os.remove(output_file)

        logs = LogExtractor.extract_error_logs(json_copy)
        df_logs = pd.DataFrame(logs)

        # tri pour avoir "error" avant "warning"
        if not df_logs.empty:
            df_logs["level"] = pd.Categorical(df_logs["level"], categories=["error", "warning"], ordered=True)
            df_logs = df_logs.sort_values(by=["level"])

        system_info_dict = SystemInfo.get_system_status_dict()
        df_system = pd.DataFrame([system_info_dict])

        df_env_vars = SystemInfo.get_environment_variables_df()
        df_processes = ProcessAnalyzer.get_top_processes_df()

        #Formatage Pour Excel sheet system status , j'ai modifié l'affichage dans excel pour plus de lisibilité
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            if not df_logs.empty:
                df_logs.to_excel(writer, sheet_name="logs", index=False)

            ws_name = "System status"

            # Infos système 
            df_system.to_excel(writer, sheet_name=ws_name, index=False, startrow=0)

            # Variables d’environnement 
            env_start_row = 4  # décallage ligne 5
            ws = writer.book[ws_name]
            ws.cell(row=env_start_row + 1, column=1).value = "Variables d’environnement :"
            df_env_vars.to_excel(writer, sheet_name=ws_name, index=False, startrow=env_start_row + 1)

            # Top 5 processus 
            process_start_row = env_start_row + len(df_env_vars) + 4  
            ws.cell(row=process_start_row, column=1).value = "Top 5 processus les plus gourmands"
            df_processes.to_excel(writer, sheet_name=ws_name, index=False, startrow=process_start_row)

        print(f"Exportation terminée : {output_file}")

        if os.path.exists(json_copy):
            os.remove(json_copy)
            print(f"Fichier JSON supprimé : {json_copy}")

# TEST
json_file = input("Entrez le chemin du fichier de log au format .JSON à traiter : ")
ExcelExporter.export_to_excel(json_file)