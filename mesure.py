from SAE_POO import Mesure
from ARV_S2VNA import ARV_S2VNA
import os
import time

class Mesure_ARV(Mesure):
    def __init__(self,instrument: ARV_S2VNA, name =None, unit =None):
        super().__init__(instrument)
        self.name =name
        self.unit = unit
        
    def marker_y(self):
        """Lit la valeur du marqueur actif (en dB par exemple)."""
        try:
            # Activation explicite du marqueur si pas déjà fait
            self.instrument.device.write("CALC:MARK1 ON")
            time.sleep(1)
            
            # S'assurer qu’un calcul est terminé
            self.instrument.device.write("*WAI")

            # Interroger la valeur du marqueur
            raw = self.instrument.device.query("CALC:MARK1:Y?")
            return float(raw.strip())
        except Exception as e:
            print(f"Erreur lors de la lecture du marqueur : {e}")
            return None

    def marker_x_hz(self):
        """Retourne la fréquence (X) du marqueur 1 en Hz."""
        try:
            raw = self.instrument.device.query("CALC:MARK1:X?")
            return float(raw)
        except Exception as e:
            print(f"Erreur lecture marqueur X : {e}")
            return None

    def setInstrument(self,freq_start, freq_span, cal, paramS):
        self.freq_start = freq_start
        self.freq_span = freq_span
        self.cal = cal 
        self.paramS = paramS
        self.instrument.preset()
        self.instrument.set_frequence(self.freq_start, self.freq_span)
        self.instrument.set_calibrage(self.cal)
        self.instrument.set_parametre_S(self.paramS)


    def get_trace_data(self, dossier="F:/BUT_GE2I/SDK_SAE", base_nom = "", extension=".csv"):
        """
        Sauvegarde la trace de mesure avec un nom personnalisé et horodaté.
        Exemple : E:/BUT_GE2I/SDK_SAE/mesure_S21_20251014_153045.csv
        """
        try:
            # Génération du nom de fichier avec date et heure
            nom_fichier = f"{base_nom}{extension}"
            chemin_complet = os.path.join(dossier, nom_fichier)

            # Envoi de la commande à l'instrument
            self.instrument.device.write(f"MMEM:STOR:FDAT '{chemin_complet}'")
            print(f"Fichier sauvegardé : {chemin_complet}")
            return chemin_complet
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des mesures : {e}")
            return None
        

class S11Mesure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="S11", unit="dB")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        self.instrument.set_parametre_S("S11")
        time.sleep(0.2) 
        self.instrument.write("CALC:MARK1:FUNC:TYPE MIN")
        self.instrument.write("CALC:MARK1:FUNC:EXEC")
        val_db = self.marker_y()
        return {"name": self.name, "value": val_db, "unit": self.unit}

class FCS21MaxMeasure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="FC:S21max(MHZ)", unit="MHz")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        try:
            self.instrument.set_parametre_S("S21")
            time.sleep(0.2)     
            self.instrument.device.write("CALC:PAR1:DEF S21")
            print("Paramètre S21 défini via CALC:PAR1:DEF S21")
            
            self.instrument.device.write("CALC:MARK1 ON")
            self.instrument.device.write("CALC:MARK1:FUNC:TYPE MAX")
            self.instrument.device.write("INIT:IMM")
            self.instrument.device.query("*OPC?")

            f0_hz = self.marker_x_hz()

            if f0_hz is None:
                print("⚠️ Lecture de f0 impossible (timeout)")
                return {"name": self.name, "value": None, "unit": self.unit}

            return {"name": self.name, "value": f0_hz / 1e6, "unit": self.unit}

        except Exception as e:
            print(f"Erreur lors de la mesure FCS21Max: {e}")
            return {"name": self.name, "value": None, "unit": self.unit}

class DeltaBPMeasure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="deltaBP(MHZ)", unit="MHz")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        self.instrument.set_parametre_S("S21")
        time.sleep(0.2) 
        self.instrument.device.write("CALC:MARK:BWID ON")
        self.instrument.device.write("CALC:MARK:BWID:REF MAX")
        self.instrument.device.write("CALC:MARK:BWID:THR -3")
        self.instrument.device.write("CALC:MARK:BWID:TYPE BPAS")
        # Lecture de la bande passante
        try:
            raw = self.instrument.write("CALC:MARK1:BWID?")  # commande principale
            raw = self.instrument.read("CALC:MARK1:BWID?")  # commande principale
            if raw is None or raw.strip() == "":
                print("⚠️ BWID non disponible sur cet instrument")
                bw_hz = 0.0
            else:
                bw_hz = float(raw.split(",")[0])
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de la bande passante : {e}")
            bw_hz = 0.0

        return {"name": self.name, "value": bw_hz / 1e6, "unit": "MHz"}

class DeltaBRMeasure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="deltaBR(MHZ)", unit="MHz")

    def do_mesures(self):
        print(self.instrument.query("*IDN?"))
        self.instrument.set_parametre_S("S21")
        time.sleep(0.2) 
        self.instrument.device.write("CALC:MARK:BWID ON")
        self.instrument.device.write("CALC:MARK:BWID:REF MAX")
        self.instrument.device.write("CALC:MARK:BWID:THR -20")
        self.instrument.device.write("CALC:MARK:BWID:TYPE BPAS")
        # Lecture de la bande passante
        try:
            raw = self.instrument.query("CALC:MARK1:BWID?")  # commande principale
            if raw is None or raw.strip() == "":
                print("⚠️ BWID non disponible sur cet instrument")
                bw_hz = 0.0
            else:
                bw_hz = float(raw.split(",")[0])
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de la bande passante : {e}")
            bw_hz = 0.0

        return {"name": self.name, "value": bw_hz / 1e6, "unit": "MHz"}
