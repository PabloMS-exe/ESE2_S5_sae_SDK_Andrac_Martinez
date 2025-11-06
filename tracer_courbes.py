import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
import csv

class TracerCourbes:
    def __init__(self, fichier_csv=None, titre="Mesures Hyperfréquences"):
        # Liste des gabarits à afficher
        self.liste_gabarit = []
        self.titre = titre

        # Création de la figure et des axes pour le tracé
        self.fig, self.ax = plt.subplots(figsize=(8, 5))

        # Charge les données depuis le CSV si fourni
        self.donnees = self.charger_donnees_csv(fichier_csv) if fichier_csv else None

    def charger_donnees_csv(self, fichier_csv):
        """
        Lit un fichier CSV avec deux colonnes : fréquence et gain.
        Ignore les lignes mal formées et vérifie si il y a un en-tête.
        """
        if not os.path.exists(fichier_csv):
            print(f"Fichier CSV introuvable : {fichier_csv}")
            return None

        try:
            data = []
            with open(fichier_csv, 'r') as f:
                reader = csv.reader(f)
                lignes = list(reader)

                # Détecte si la première ligne est un texte (en-tête)
                start_index = 1 if any(s.isalpha() for s in lignes[0][0]) else 0

                for row in lignes[start_index:]:
                    try:
                        freq = float(row[0].strip())
                        gain = float(row[1].strip())
                        data.append((freq, gain))
                    except ValueError:
                        continue  # Ignore les lignes incorrectes

            print(f"{len(data)} points chargés depuis : {fichier_csv}")
            return np.array(data)
        except Exception as e:
            print(f"Erreur lecture fichier CSV : {e}")
            return None

    def ajouter_gabarit(self, liste_gabarit):
        """Ajoute une liste de gabarits pour les tracer ensuite"""
        self.liste_gabarit = liste_gabarit 

    def tracer(self):
        """Trace la courbe et les gabarits"""
        if self.donnees is None or len(self.donnees) == 0:
            print("Aucune donnée à tracer.")
            return

        x, y = self.donnees[:, 0], self.donnees[:, 1]
        self.ax.plot(x, y, label="Signal", color='blue', linewidth=1.5)

        # Si des gabarits sont définis
        if self.liste_gabarit:
            points_dans = []
            for xi, yi in zip(x, y):
                for g in self.liste_gabarit:
                    if g.freq_min <= xi <= g.freq_max and g.att_min <= yi <= g.att_max:
                        points_dans.append((xi, yi))
                        break  # Un point ne doit appartenir qu'à un seul gabarit

            # Trace les points dans les gabarits en rouge
            if points_dans:
                x_d, y_d = zip(*points_dans)
                self.ax.scatter(x_d, y_d, color='red', s=20)

            # Tracer les gabarits visuellement
            for g in self.liste_gabarit:
                g.tracer(self.ax, label='Gabarit')

        # Évite les doublons dans la légende
        handles, labels = self.ax.get_legend_handles_labels()
        unique = {}
        for h, l in zip(handles, labels):
            if l not in unique and l is not None:
                unique[l] = h
        self.ax.legend(unique.values(), unique.keys())

        self.ax.set_title(self.titre)
        self.ax.set_xlabel("Fréquence (GHz)")
        self.ax.set_ylabel("Amplitude (dB)")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        plt.show()

    def verifier_conformite(self, liste_gabarit=None):
        """Vérifie si la courbe respecte tous les gabarits. Retourne True si aucun point n'est dans les gabarits."""
        if self.donnees is None or len(self.donnees) == 0:
            print("Aucune donnée pour vérifier la conformité.")
            return False

        gabarits = liste_gabarit if liste_gabarit else self.liste_gabarit
        if not gabarits:
            print("Aucun gabarit défini.")
            return False

        freqs = self.donnees[:, 0]
        gains = self.donnees[:, 1]

        for g in gabarits:
            for f, g_mes in zip(freqs, gains):
                if g.freq_min <= f <= g.freq_max and g.att_min <= g_mes <= g.att_max:
                    # Si un point est dans le gabarit => non conforme
                    return False

        # Aucun point dans les gabarits => conforme
        return True

    def sauvegarder(self, chemin=None):
        """Sauvegarde la figure dans un fichier temporaire ou donné"""
        if chemin is None:
            chemin = tempfile.mktemp(suffix='.png')
        self.tracer()
        self.fig.savefig(chemin, bbox_inches='tight', dpi=100)
        plt.close(self.fig)  # Libère la mémoire
        return chemin
