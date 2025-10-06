import os
import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
from datetime import datetime

class CertificatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Certificat")
        
        # Création des champs de formulaire
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.root, text="Nom du technicien").grid(row=0, column=0)
        self.technicien_entry = tk.Entry(self.root)
        self.technicien_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Référence de l'appareil").grid(row=1, column=0)
        self.appareil_entry = tk.Entry(self.root)
        self.appareil_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Numéro de série").grid(row=2, column=0)
        self.serie_entry = tk.Entry(self.root)
        self.serie_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Test 1 :").grid(row=3, column=0)
        self.test1_entry = tk.Entry(self.root)
        self.test1_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Test 2 :").grid(row=4, column=0)
        self.test2_entry = tk.Entry(self.root)
        self.test2_entry.grid(row=4, column=1)

        tk.Label(self.root, text="Test 3 :").grid(row=5, column=0)
        self.test3_entry = tk.Entry(self.root)
        self.test3_entry.grid(row=5, column=1)

        # Bouton pour générer le certificat
        self.generate_button = tk.Button(self.root, text="Générer le certificat", command=self.generer_certificat)
        self.generate_button.grid(row=6, columnspan=2)

    def generer_certificat(self):
        technicien = self.technicien_entry.get()
        appareil = self.appareil_entry.get()
        serie = self.serie_entry.get()
        
        # Récupération des résultats de tests
        tests = {
            "Test de fonctionnalité 1": self.test1_entry.get(),
            "Test de performance": self.test2_entry.get(),
            "Test de sécurité": self.test3_entry.get()
        }
        
        # Générer le PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Certificat de Bon Fonctionnement", ln=True, align='C')

        pdf.ln(10)  # Espacement
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Date du test : {datetime.now().strftime('%d-%m-%Y')}", ln=True)
        pdf.cell(200, 10, f"Nom du technicien : {technicien}", ln=True)
        pdf.cell(200, 10, f"Référence de l'appareil : {appareil}", ln=True)
        pdf.cell(200, 10, f"Numéro de série : {serie}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, "Tests effectués :", ln=True)

        pdf.set_font("Arial", size=10)
        for test, resultat in tests.items():
            pdf.cell(200, 10, f"{test}: {resultat}", ln=True)

        # Verdict final
        verdict = "Bon fonctionnement" if all(result == 'OK' for result in tests.values()) else "À revoir"
        pdf.ln(10)
        pdf.cell(200, 10, f"Verdict final : {verdict}", ln=True)

        # Dossier de sauvegarde
        dossier_sauvegarde = "C:/Users/TonNomUtilisateur/Bureau/certificats"
        os.makedirs(dossier_sauvegarde, exist_ok=True)  # Crée le dossier s'il n'existe pas

        # Sauvegarde du PDF dans le dossier spécifié
        pdf.output(f"{dossier_sauvegarde}/certificat_{appareil}_{serie}.pdf")
        
        messagebox.showinfo("Succès", "Le certificat a été généré et sauvegardé avec succès !")

# Créer l'application Tkinter
root = tk.Tk()
app = CertificatApp(root)
root.mainloop()
