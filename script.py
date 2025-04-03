import os
import shutil
import json
import psutil
import platform
import pandas as pd
from datetime import datetime


def main():
    # Demander à l'utilisateur le fichier source
    source_file = get_source_file()
    destination_file = "copied_logs.json"

    # Créer un objet LogProcessor
    log_processor = LogProcessor(source_file, destination_file)

    # Copier le fichier de logs
    log_processor.copy_log_file()

    # Traiter les logs
    log_processor.process_logs()

    # Afficher les logs filtrés
    print("Logs filtrés :")
    for log in log_processor.get_filtered_logs():
        print(f"Log Level: {log[0]}, Message: {log[1]}")



if __name__ == "__main__":
    main()