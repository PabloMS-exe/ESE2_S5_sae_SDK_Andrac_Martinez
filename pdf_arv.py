import os
import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
from datetime import datetime
import pyvisa
import time

# Classe pour gérer l'appareil ARV
class ARV:
    def __init__(self, ip, port=5025):
        self.ip = ip
        self.port = port
        self.rm = pyvisa.ResourceManager()
        self.device = None

    def connect(self):
        try:
            resource_string = f"TCPIP0::{self.ip}::{self.port}::SOCKET"
            self.device = self.rm.open_resource(resource_string)
            self.device.timeout = 5000
            print(f"Connecté à l'ARV {self.ip}")
            self.device.write("*IDN?")
            print(self.device.read())
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def preset(self):
        if self.device:
            self.device.write("*RST")
            print("Oscilloscope réinitialisé.")

    def set_calibrage(self, method="full", port=1, delay=2):
        if not self.device:
            return
        self.device.write("CALC:CORR:COLL:METH SOLT")
        self.device.write(f"CALC:CORR:COLL:PORT {port}")
        if method.lower() == "open":
            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ OPEN")
        elif method.lower() == "short":
            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ SHORT")
        elif method.lower() == "thru":
            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ THRU")
        elif method.lower() == "full":
            steps = ["OPEN", "SHORT", "LOAD", "THRU"]
            for step in steps:
                time.sleep(delay)
                self.device.write(f"CALC:CORR:COLL:ACQ {step}")
            time.sleep(1)
            self.device.write("CALC:CORR:COLL:SAVE")

    def set_frequence(self, freq, span):
        self.device.write(f"SENSE:FREQUENCY:CENTER {freq}")
        self.device.write(f"SENSE:FREQUENCY:SPAN {span}")

    def close(self):
        if self.device:
            self.device.close()
            print("Connexion fermée.")

# Classe principale de l'application
class CertificatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Certificat + ARV")

        self.arv = ARV("127.0.0.1")  # à adapter à l’IP réelle
        self.arv.connect()

        self.create_widgets()

    def create_widgets(self):
        # Champs info
        champs = [
            ("Nom du technicien", "technicien_entry"),
            ("Référence de l'appareil", "appareil_entry"),
            ("Numéro de série", "serie_entry"),
            ("Fréquence (Hz)", "frequence_entry"),
            ("Span (Hz)", "span_entry"),
            ("Méthode de calibration", "calibration_entry"),
        ]
        self.entries = {}

        for i, (label, attr) in enumerate(champs):
            tk.Label(self.root, text=label).grid(row=i, column=0)
            entry = tk.Entry(self.root)
            entry.grid(row=i, column=1)
            self.entries[attr] = entry

        # Champs test
        tk.Label(self.root, text="Test 1 :").grid(row=6, column=0)
        self.test1_entry = tk.Entry(self.root)
        self.test1_entry.grid(row=6, column=1)

        tk.Label(self.root, text="Test 2 :").grid(row=7, column=0)
        self.test2_entry = tk.Entry(self.root)
        self.test2_entry.grid(row=7, column=1)

        tk.Label(self.root, text="Test 3 :").grid(row=8, column=0)
        self.test3_entry = tk.Entry(self.root)
        self.test3_entry.grid(row=8, column=1)

        self.generate_button = tk.Button(self.root, text="Lancer test + Générer PDF", command=self.generer_certificat)
        self.generate_button.grid(row=9, columnspan=2)

    def generer_certificat(self):
        technicien = self.entries["technicien_entry"].get()
        appareil = self.entries["appareil_entry"].get()
        serie = self.entries["serie_entry"].get()
        freq = self.entries["frequence_entry"].get()
        span = self.entries["span_entry"].get()
        calibration = self.entries["calibration_entry"].get().lower()

        # Envoi des paramètres à l'appareil
        try:
            self.arv.preset()
            self.arv.set_frequence(freq, span)
            self.arv.set_calibrage(calibration)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la communication avec l'instrument : {e}")
            return

        # Résultats manuels
        tests = {
            "Test de fonctionnalité 1": self.test1_entry.get(),
            "Test de performance": self.test2_entry.get(),
            "Test de sécurité": self.test3_entry.get()
        }

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Certificat de Bon Fonctionnement", ln=True, align='C')

        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Date : {datetime.now().strftime('%d-%m-%Y')}", ln=True)
        pdf.cell(200, 10, f"Technicien : {technicien}", ln=True)
        pdf.cell(200, 10, f"Réf Appareil : {appareil}", ln=True)
        pdf.cell(200, 10, f"Numéro de série : {serie}", ln=True)
        pdf.ln(5)
        pdf.cell(200, 10, f"Fréquence : {freq} Hz", ln=True)
        pdf.cell(200, 10, f"Span : {span} Hz", ln=True)
        pdf.cell(200, 10, f"Calibration : {calibration.upper()}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 10, "Résultats des tests :", ln=True)
        for test, resultat in tests.items():
            pdf.cell(200, 10, f"{test} : {resultat}", ln=True)

        verdict = "Bon fonctionnement" if all(v == 'OK' for v in tests.values()) else "À revoir"
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"Verdict : {verdict}", ln=True)

        # Sauvegarde
        dossier_sauvegarde = "E:/BUT_GE2I/SDK/test_rapports"
        os.makedirs(dossier_sauvegarde, exist_ok=True)
        pdf.output(f"{dossier_sauvegarde}/certificat_{appareil}_{serie}.pdf")

        messagebox.showinfo("Succès", "Le certificat a été généré avec succès.")

        self.arv.close()

#pp
root = tk.Tk()
app = CertificatApp(root)
root.mainloop()
