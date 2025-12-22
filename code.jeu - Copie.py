import tkinter as tk
import random
import json
import difflib

with open('carte_esiee.txt', 'r') as f:
    cartes = json.load(f)

class JeuEnLigne:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeu en ligne interactif")
        self.root.config(bg="black")

        self.joueurs = []
        self.paquet_actuel = []
        self.index_carte = 0
        self.scores = {}
        self.mode_jeu = ""

        self.init_ecran_accueil()

    def init_ecran_accueil(self):
        self.clear_screen()

        tk.Label(self.root, text="Bienvenue au jeu !", fg="purple", bg="pink", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Nombre de joueurs (2-6)").pack()
        self.nb_joueurs_var = tk.IntVar(value=2)
        tk.Entry(self.root, textvariable=self.nb_joueurs_var).pack()
        self.root.config(bg="black")
        tk.Button(self.root, text="Continuer", command=self.init_joueurs).pack(pady=20)

    def init_joueurs(self):
        self.clear_screen()
        self.joueurs = []
        nb_joueurs = self.nb_joueurs_var.get()
        self.root.config(bg="black")

        tk.Label(self.root, text="Entrez les noms des joueurs", bg="pink", fg="purple", font=("Arial", 14)).pack(pady=10)
        self.joueur_vars = []
        for i in range(nb_joueurs):
            tk.Label(self.root, text=f"Joueur {i + 1}").pack()
            joueur_var = tk.StringVar()
            tk.Entry(self.root, textvariable=joueur_var).pack()
            self.joueur_vars.append(joueur_var)

        tk.Button(self.root, text="Commencer", command=self.init_choix_jeu).pack(pady=20)

    def init_choix_jeu(self):
        self.clear_screen()
        self.joueurs = [var.get() for var in self.joueur_vars]
        self.scores = {joueur: 0 for joueur in self.joueurs}

        tk.Label(self.root, text="Choisissez un mode de jeu", bg="pink", fg="purple", font=("Arial", 14)).pack(pady=10)
        for mode in cartes.keys():
            tk.Button(self.root, text=mode, command=lambda m=mode: self.init_partie(m)).pack(pady=5)

        tk.Button(self.root, text="Mélanger", command=lambda: self.init_partie("Mélanger")).pack(pady=5)

    def init_partie(self, mode):
        self.clear_screen()
        self.mode_jeu = mode

        if mode == "Mélanger":
            self.paquet_actuel = [carte for cartes_mode in cartes.values() for carte in cartes_mode]
            random.shuffle(self.paquet_actuel)
        else:
            self.paquet_actuel = cartes[mode]

        self.index_carte = 0
        self.afficher_carte()

    def afficher_carte(self):
        self.clear_screen()

        if self.index_carte >= len(self.paquet_actuel):
            # Fin de la partie
            tk.Label(self.root, text="Fin de la partie !", bg="pink", fg="purple", font=("Arial", 16)).pack(pady=20)
            tk.Label(self.root, text="Scores finaux :", fg="white", bg="black", font=("Arial", 14)).pack()
            for joueur, score in sorted(self.scores.items(), key=lambda x: x[1], reverse=True):
                tk.Label(self.root, text=f"{joueur} : {score} point(s)", fg="white", bg="black").pack()

            tk.Button(self.root, text="Recommencer", bg="pink", fg="purple", command=self.init_ecran_accueil).pack(pady=20)
            return

        carte = self.paquet_actuel[self.index_carte]

        if self.mode_jeu.lower() == "devinette" and isinstance(carte, dict) and "question" in carte and "reponse" in carte:
            # DEVINETTE : Question-Réponse
            tk.Label(self.root, text=carte["question"], bg="pink", fg="purple", font=("Arial", 14), wraplength=400).pack(pady=20)

            self.reponses_vars = {}
            for joueur in self.joueurs:
                tk.Label(self.root, text=f"{joueur}, ta réponse :", fg="white", bg="black").pack()
                var = tk.StringVar()
                tk.Entry(self.root, textvariable=var).pack()
                self.reponses_vars[joueur] = var

            tk.Button(self.root, text="Valider", command=lambda: self.verifier_reponses(carte["reponse"])).pack(pady=20)

        else:
            # Autres modes
            tk.Label(self.root, text=carte, bg="pink", fg="purple", font=("Arial", 14), wraplength=400).pack(pady=20)

            # On n'affiche pas les scores pour le mode "tu préfères"
            if self.mode_jeu.lower() != "tu préfères":
                tk.Label(self.root, text="Scores actuels :", fg="white", bg="black", font=("Arial", 12)).pack()
                for joueur, score in self.scores.items():
                    tk.Label(self.root, text=f"{joueur} : {score} point(s)", fg="white", bg="black").pack()

                tk.Label(self.root, text="Attribuer un point :", fg="white", bg="black", font=("Arial", 12)).pack()
                for joueur in self.joueurs:
                    tk.Button(self.root, text=joueur, command=lambda j=joueur: self.donner_point(j)).pack(pady=2)
            else:
                tk.Label(self.root, text="Mode discussion - Pas de points", fg="white", bg="black", font=("Arial", 12)).pack(pady=10)

            tk.Button(self.root, text="Suivant", command=self.suivant).pack(pady=20)

    def verifier_reponses(self, bonne_reponse):
        bonne_reponse = bonne_reponse.strip().lower()
        messages = []

        for joueur, var in self.reponses_vars.items():
            reponse = var.get().strip().lower()
            if reponse == bonne_reponse or difflib.get_close_matches(reponse, [bonne_reponse], n=1, cutoff=0.8):
                self.scores[joueur] += 1
                messages.append(f"{joueur} ✅ Bonne réponse !")
            else:
                messages.append(f"{joueur} ❌ Mauvaise réponse.")

        self.clear_screen()

        tk.Label(self.root, text="Correction", bg="pink", fg="purple", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=f"Bonne réponse : {bonne_reponse}", fg="white", bg="black", font=("Arial", 14)).pack(pady=5)

        for msg in messages:
            tk.Label(self.root, text=msg, fg="white", bg="black", font=("Arial", 12)).pack(pady=2)

        # On n'affiche pas les scores pour le mode "tu préfères"
        if self.mode_jeu.lower() != "tu préfères":
            tk.Label(self.root, text="Scores actuels :", fg="white", bg="black", font=("Arial", 12)).pack(pady=10)
            for joueur, score in self.scores.items():
                tk.Label(self.root, text=f"{joueur} : {score} point(s)", fg="white", bg="black").pack()

        tk.Button(self.root, text="Carte suivante", command=self.suivant).pack(pady=20)

    def donner_point(self, joueur):
        if self.mode_jeu.lower() != "tu préfères":
            self.scores[joueur] += 1
        self.afficher_carte()

    def suivant(self):
        self.index_carte += 1
        self.afficher_carte()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JeuEnLigne(root)
    root.mainloop()