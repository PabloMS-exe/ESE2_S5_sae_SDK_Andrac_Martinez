from fpdf import FPDF
import os

class Creation_PDF(FPDF):
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