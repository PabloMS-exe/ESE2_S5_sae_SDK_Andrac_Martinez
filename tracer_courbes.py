import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile
import os

class Gabarit:
    def __init__(self, freq_min, freq_max, att_min, att_max):
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.att_min = att_min
        self.att_max = att_max

    def est_dans_gabarit(self, freq, valeur):
        return (self.freq_min <= freq <= self.freq_max and
                self.att_min <= valeur <= self.att_max)

    def tracer(self, ax):
        ax.axvline(self.freq_min, color='r', linestyle='--', alpha=0.5)
        ax.axvline(self.freq_max, color='r', linestyle='--', alpha=0.5)
        ax.axhline(self.att_min, color='g', linestyle='--', alpha=0.5)
        ax.axhline(self.att_max, color='g', linestyle='--', alpha=0.5)
        ax.fill_between(
            [self.freq_min, self.freq_max],
            self.att_min, self.att_max,
            color='yellow', alpha=0.2, label='Gabarit'
        )

class TracerCourbes:
    def __init__(self, donnees, titre="Mesures Hyperfréquences"):
        self.donnees = donnees
        self.liste_gabarit = []
        self.titre = titre
        self.fig, self.ax = plt.subplots(figsize=(8, 5))

    def ajouter_gabarit(self, liste_gabarit):
        self.liste_gabarit = liste_gabarit 

    def tracer(self):
        if self.donnees is None or len(self.donnees) == 0:
            print("⚠️ Aucune donnée à tracer.")
            return

        x, y = self.donnees[:, 0], self.donnees[:, 1]
        self.ax.plot(x, y, label="Signal", color='blue', linewidth=1.5)

        if self.liste_gabarit:
            for gabarit in self.liste_gabarit:
                gabarit.tracer(self.ax)

                # Points hors gabarit (je suppose que est_dans_gabarit renvoie False pour hors gabarit)
                hors_gabarit = [(x[i], y[i]) for i in range(len(x))
                                if not gabarit.est_dans_gabarit(x[i], y[i])]
                if hors_gabarit:
                    x_hg, y_hg = zip(*hors_gabarit)
                    self.ax.scatter(x_hg, y_hg, color='red', label='Hors gabarit', s=20)

        self.ax.set_title(self.titre)
        self.ax.set_xlabel("Fréquence (Hz)")
        self.ax.set_ylabel("Amplitude (dB)")
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.6)
        plt.show()

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

    def ajouter_texte(self, texte, taille=12):
        self.add_page()  # Nouvelle page pour le texte
        self.set_font("Arial", size=taille)
        self.multi_cell(0, 10, texte)
        self.ln(5)

    def ajouter_courbe(self, tracer, titre=None):
        """Ajoute une courbe au PDF avec gestion des images."""
        chemin_img = tracer.sauvegarder()
        # self.add_page()  # Nouvelle page pour la courbe
        if titre:
            self.set_font("Arial", 'B', 14)
            self.cell(0, 10, titre, ln=True, align='C')
            self.ln(5)
        # Insère l'image centrée
        self.image(chemin_img, x=30, y=None, w=150)
        os.remove(chemin_img)  # Nettoyage

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

