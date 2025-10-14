import pyvisa
import numpy as np
import time

class ResultatARV(Resultat):
    def __init__(self, resource_name, freq_cible):
        super().__init__()
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)
        self.instrument.timeout = 5000  # Timeout en millisecondes
        self.freq_cible = freq_cible  # Fréquence cible pour la mesure

    def _envoyer_commande(self, commande):
        """Envoie une commande SCPI et attend une réponse."""
        self.instrument.write(commande)
        time.sleep(0.1)  # Attente pour assurer que la commande est traitée

    def _lire_reponse(self):
        """Lit la réponse de l'instrument."""
        return self.instrument.read()

    def get_bande_passante(self):
        """Récupère la bande passante à -3 dB."""
        self._envoyer_commande("SENS:FREQ:SPAN?")
        span = float(self._lire_reponse())
        self._envoyer_commande("SENS:FREQ:CENT?")
        centre_freq = float(self._lire_reponse())
        return span, centre_freq

    def get_perte_insertion(self):
        """Récupère la perte d'insertion à la fréquence cible."""
        self._envoyer_commande(f"MEAS:FREQ {self.freq_cible}")
        self._envoyer_commande("MEAS:IMPed:LOSS?")
        return float(self._lire_reponse())

    def get_frequence(self):
        """Récupère la fréquence actuelle de l'instrument."""
        self._envoyer_commande("SENS:FREQ:CENT?")
        return float(self._lire_reponse())

    def mesurer(self):
        """Effectue les mesures et retourne les résultats."""
        bande_passante, centre_freq = self.recuperer_bande_passante()
        perte_insertion = self.recuperer_perte_insertion()
        frequence = self.recuperer_frequence()
        return {
            "bande_passante": bande_passante,
            "centre_freq": centre_freq,
            "perte_insertion": perte_insertion,
            "frequence": frequence
        }
    
