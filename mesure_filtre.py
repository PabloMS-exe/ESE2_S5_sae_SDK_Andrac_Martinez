import pyvisa
import time

# Classe pour la communication avec l'ARV
class CommunicationARV:
    def __init__(self, adresse, port):
        self.adresse = adresse
        self.port = port
        self.rm = pyvisa.ResourceManager()
        self.device = None

    def connect(self):
        """ Connexion à l'ARV via VISA """
        try:
            resource_string = f"TCPIP0::{self.adresse}::{self.port}::SOCKET"
            self.device = self.rm.open_resource(resource_string)
            print(f"Connecté à l'ARV {self.adresse} sur le port {self.port}")
            self.device.write("*IDN?")  # Identification de l'instrument
            print(self.device.read())  # Lire et afficher l'ID de l'ARV
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def get_resultat(self, param):
        """ Récupère les résultats du paramètre depuis l'ARV """
        result = self.device.query(param)  # Utilisation de query pour envoyer la commande et obtenir la réponse
        print(f"Résultat de {param}: {result}")
        return float(result)

    def close(self):
        """ Ferme la connexion avec l'ARV """
        if self.device is not None:
            self.device.close()
            print("Connexion fermée.")


# Classe pour gérer les mesures des filtres et récupérer les valeurs de l'ARV
class MesureFiltre(CommunicationARV):
    def __init__(self, adresse, port):
        # Initialisation de la classe CommunicationARV pour la communication avec l'ARV
        super().__init__(adresse, port)

    def recuperer_mesures(self):
        """ Récupère les résultats du filtre simulé sur l'ARV """
        # Lire les mesures du filtre simulé par l'ARV
        frequence_centrale = self.get_resultat("SENS:FREQ:CENT")
        bande_3dB = self.get_resultat("SENS:FREQ:SPAN")  # Bande passante à -3 dB
        perte_insertion = self.get_resultat("S21:INSL")  # Pertes d'insertion (S21)

        return frequence_centrale, bande_3dB, perte_insertion


# Exemple d'utilisation avec communication à l'ARV

# Crée une instance de la classe MesureFiltre pour se connecter à l'ARV
filtre = MesureFiltre(
    adresse="127.0.0.1",   # Adresse IP de l'ARV
    port=5025              # Port de communication (par défaut 5025)
)

# Connexion à l'ARV
filtre.connect()

# Récupération des mesures du filtre simulé par l'ARV
frequence_centrale, bande_3dB, perte_insertion = filtre.recuperer_mesures()

# Affichage des mesures récupérées
print(f"Fréquence centrale : {frequence_centrale} Hz")
print(f"Bande passante à -3 dB : {bande_3dB} Hz")
print(f"Pertes d'insertion (S21) : {perte_insertion} dB")


