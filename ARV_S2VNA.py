import pyvisa
import time

class Instrument : 
        def __init__(self, adresse, port,nom, reglage,etat ):
             self.adresse = adresse
             self.port = port
             self.nom = nom
             self.reglage = reglage
             self.etat = etat

class ARV (Instrument):
    def __init__(self, adresse, port, nom, reglage=None, etat=None ):
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
        Calibration automatique sans interface :
        - method: 'open', 'short', 'thru', 'full'
        - port: port concerné par la calibration (1 ou 2)
        - delay: temps en secondes entre chaque étape
        """
        if self.device is None:
            return

        if method.lower() == "open":
            self.device.write("CALC:CORR:COLL:METH SOLT")
            self.device.write(f"CALC:CORR:COLL:PORT {port}")
            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ OPEN")

        elif method.lower() == "short":
            self.device.write("CALC:CORR:COLL:METH SOLT")
            self.device.write(f"CALC:CORR:COLL:PORT {port}")
            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ SHORT")

        elif method.lower() == "thru":
            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ THRU")

        elif method.lower() == "full":
            self.device.write("CALC:CORR:COLL:METH SOLT")
            self.device.write(f"CALC:CORR:COLL:PORT {port}")

            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ OPEN")

            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ SHORT")

            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ LOAD")

            time.sleep(delay)
            self.device.write("CALC:CORR:COLL:ACQ THRU")

            time.sleep(1)
            self.device.write("CALC:CORR:COLL:SAVE")

    def set_frequence(self, freq, span):
        self.device.write(f"SENSE:FREQUENCY:CENTER {freq}")
        self.device.write(f"SENSE:FREQUENCY:SPAN {span}")
 

    def close(self):
        """ Ferme la connexion avec l'ARV """
        if self.device is not None:
            self.device.close()
            print("Connexion fermée.")


S2VNA = ARV("127.0.0.1",5025, "ARV")  
S2VNA.connect()
S2VNA.preset()
S2VNA.set_frequence(175000000, 150000000)
S2VNA.set_calibrage("Open")




