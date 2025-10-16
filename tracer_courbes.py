import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile
import os
import csv

class Gabarit:
    def __init__(self, freq_min, freq_max, att_min, att_max):
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.att_min = att_min
        self.att_max = att_max

    def est_dans_gabarit(self, freq, valeur):
        return (self.freq_min <= freq <= self.freq_max and
                self.att_min <= valeur <= self.att_max)

    def tracer(self, ax, label):
        ax.axvline(self.freq_min, color='r', linestyle='--', alpha=0.5)
        ax.axvline(self.freq_max, color='r', linestyle='--', alpha=0.5)
        ax.axhline(self.att_min, color='g', linestyle='--', alpha=0.5)
        ax.axhline(self.att_max, color='g', linestyle='--', alpha=0.5)
        ax.fill_between(
            [self.freq_min, self.freq_max],
            self.att_min, self.att_max,
            color='#FFFF00', alpha=0.4, label='Gabarit'
        )

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
            # On prépare deux listes globales
            points_dans = []
            points_hors = []
            # On fait pour chaque point : vérifier s'il est dans **au moins un** gabarit
            for xi, yi in zip(x, y):
                dans = False
                for g in self.liste_gabarit:
                    if g.freq_min <= xi <= g.freq_max and g.att_min <= yi <= g.att_max:
                        dans = True
                        break
                if dans:
                    points_dans.append((xi, yi))
                else:
                    points_hors.append((xi, yi))

            # Maintenant on scatter les deux catégories, avec labels une seule fois
            if points_hors:
                x_h, y_h = zip(*points_hors)
                self.ax.scatter(x_h, y_h, color='red', label='Hors gabarit', s=20)
            if points_dans:
                x_d, y_d = zip(*points_dans)
                self.ax.scatter(x_d, y_d, color='black', label='Dans le gabarit', s=20)

            # Optionnel : tracer les gabarits visuellement
            # Ici on les trace tous (avec ou sans label selon ta préférence)
            # (Supposons qu'on veuille une seule légende "Gabarit")
            # On peut faire un tracé invisible pour légende du gabarit
            # Exemple :
            self.ax.fill_between([], [], color='yellow', alpha=0.2, label='Gabarit')
            for g in self.liste_gabarit:
                g.tracer(self.ax, label = "Gabarit")

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
        Retourne True si conforme, False sinon.
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
                if g.freq_min <= f <= g.freq_max:
                    if not (g.att_min <= g_mes <= g.att_max):
                        return False
        return True


    def sauvegarder(self, chemin=None):
        """Sauvegarde la figure dans un fichier temporaire."""
        if chemin is None:
            chemin = tempfile.mktemp(suffix='.png')
        self.tracer()
        self.fig.savefig(chemin, bbox_inches='tight', dpi=100)
        plt.close(self.fig)  # Important pour libérer la mémoire
        return chemin

class PDFExporter(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Charge la police Unicode DejaVu (assure-toi que le fichier TTF est bien dans fonts/)
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        self.set_font('DejaVu', '', 12)
    
    def ajouter_page(self):
        self.add_page()

    def ajouter_texte(self, texte, taille=12):
        self.set_font('DejaVu', '', taille)
        self.multi_cell(0, 10, texte)
        self.ln(5)

    def ajouter_courbe(self, tracer, titre=None):
        chemin_img = tracer.sauvegarder()
        if titre:
            self.set_font('DejaVu', 'B', 14)
            self.cell(0, 10, titre, ln=True, align='C')
            self.ln(5)
        self.image(chemin_img, x=30, w=150)
        os.remove(chemin_img)

    def generer(self, chemin_pdf):
        self.output(chemin_pdf)
        print(f"PDF généré: {chemin_pdf}")


# # 1. Créer une courbe avec gabarit
# tracer = TracerCourbes(titre="Analyse Hyperfréquence - Gabarit")
# gabarit1 = Gabarit(freq_min=0.0, freq_max=2.2, att_min=1.0, att_max=2.0)
# gabarit2 = Gabarit(freq_min=2.2, freq_max=6.0, att_min=-0.8, att_max=0.5)
# gabarit3 = Gabarit(freq_min=6.0, freq_max=8.0, att_min=1.2, att_max=2.2)
# liste_gabarit = [gabarit1, gabarit2, gabarit3]
# tracer.ajouter_gabarit(liste_gabarit)

# # 2. Générer le PDF
# pdf = PDFExporter()
# pdf.ajouter_texte(
#     "Rapport de Mesures Hyperfréquences\n"
#     "----------------------------------\n"
#     f"Gabarit appliqué:\n"
#     f"- Plage de fréquences: {gabarit1.freq_min} à {gabarit1.freq_max} Hz\n"
#     f"- Atténuation tolérée: {gabarit1.att_min} à {gabarit1.att_max} dB \n"
# )
# pdf.ajouter_courbe(tracer, "Courbe avec Gabarit Hyperfréquence")
# pdf.generer("rapport_hyperfrequences.pdf")

