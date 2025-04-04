import tkinter as tk
from tkinter import messagebox
import requests

class PopulationApp:
    def __init__(self, root):
        # Initialisation de la fenêtre principale
        self.root = root
        self.root.title("Recherche de Population")  # Titre de la fenêtre
        self.root.geometry("400x250")  # Taille de la fenêtre
        self.root.resizable(False, False)  # Empêche le redimensionnement de la fenêtre

        self.create_widgets()  # Appel de la méthode pour créer les widgets

    def create_widgets(self):
        # Création de l'interface utilisateur (labels, champs, boutons)
        self.label_instruction = tk.Label(self.root, text="Entrez un département (78) ou un code postal (78310) :")
        self.label_instruction.pack(pady=10)  # Affiche l'instruction avec un espacement

        self.champ_entrée = tk.Entry(self.root, width=20)  # Champ de texte pour entrer le département ou le code postal
        self.champ_entrée.pack()  # Affiche le champ dans la fenêtre

        self.bouton_recherche = tk.Button(self.root, text="Rechercher", command=self.obtenir_population)
        # Bouton pour lancer la recherche, déclenche la méthode obtenir_population
        self.bouton_recherche.pack(pady=10)  # Affiche le bouton avec un espacement

        self.label_resultat = tk.Label(self.root, text="", wraplength=380, justify="center")
        # Label pour afficher les résultats de la recherche
        self.label_resultat.pack(pady=10)  # Affiche le label pour les résultats

    def obtenir_population(self):
        # Récupère le code entré par l'utilisateur
        code_entrée = self.champ_entrée.get().strip()

        if len(code_entrée) == 2 and code_entrée.isdigit():  # Si c'est un code de département (2 chiffres)
            url = f"https://geo.api.gouv.fr/departements/{code_entrée}"
            try:
                rep = requests.get(url, verify=False)  # Requête pour obtenir les informations du département, ignorer SSL
            except requests.exceptions.SSLError:
                messagebox.showerror("Erreur SSL", "Problème de certificat SSL, la connexion n'a pas pu être établie.")
                return

            if rep.status_code == 200:  # Si la requête est réussie
                departement = rep.json()  # Récupère les données du département
                nom_departement = departement["nom"]  # Extraie le nom du département
                url_communes = f"https://geo.api.gouv.fr/departements/{code_entrée}/communes"
                try:
                    rep_communes = requests.get(url_communes, verify=False)  # Requête pour obtenir les communes du département, ignorer SSL
                except requests.exceptions.SSLError:
                    messagebox.showerror("Erreur SSL", "Problème de certificat SSL, la connexion n'a pas pu être établie.")
                    return

                if rep_communes.status_code == 200:  # Si la requête est réussie
                    communes = rep_communes.json()  # Récupère les données des communes
                    population_totale = sum(commune["population"] for commune in communes)  # Calcule la population totale
                    self.label_resultat.config(text=f"Population du département {nom_departement} ({code_entrée}) : {population_totale} habitants")
                    # Affiche la population totale du département
                else:
                    messagebox.showerror("Erreur", "Impossible de récupérer les communes du département.")  # Gestion d'erreur
            else:
                messagebox.showerror("Erreur", "Département non trouvé.")  # Gestion d'erreur

        elif len(code_entrée) == 5 and code_entrée.isdigit():  # Si c'est un code postal (5 chiffres)
            url = f"https://geo.api.gouv.fr/communes?codePostal={code_entrée}"
            try:
                rep = requests.get(url, verify=False)  # Requête pour obtenir les communes correspondant au code postal, ignorer SSL
            except requests.exceptions.SSLError:
                messagebox.showerror("Erreur SSL", "Problème de certificat SSL, la connexion n'a pas pu être établie.")
                return

            if rep.status_code == 200:  # Si la requête est réussie
                communes = rep.json()  # Récupère les données des communes
                if communes:
                    population_totale = sum(commune["population"] for commune in communes)  # Calcule la population totale
                    noms_communes = ", ".join(commune["nom"] for commune in communes)  # Récupère les noms des communes
                    self.label_resultat.config(text=f"Population des communes ({noms_communes}) : {population_totale} habitants")
                    # Affiche la population totale des communes
                else:
                    messagebox.showerror("Erreur", "Aucune commune trouvée pour ce code postal.")  # Gestion d'erreur
            else:
                messagebox.showerror("Erreur", "Erreur lors de la récupération des données.")  # Gestion d'erreur

        else:
            messagebox.showerror("Format invalide", "Entrez un numéro de département (2 chiffres) ou un code postal (5 chiffres).")
            # Si l'utilisateur n'entre pas un code valide

# Création de la fenêtre principale
if __name__ == "__main__":
    root = tk.Tk()  # Crée la fenêtre principale
    app = PopulationApp(root)  # Crée l'instance de l'application
    root.mainloop()  # Lancement de la boucle principale de l'application
