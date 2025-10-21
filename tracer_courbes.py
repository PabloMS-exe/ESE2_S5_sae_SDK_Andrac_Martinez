import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
import csv

class TracerCourbes:
    def __init__(self, fichier_csv=None, titre="Mesures Hyperfréquences"):
        self.liste_gabarit = []
        self.titre = titre
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        # Charger les données depuis le fichier CSV si fourni
        self.donnees = self.charger_donnees_csv(fichier_csv) if fichier_csv else None

    def charger_donnees_csv(self, fichier_csv):
        """
        Charge les données (fréquence, gain) depuis un fichier CSV.
        Le fichier doit avoir deux colonnes numériques sans en-tête, ou avec 'Frequence', 'Gain'.
        """
        if not os.path.exists(fichier_csv):
            print(f"❌ Fichier CSV introuvable : {fichier_csv}")
            return None

        try:
            data = []
            with open(fichier_csv, 'r') as f:
                reader = csv.reader(f)
                lignes = list(reader)

                # Vérifie s’il y a un en-tête (texte dans la première ligne)
                start_index = 1 if any(s.isalpha() for s in lignes[0][0]) else 0

                for row in lignes[start_index:]:
                    try:
                        freq = float(row[0].strip())
                        gain = float(row[1].strip())
                        data.append((freq, gain))
                    except ValueError:
                        continue  # Ignore les lignes mal formatées

            print(f"✅ {len(data)} points chargés depuis : {fichier_csv}")
            return np.array(data)
        except Exception as e:
            print(f"Erreur lecture fichier CSV : {e}")
            return None

    def ajouter_gabarit(self, liste_gabarit):
        self.liste_gabarit = liste_gabarit 

    def tracer(self):
        if self.donnees is None or len(self.donnees) == 0:
            print("⚠️ Aucune donnée à tracer.")
            return

        x, y = self.donnees[:, 0], self.donnees[:, 1]
        self.ax.plot(x, y, label="Signal", color='blue', linewidth=1.5)

        if self.liste_gabarit:
            # Lister uniquement les points dans au moins un gabarit
            points_dans = []
            for xi, yi in zip(x, y):
                for g in self.liste_gabarit:
                    if g.freq_min <= xi <= g.freq_max and g.att_min <= yi <= g.att_max:
                        points_dans.append((xi, yi))
                        break  # Un seul gabarit suffit

            # Tracer uniquement les points dans les gabarits, en rouge
            if points_dans:
                x_d, y_d = zip(*points_dans)
                self.ax.scatter(x_d, y_d, color='red', s=20)

            # Tracer les gabarits visuellement
            self.ax.fill_between([], [], color='yellow', alpha=0.2, label='Gabarit')
            for g in self.liste_gabarit:
                g.tracer(self.ax, label='Gabarit')

        # Légende unique
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
        """
        Vérifie si la courbe mesurée respecte tous les gabarits.
        Retourne True si conforme (aucun point dans le gabarit), False sinon.
        Si liste_gabarit n'est pas fourni, utilise self.liste_gabarit.
        """
        if self.donnees is None or len(self.donnees) == 0:
            print("⚠️ Aucune donnée pour vérification.")
            return False

        gabarits = liste_gabarit if liste_gabarit is not None else self.liste_gabarit
        if not gabarits:
            print("⚠️ Aucun gabarit défini pour la vérification.")
            return False

        freqs = self.donnees[:, 0]
        gains = self.donnees[:, 1]

        for g in gabarits:
            for f, g_mes in zip(freqs, gains):
                # Si point DANS le gabarit (freq + gain dans les limites)
                if g.freq_min <= f <= g.freq_max and g.att_min <= g_mes <= g.att_max:
                    # Point trouvé dans gabarit => non conforme
                    return False

        # Aucun point dans aucun gabarit => conforme
        return True


    def sauvegarder(self, chemin=None):
        """Sauvegarde la figure dans un fichier temporaire."""
        if chemin is None:
            chemin = tempfile.mktemp(suffix='.png')
        self.tracer()
        self.fig.savefig(chemin, bbox_inches='tight', dpi=100)
        plt.close(self.fig)  # Important pour libérer la mémoire
        return chemin






