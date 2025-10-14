import pyvisa
import time
import csv
import numpy as np
from SAE_POO import Instrument, Mesure
from tracer_courbes import TracerCourbes, Gabarit, PDFExporter
# from mesure import S11Measure, FCS21MaxMeasure, DeltaBPMeasure, DeltaBRMeasure

class ARV_S2VNA(Instrument):
    def __init__(self, adresse, port, nom, reglage=None, etat=None):
        super().__init__(adresse, port, nom, reglage, etat)
        self.adresse = adresse
        self.port = port
        self.rm = pyvisa.ResourceManager()
        self.device = None

    def connect(self):
        try:
            # Format de l'adresse : TCPIP0::ip_address::5025::SOCKET
            resource_string = f"TCPIP0::{self.adresse}::{self.port}::SOCKET"
            self.device = self.rm.open_resource(resource_string)
            print(f"Connecté à l'ARV {self.adresse} sur le port {self.port}")
            self.device.write("*IDN?")  # Identification de l'instrument
            print(self.device.read())  # Affiche l'ID de l'ARV
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def preset(self):
        if self.device is None:
            print("Aucune connexion active à l'ARV.")
            return
        try:
            # Commande pour effectuer un preset
            self.device.write("*RST")  # Commande standard pour réinitialiser l'instrument
            print("Oscilloscope réinitialisé.")
        except Exception as e:
            print(f"Erreur lors du preset de l'ARV : {e}")

    def set_calibrage(self, method="full", port=1, delay=5):
        """
        Calibration automatique avec les commandes SENS:CORR:COLL:METH:xxx
        - method possible : open, short, thru, solt1, eres, solt2, trl2
        - port concerné (si nécessaire)
        - delay en secondes entre étapes
        """

        if self.device is None:
            print("Pas de connexion active.")
            return

        # Dictionnaire des méthodes correspondantes aux commandes
        method_commands = {
            "open": "SENS:CORR:COLL:METH:OPEN",
            "short": "SENS:CORR:COLL:METH:SHOR",
            "thru": "SENS:CORR:COLL:METH:THRU",
            "solt1": "SENS:CORR:COLL:METH:SOLT1",
            "eres": "SENS:CORR:COLL:METH:ERES",
            "solt2": "SENS:CORR:COLL:METH:SOLT2",
            "trl2": "SENS:CORR:COLL:METH:TRL2",
        }

        method = method.lower()  # Pour pas avoir de problèmes avec la casse
        if method not in method_commands:
            print(f"Méthode de calibrage inconnue : {method}")
            return

        try:
            # Envoi de la commande de méthode de calibrage
            self.device.write(method_commands[method])
            print(f"Commande de calibration envoyée : {method_commands[method]}")

            # Si la calibration nécessite de spécifier un port, on peut envoyer une commande ici
            # (à vérifier selon la doc de ton ARV)
            if port in [1, 2]:
                self.device.write(f"SENS:CORR:COLL:PORT {port}")
                print(f"Port de calibration défini : {port}")

            time.sleep(delay)

            # Ensuite, tu peux envoyer une commande pour démarrer l'acquisition/calibration selon méthode
            self.device.write("SENS:CORR:COLL:ACQ")
            print("Acquisition de calibration lancée...")

            # Optionnel : tu peux interroger le statut de la calibration
            # par exemple : status = self.device.query("SENS:CORR:COLL:STAT?")
            # et afficher ou gérer le résultat

            time.sleep(delay)

            # Sauvegarde ou validation de la calibration
            self.device.write("SENS:CORR:COLL:SAVE")
            print("Calibration sauvegardée.")

        except Exception as e:
            print(f"Erreur lors de la calibration : {e}")


    def set_frequence(self, freq, span):
        self.device.write(f"SENSE:FREQUENCY:CENTER {freq}")
        self.device.write(f"SENSE:FREQUENCY:SPAN {span}")
    
    def set_parametre_S(self, param_S):  
        #Définir un paramètre S souhaité (S11, S12, S21, S22)
        # 1. Définit le type de conversion (S-parameters)
        self.device.write("CALC:CONV:FUNC S")

        # 2. Définit un paramètre personnalisé avec le S-parameter voulu
        self.device.write(f"CALC:PAR:DEF {param_S}")
        
        # 3. Sélectionne ce paramètre
        self.device.write("CALC:PAR:SEL {param_S}")
        
        # 4. L'affiche dans la trace 1
        self.device.write("DISP:WIND:TRAC1:FEED {param_S}")

        print(f"Paramètre {param_S} défini via CALC:CONV:FUNC S.")  

    def verifier_conformite(self, liste_gabarit):
        """
        Vérifie si la courbe mesurée respecte tous les gabarits.
        Retourne True si conforme, False sinon.
        """
        data = self.charger_donnees_csv()  # suppose que tu as une méthode pour charger tes données
        freqs = data["Frequence"]  # ou la colonne correspondante
        gains = data["Gain"]       # ou la colonne correspondante

        for g in liste_gabarit:
            for f, g_mes in zip(freqs, gains):
                if g.freq_min <= f <= g.freq_max:
                    if not (g.att_min <= g_mes <= g.att_max):
                        return False
        return True
  
    def close(self):
        """ Ferme la connexion avec l'ARV """
        if self.device is not None:
            self.device.close()
            print("Connexion fermée.")

class Mesure_ARV(Mesure):
    def __init__(self,instrument: ARV_S2VNA):
        self.instrument=instrument

    def marker_y(self):
        raw = self.instrument.device.query("CALC:MARK1:Y?")
        return float(str(raw).split(",")[0])

    def setInstrument(self,freq_start, freq_span, cal, paramS):
        self.freq_start = freq_start
        self.freq_span = freq_span
        self.cal = cal 
        self.paramS = paramS
        self.instrument.preset()
        self.instrument.set_frequence(self.freq_start, self.freq_span)
        self.instrument.set_calibrage(self.cal)
        self.instrument.set_parametre_S(self.paramS)


    def get_trace_data(self, filename="mesures.csv"):
        # code pour demander à l’instrument de sauvegarder la trace CSV
        if self.instrument.device is None:
            print("Pas de connexion active.")
            return None
        try:
            self.instrument.device.write(f"MMEM:STOR:FDAT '{filename}'")
            print(f"Fichier {filename} sauvegardé sur l'instrument.")
            return filename
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des mesures : {e}")
            return None
        

# Programme Principal 
S2VNA = ARV_S2VNA("127.0.0.1", 32000, "ARV")  # Création de l'instrument S2VNA
S2VNA.connect()
mesure_S2VNA = Mesure_ARV(S2VNA)

# 2. Demande à l'instrument de sauvegarder la trace dans un fichier CSV
nom_fichier_instrument = "mesures.csv"
fichier_sur_instrument = mesure_S2VNA.get_trace_data(nom_fichier_instrument)

if fichier_sur_instrument is None:
    print("Erreur lors de la sauvegarde des mesures sur l'instrument.")
    exit(1)

print(f"Le fichier {fichier_sur_instrument} a été sauvegardé")

# 3. *** Récupérer manuellement ce fichier sur ta machine ***
#    Exemple : par FTP, USB, ou autre méthode selon ton instrument.

# 4. Charger localement ce fichier CSV sur ton PC (chemin local)
chemin_fichier_local = "E:/BUT_GE2I/SDK_SAE/"  # <-- à modifier selon où tu copies le fichier

# 3. Créer les gabarits
gabarit1 = Gabarit(freq_min=0.0, freq_max=2.2e9, att_min=1.0, att_max=2.0)
gabarit2 = Gabarit(freq_min=2.2e9, freq_max=6.0e9, att_min=-0.8, att_max=0.5)
gabarit3 = Gabarit(freq_min=6.0e9, freq_max=8.0e9, att_min=1.2, att_max=2.2)
liste_gabarit = [gabarit1, gabarit2, gabarit3]

# 4. Tracer la courbe
tracer = TracerCourbes(fichier_csv=chemin_fichier_local, titre="Gain S21 mesuré")
tracer.ajouter_gabarit(liste_gabarit)
tracer.tracer()  # Ne pas oublier de lancer le tracé

# 5. Créer le PDF
pdf = PDFExporter()
pdf.ajouter_texte(
    "Rapport de Mesures Hyperfréquences\n"
    "----------------------------------\n"
    f"Gabarits appliqués :\n"
    f"- [{gabarit1.freq_min/1e9:.1f} GHz – {gabarit1.freq_max/1e9:.1f} GHz] : {gabarit1.att_min} à {gabarit1.att_max} dB\n"
    f"- [{gabarit2.freq_min/1e9:.1f} GHz – {gabarit2.freq_max/1e9:.1f} GHz] : {gabarit2.att_min} à {gabarit2.att_max} dB\n"
    f"- [{gabarit3.freq_min/1e9:.1f} GHz – {gabarit3.freq_max/1e9:.1f} GHz] : {gabarit3.att_min} à {gabarit3.att_max} dB\n"
)
pdf.ajouter_courbe(tracer, "Courbe S21 avec Gabarit")

# 6. Vérification de la conformité du test
conforme = tracer.verifier_conformite(liste_gabarit) if hasattr(tracer, "verifier_conformite") else None

if conforme is not None:
    if conforme:
        pdf.ajouter_texte("\n Le dispositif est **CONFORME** aux spécifications du gabarit.\n")
    else:
        pdf.ajouter_texte("\n Le dispositif est **NON CONFORME** aux spécifications du gabarit.\n")
else:
    pdf.ajouter_texte("\n Impossible de déterminer la conformité (méthode `verifier_conformite` manquante dans `TracerCourbes`).\n")


# 7. Ajouter les résultats au PDF
pdf.ajouter_texte("\nRésultats des Mesures :\n------------------------")

# 8. Générer le PDF final
pdf.generer("rapport_hyperfrequences.pdf")




# S2VNA.preset()
# S2VNA.set_frequence(175000000, 150000000)
# S2VNA.set_calibrage("ShOrT")
# S2VNA.set_parametre_S("S21")
#S2VNA.close() 

