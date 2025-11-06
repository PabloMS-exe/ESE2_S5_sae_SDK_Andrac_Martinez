import pyvisa
import time
from SAE_POO import Resultat

class ResultatARV(Resultat):
    def __init__(self, freq_cible):
        super().__init__()

        # Import de la classe de l’instrument (analyseur ARV)
        from ARV_S2VNA import ARV_S2VNA
        # Connexion à l’appareil ARV via son adresse IP
        self.instrument = ARV_S2VNA("127.0.0.1", 5025, "ARV")
        self.instrument.connect()
        self.instrument.preset()
        self.instrument.device.timeout = 10000  # Temps d’attente (10 secondes)
        self.freq_cible = freq_cible

        # Import local des classes de mesure pour éviter une boucle entre fichiers
        from mesure import S11Mesure, FCS21MaxMeasure, DeltaBPMeasure, DeltaBRMeasure

        # Liste des mesures à effectuer
        self.liste_mesures = [
            S11Mesure(self.instrument),
            FCS21MaxMeasure(self.instrument),
            DeltaBPMeasure(self.instrument),
            DeltaBRMeasure(self.instrument)
        ]

    def _envoyer_commande(self, commande):
        """Envoie une commande à l’appareil (sans lire de réponse)."""
        try:
            self.instrument.device.write(commande)
            time.sleep(0.05)
        except Exception as e:
            print(f"Erreur lors de l’envoi de la commande '{commande}' : {e}")

    def _safe_query(self, commande, delay=0.2):
        """Envoie une commande à l’appareil et lit la réponse après un petit délai.Sert pour éviter les erreurs quand la commande met du temps à répondre."""
        try:
            self.instrument.device.write(commande)
            time.sleep(delay)
            return self.instrument.device.read()
        except Exception as e:
            print(f"Erreur lors de la commande '{commande}' : {e}")
            return None

    def get_bande_passante(self):
        """Récupère la bande passante et la fréquence centrale depuis l’appareil."""
        span_str = self._safe_query("SENS:FREQ:SPAN?")
        centre_str = self._safe_query("SENS:FREQ:CENT?")
        try:
            span = float(span_str) if span_str else None
            centre = float(centre_str) if centre_str else None
        except ValueError:
            span, centre = None, None
        return span, centre

    def get_perte_insertion(self):
        """Mesure la perte d’insertion (S21 en dB) à la fréquence choisie.Cela correspond à la perte du signal à travers le filtre."""
        try:
            # Sélectionne le paramètre S21 sur l’appareil
            self._envoyer_commande("CALC:PAR:DEF S21, S21")
            self._envoyer_commande("CALC:PAR:SEL S21")

            # Définit la fréquence de mesure
            self._envoyer_commande(f"SENS:FREQ:CENT {self.freq_cible}")

            # Demande les données S21 au format brut
            magnitude_str = self._safe_query("CALC:DATA:FDAT?", delay=0.5)
            if not magnitude_str:
                return None

            # Réponse = une série de valeurs : re0, im0, re1, im1, ...
            valeurs = list(map(float, magnitude_str.strip().split(',')))
            if len(valeurs) < 2:
                return None

            re, im = valeurs[0], valeurs[1]

            # Calcule la magnitude en dB : 20 * log10(|S21|)
            import math
            mag_dB = 20 * math.log10((re**2 + im**2)**0.5)
            return mag_dB

        except Exception as e:
            print(f"Erreur pendant la mesure de la perte d’insertion : {e}")
            return None

    def get_frequence(self):
        """Récupère la fréquence centrale actuelle de l’appareil."""
        freq_str = self._safe_query("SENS:FREQ:CENT?")
        try:
            return float(freq_str) if freq_str else None
        except ValueError:
            return None

    def mesurer(self):
        """Fait toutes les mesures (bande passante, fréquence, pertes, etc.) et renvoie les résultats dans un dictionnaire clair."""
        resultats = {}

        # Mesures de base (faites directement par SCPI)
        bp, cf = self.get_bande_passante()
        pi = self.get_perte_insertion()
        f = self.get_frequence()
        resultats["bande_passante"] = {"value": bp, "unit": "Hz"}
        resultats["centre_freq"] = {"value": cf, "unit": "Hz"}
        resultats["perte_insertion"] = {"value": pi, "unit": "dB"}
        resultats["frequence"] = {"value": f, "unit": "Hz"}

        # Mesures avancées (faites par les autres classes de mesure)
        for mesure in self.liste_mesures:
            try:
                res = mesure.do_mesures()
                resultats[res['name']] = {"value": res["value"], "unit": res["unit"]}
            except Exception as e:
                print(f"Erreur pendant la mesure {mesure.__class__.__name__} : {e}")
                resultats[mesure.__class__.__name__] = {"value": None, "unit": ""}

        return resultats
