import pyvisa
import time
import csv
from SAE_POO import Instrument


class ARV_S2VNA(Instrument):
    def __init__(self, adresse, port, nom, reglage=None, etat=None):
        super().__init__(adresse, port, nom, reglage, etat)
        self.adresse = adresse
        self.port = port
        self.rm = pyvisa.ResourceManager()  # Création du gestionnaire VISA pour accéder aux instruments
        self.device = None                  # L’objet représentant l’instrument connecté

    def connect(self):
        """ Etablie la connexion avec l'ARV """
        try:
            # Construction de la chaîne de connexion TCP/IP pour VISA
            resource_string = f"TCPIP0::{self.adresse}::{self.port}::SOCKET"
            self.device = self.rm.open_resource(resource_string)
            print(f"Connecté à l'ARV {self.adresse} sur le port {self.port}")
            # Vérification de la connexion en demandant l'identité de l'appareil
            self.device.write("*IDN?")
            print(self.device.read())
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def close(self):
        """ Ferme la connexion avec l'ARV """
        if self.device is not None:
            self.device.close()
            print("Connexion fermée.")

    # Wrappers PyVISA (sert à la compatibilité avec les classes de mesure)

    def write(self, cmd: str):
        """Envoie une commande SCPI à l’instrument."""
        if self.device is not None:
            self.device.write(cmd)
        else:
            raise ConnectionError("Instrument non connecté")

    def read(self) -> str:
        """Lit la réponse de l’instrument."""
        if self.device is not None:
            return self.device.read()
        else:
            raise ConnectionError("Instrument non connecté")

    def query(self, cmd: str) -> str:
        """Envoie une requête SCPI et retourne la réponse."""
        if self.device is not None:
            return self.device.query(cmd)
        else:
            raise ConnectionError("Instrument non connecté")

    def preset(self):
        """Réinitialise l’instrument à son état par défaut"""
        if self.device is None:
            print("Aucune connexion active à l'ARV.")
            return
        try:
            self.device.write("*RST")
            print("Instrument réinitialisé (preset).")
        except Exception as e:
            print(f"Erreur lors du preset de l'ARV : {e}")

    def set_calibrage(self, method="full", port=1, delay=5):
        """Calibration automatique : method : open, short, thru, solt1, eres, solt2, trl2 """
        if self.device is None:
            print("Pas de connexion active.")
            return

        # Dictionnaire reliant les méthodes de calibration aux commandes SCPI
        method_commands = {
            "open": "SENS:CORR:COLL:METH:OPEN",
            "short": "SENS:CORR:COLL:METH:SHOR",
            "thru": "SENS:CORR:COLL:METH:THRU",
            "solt1": "SENS:CORR:COLL:METH:SOLT1",
            "eres": "SENS:CORR:COLL:METH:ERES",
            "solt2": "SENS:CORR:COLL:METH:SOLT2",
            "trl2": "SENS:CORR:COLL:METH:TRL2",
        }

        method = method.lower()
        if method not in method_commands:
            print(f"Méthode de calibrage inconnue : {method}")
            return

        try:
            # Envoie de la commande correspondant à la méthode choisie
            self.write(method_commands[method])
            print(f"Commande de calibration envoyée : {method_commands[method]}")

            # Définition du port utilisé pour la calibration
            if port in [1, 2]:
                self.write(f"SENS:CORR:COLL:PORT {port}")
                print(f"Port de calibration défini : {port}")

            # Pause pour laisser le temps à la mesure de se stabiliser
            time.sleep(delay)
            self.write("SENS:CORR:COLL:ACQ")
            print("Acquisition de calibration lancée...")

            # Pause avant sauvegarde du calibrage
            time.sleep(delay)
            self.write("SENS:CORR:COLL:SAVE")
            print("Calibration sauvegardée.")

        except Exception as e:
            print(f"Erreur lors de la calibration : {e}")

    def set_frequence(self, freq, span):
        """Définit la fréquence centrale et l’étendue de balayage."""
        # Commandes SCPI pour régler la fréquence du VNA
        self.write(f"SENS:FREQ:CENT {freq}")
        self.write(f"SENS:FREQ:SPAN {span}")

    def set_parametre_S(self, param_S):
        """ Définit le paramètre S à mesurer (S11, S12, S21, S22)"""
        # Configuration du type de mesure et affichage sur l’écran du VNA
        self.write("CALC:CONV:FUNC S")
        self.write(f"CALC:PAR:DEF {param_S}")
        self.write(f"CALC:PAR:SEL {param_S}")  # Sélection du paramètre défini
        self.write(f"DISP:WIND:TRAC1:FEED {param_S}")  # Affichage sur la fenêtre de trace
        print(f"Paramètre {param_S} défini via CALC:CONV:FUNC S.")
