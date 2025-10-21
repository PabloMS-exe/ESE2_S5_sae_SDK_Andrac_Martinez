import pyvisa
import time
from SAE_POO import Resultat

class ResultatARV(Resultat):
    def __init__(self, freq_cible):
        super().__init__()
        from ARV_S2VNA import ARV_S2VNA
        self.instrument = ARV_S2VNA("127.0.0.1", 5025, "ARV")
        self.instrument.connect()
        self.instrument.preset()
        self.instrument.device.timeout = 10000  # 30 s pour commandes longues
        self.freq_cible = freq_cible

        # Import local pour éviter boucle circulaire
        from mesure import S11Mesure, FCS21MaxMeasure, DeltaBPMeasure, DeltaBRMeasure
        self.liste_mesures = [
            S11Mesure(self.instrument),
            FCS21MaxMeasure(self.instrument),
            DeltaBPMeasure(self.instrument),
            DeltaBRMeasure(self.instrument)
        ]

    def _envoyer_commande(self, commande):
        """Commande SCPI sans retour (write)."""
        try:
            self.instrument.device.write(commande)
            time.sleep(0.05)
        except Exception as e:
            print(f"Erreur write('{commande}') : {e}")

    def _safe_query(self, commande, delay=0.2):
        """
        Envoie une commande SCPI et lit la réponse avec délai.
        Utile pour commandes longues qui provoquent VI_ERROR_TMO.
        """
        try:
            self.instrument.device.write(commande)
            time.sleep(delay)
            return self.instrument.device.read()
        except Exception as e:
            print(f"Erreur safe_query('{commande}') : {e}")
            return None

    def get_bande_passante(self):
        """Récupère bande passante et fréquence centrale via SCPI."""
        span_str = self._safe_query("SENS:FREQ:SPAN?")
        centre_str = self._safe_query("SENS:FREQ:CENT?")
        try:
            span = float(span_str) if span_str else None
            centre = float(centre_str) if centre_str else None
        except ValueError:
            span, centre = None, None
        return span, centre

    def get_perte_insertion(self):
        """
        Récupère la perte d'insertion (|S21| en dB) à la fréquence cible via SCPI.
        Assure que S21 est le paramètre actif.
        """
        try:
            # Définir et sélectionner le paramètre S21
            self._envoyer_commande("CALC:PAR:DEF S21, S21")
            self._envoyer_commande("CALC:PAR:SEL S21")

            # Définir la fréquence cible pour la mesure
            self._envoyer_commande(f"SENS:FREQ:CENT {self.freq_cible}")

            # Interroger la magnitude de S21 (en dB) à cette fréquence
            magnitude_str = self._safe_query("CALC:DATA:FDAT?", delay=0.5)

            if not magnitude_str:
                return None

            # La réponse est souvent une liste plate : [re0, im0, re1, im1, ...]
            # On prend le premier point réel + imaginaire
            valeurs = list(map(float, magnitude_str.strip().split(',')))
            if len(valeurs) < 2:
                return None

            re, im = valeurs[0], valeurs[1]
            # Calcul de la magnitude en dB : 20 * log10(|S21|)
            import math
            mag_dB = 20 * math.log10((re**2 + im**2)**0.5)
            return mag_dB

        except Exception as e:
            print(f"Erreur lors de la récupération de la perte d'insertion : {e}")
            return None

    def get_frequence(self):
        """Récupère la fréquence centrale actuelle."""
        freq_str = self._safe_query("SENS:FREQ:CENT?")
        try:
            return float(freq_str) if freq_str else None
        except ValueError:
            return None

    def mesurer(self):
        """
        Effectue toutes les mesures et retourne un dictionnaire uniforme
        clé = nom de la mesure, valeur = {"value": ..., "unit": ...}
        """
        resultats = {}

        # Mesures de base
        bp, cf = self.get_bande_passante()
        pi = self.get_perte_insertion()
        f = self.get_frequence()
        resultats["bande_passante"] = {"value": bp, "unit": "Hz"}
        resultats["centre_freq"] = {"value": cf, "unit": "Hz"}
        resultats["perte_insertion"] = {"value": pi, "unit": "dB"}
        resultats["frequence"] = {"value": f, "unit": "Hz"}

        # Mesures avancées via safe_query() de chaque classe
        for mesure in self.liste_mesures:
            try:
                res = mesure.do_mesures()
                resultats[res['name']] = {"value": res["value"], "unit": res["unit"]}
            except Exception as e:
                print(f"Erreur lors de la mesure {mesure.__class__.__name__} : {e}")
                # On peut mettre None si la mesure échoue
                resultats[mesure.__class__.__name__] = {"value": None, "unit": ""}

        return resultats
