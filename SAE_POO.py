import pyvisa
import reportlab
import fpdf 


class Resultat : 
    def __init__(self):
        pass
    def setReport(self):
        pass

class Mesure : 
    def __init__(self, instrument):
        self.instrument = instrument
    def getResult(self):
        pass
    def setInstrument(self):
        pass

class Instrument : 
        def __init__(self, adresse, port,nom, reglage, etat ):
             self.adresse = adresse
             self.port = port
             self.nom = nom
             self.reglage = reglage
             self.etat = etat


class Rapport : 
    def __init__(self):
         pass
    def includeResultat(self):
         pass

resourceManager = pyvisa.ResourceManager()
list = resourceManager.list_resources()
print(list)