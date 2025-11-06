from SAE_POO import Mesure
from ARV_S2VNA import ARV_S2VNA
import os
import time

class Mesure_ARV(Mesure):
    # Sert à contrôler l'instrument et lire les mesures
    def __init__(self, instrument: ARV_S2VNA, name=None, unit=None):
        super().__init__(instrument)
        self.name = name      # Nom de la mesure (ex: S11, S21…)
        self.unit = unit      # Unité de mesure (ex: dB, MHz…)

    def marker_y(self):
        """Lit la valeur du marqueur """
        try:
            # Active le marqueur 1 sur le graphe
            self.instrument.device.write("CALC:MARK1 ON")
            time.sleep(1)  # On attend un peu pour être sûr que c’est pris en compte

            # Attend que l’appareil ait fini ses calculs
            self.instrument.device.write("*WAI")

            # Demande la valeur du marqueur (axe Y)
            raw = self.instrument.device.query("CALC:MARK1:Y?")
            return float(raw.strip())  # On enlève les espaces et on convertit en nombre
        except Exception as e:
            print(f"Erreur lors de la lecture du marqueur : {e}")
            return None

    def marker_x_hz(self):
        """Lit la fréquence du marqueur en Hertz."""
        try:
            raw = self.instrument.device.query("CALC:MARK1:X?")
            return float(raw)
        except Exception as e:
            print(f"Erreur lecture marqueur X : {e}")
            return None

    def setInstrument(self, freq_start, freq_span, cal, paramS):
        """Configure l’instrument avant la mesure."""
        self.freq_start = freq_start  # fréquence de départ
        self.freq_span = freq_span    # largeur de bande
        self.cal = cal                # type de calibration
        self.paramS = paramS          # paramètre S choisi (S11, S21…)

        # Réinitialise l’appareil et applique les réglages
        self.instrument.preset()
        self.instrument.set_frequence(self.freq_start, self.freq_span)
        self.instrument.set_calibrage(self.cal)
        self.instrument.set_parametre_S(self.paramS)

    def get_trace_data(self, dossier="F:/BUT_GE2I/SDK_SAE", base_nom="", extension=".csv"):

        #Sauvegarde la courbe mesurée dans un fichier CSV
        try:
            # Crée le nom complet du fichier
            nom_fichier = f"{base_nom}{extension}"
            chemin_complet = os.path.join(dossier, nom_fichier)

            # Commande envoyée à l’appareil pour sauvegarder la courbe
            self.instrument.device.write(f"MMEM:STOR:FDAT '{chemin_complet}'")
            print(f"Fichier sauvegardé : {chemin_complet}")
            return chemin_complet
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des mesures : {e}")
            return None

class S11Mesure(Mesure_ARV):
    # Sert à mesurer le paramètre S11 (taux de réflexion)
    def __init__(self, instrument):
        super().__init__(instrument, name="S11", unit="dB")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))  # Vérifie la connexion
        self.instrument.set_parametre_S("S11")  # Sélectionne S11
        time.sleep(0.2)

        # Cherche le minimum (le point le plus bas de la courbe)
        self.instrument.write("CALC:MARK1:FUNC:TYPE MIN")
        self.instrument.write("CALC:MARK1:FUNC:EXEC")

        # Lit la valeur du marqueur
        val_db = self.marker_y()
        return {"name": self.name, "value": val_db, "unit": self.unit}

class FCS21MaxMeasure(Mesure_ARV):
    # Sert à trouver la fréquence où S21 est au maximum
    def __init__(self, instrument):
        super().__init__(instrument, name="FC:S21max(MHZ)", unit="MHz")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        try:
            self.instrument.set_parametre_S("S21")
            time.sleep(0.2)
            self.instrument.device.write("CALC:PAR1:DEF S21")
            print("Paramètre S21 défini.")

            # Active le marqueur et cherche le maximum
            self.instrument.device.write("CALC:MARK1 ON")
            self.instrument.device.write("CALC:MARK1:FUNC:TYPE MAX")

            # Lance la mesure et attend la fin
            self.instrument.device.write("INIT:IMM")
            self.instrument.device.query("*OPC?")

            # Récupère la fréquence du marqueur
            f0_hz = self.marker_x_hz()

            if f0_hz is None:
                print("Lecture de la fréquence impossible.")
                return {"name": self.name, "value": None, "unit": self.unit}

            return {"name": self.name, "value": f0_hz / 1e6, "unit": self.unit}  # converti en MHz

        except Exception as e:
            print(f"Erreur lors de la mesure FCS21Max: {e}")
            return {"name": self.name, "value": None, "unit": self.unit}

class DeltaBPMeasure(Mesure_ARV):
    # Sert à mesurer la bande passante à -3 dB
    def __init__(self, instrument):
        super().__init__(instrument, name="deltaBP(MHZ)", unit="MHz")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        self.instrument.set_parametre_S("S21")
        time.sleep(0.2)

        # Réglage du mode "bande passante"
        self.instrument.device.write("CALC:MARK:BWID ON")
        self.instrument.device.write("CALC:MARK:BWID:REF MAX")
        self.instrument.device.write("CALC:MARK:BWID:THR -3")  # seuil -3 dB
        self.instrument.device.write("CALC:MARK:BWID:TYPE BPAS")

        # Lecture de la bande passante
        try:
            raw = self.instrument.query("CALC:MARK1:BWID?")
            if raw is None or raw.strip() == "":
                print("Bande passante non disponible.")
                bw_hz = 0.0
            else:
                bw_hz = float(raw.split(",")[0])
        except Exception as e:
            print(f"Erreur lors de la lecture de la bande passante : {e}")
            bw_hz = 0.0

        return {"name": self.name, "value": bw_hz / 1e6, "unit": "MHz"}

class DeltaBRMeasure(Mesure_ARV):
    # Sert à mesurer la bande à -20 dB (réjection)
    def __init__(self, instrument):
        super().__init__(instrument, name="deltaBR(MHZ)", unit="MHz")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        self.instrument.set_parametre_S("S21")
        time.sleep(0.2)

        # Réglage du mode "bande réjection"
        self.instrument.device.write("CALC:MARK:BWID ON")
        self.instrument.device.write("CALC:MARK:BWID:REF MAX")
        self.instrument.device.write("CALC:MARK:BWID:THR -20")  # seuil -20 dB
        self.instrument.device.write("CALC:MARK:BWID:TYPE BPAS")

        # Lecture de la bande à -20 dB
        try:
            raw = self.instrument.query("CALC:MARK1:BWID?")
            if raw is None or raw.strip() == "":
                print("Bande passante non disponible.")
                bw_hz = 0.0
            else:
                bw_hz = float(raw.split(",")[0])
        except Exception as e:
            print(f"Erreur lors de la lecture de la bande à -20 dB : {e}")
            bw_hz = 0.0

        return {"name": self.name, "value": bw_hz / 1e6, "unit": "MHz"}
