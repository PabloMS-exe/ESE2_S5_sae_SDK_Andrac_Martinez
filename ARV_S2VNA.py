import pyvisa
import time
import csv
from SAE_POO import Instrument


class ARV_S2VNA(Instrument):
    def __init__(self, adresse, port, nom, reglage=None, etat=None):
        super().__init__(adresse, port, nom, reglage, etat)
        self.adresse = adresse
        self.port = port
        self.rm = pyvisa.ResourceManager()
        self.device = None

    # -------------------------------------------------------------------------
    # --- Gestion connexion VISA
    # -------------------------------------------------------------------------
    def connect(self):
        try:
            resource_string = f"TCPIP0::{self.adresse}::{self.port}::SOCKET"
            self.device = self.rm.open_resource(resource_string)
            print(f"Connecté à l'ARV {self.adresse} sur le port {self.port}")
            self.device.write("*IDN?")
            print(self.device.read())
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def close(self):
        """ Ferme la connexion avec l'ARV """
        if self.device is not None:
            self.device.close()
            print("Connexion fermée.")

    # Wrappers PyVISA (pour compatibilité avec les classes de mesure)

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

    # Commandes instrument spécifiques

    def preset(self):
        if self.device is None:
            print("Aucune connexion active à l'ARV.")
            return
        try:
            self.device.write("*RST")
            print("Instrument réinitialisé (preset).")
        except Exception as e:
            print(f"Erreur lors du preset de l'ARV : {e}")

    def set_calibrage(self, method="full", port=1, delay=5):
        """
        Calibration automatique :
        method : open, short, thru, solt1, eres, solt2, trl2
        """
        if self.device is None:
            print("Pas de connexion active.")
            return

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
            self.write(method_commands[method])
            print(f"Commande de calibration envoyée : {method_commands[method]}")

            if port in [1, 2]:
                self.write(f"SENS:CORR:COLL:PORT {port}")
                print(f"Port de calibration défini : {port}")

            time.sleep(delay)
            self.write("SENS:CORR:COLL:ACQ")
            print("Acquisition de calibration lancée...")

            time.sleep(delay)
            self.write("SENS:CORR:COLL:SAVE")
            print("Calibration sauvegardée.")

        except Exception as e:
            print(f"Erreur lors de la calibration : {e}")

    def set_frequence(self, freq, span):
        """Définit la fréquence centrale et l’étendue de balayage."""
        self.write(f"SENS:FREQ:CENT {freq}")
        self.write(f"SENS:FREQ:SPAN {span}")

    def set_parametre_S(self, param_S):
        """
        Définit le paramètre S à mesurer (S11, S12, S21, S22)
        """
        self.write("CALC:CONV:FUNC S")
        self.write(f"CALC:PAR:DEF {param_S}")
        self.write(f"CALC:PAR:SEL {param_S}")  # <-- corrigé ici (ajout du f)
        self.write(f"DISP:WIND:TRAC1:FEED {param_S}")
        print(f"Paramètre {param_S} défini via CALC:CONV:FUNC S.")
