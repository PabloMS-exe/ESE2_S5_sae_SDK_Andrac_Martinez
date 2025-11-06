from fpdf import FPDF
import os

class Creation_PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Active le saut de page automatique (pour éviter d'écrire trop bas)
        self.set_auto_page_break(auto=True, margin=15)

        # Ajoute la police DejaVu pour gérer les accents et caractères spéciaux
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)

        # Définit la police par défaut (texte normal)
        self.set_font('DejaVu', '', 12)
    
    def ajouter_page(self):
        """Ajoute une nouvelle page dans le PDF"""
        self.add_page()

    def ajouter_texte(self, texte, taille=12):
        """Ajoute un texte dans le PDF"""
        self.set_font('DejaVu', '', taille)  # Définit la taille de police
        self.multi_cell(0, 10, texte)        # Écrit le texte sur plusieurs lignes 
        self.ln(5)                           # Ajoute un petit espace après le texte

    def ajouter_courbe(self, tracer, titre=None):
        """Ajoute une image (ex: une courbe tracée) dans le PDF"""
        chemin_img = tracer.sauvegarder()

        # Si un titre est précisé, on l’affiche avant l’image
        if titre:
            self.set_font('DejaVu', 'B', 14)
            self.cell(0, 10, titre, ln=True, align='C')
            self.ln(5)
        # Ajoute l’image au centre de la page
        self.image(chemin_img, x=30, w=150)
        # Supprime l’image après l’avoir utilisée
        os.remove(chemin_img)

    def generer(self, chemin_pdf):
        """Crée le fichier PDF final"""
        self.output(chemin_pdf)
        print(f"PDF généré avec succès : {chemin_pdf}")
