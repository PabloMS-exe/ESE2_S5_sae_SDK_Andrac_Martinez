import pyvisa
import yaml
import re
import numpy as np
import json


class InstrumentBase:
    def __init__(self, resource_name):
        # Nom ou adresse de la ressource VISA (instrument)
        self.resource_name = resource_name

    def set_parameter(self, name, value):
        # Méthode à implémenter dans les sous-classes
        raise NotImplementedError

    def get_parameter(self, name):
        # Méthode à implémenter dans les sous-classes
        raise NotImplementedError

    def measure(self):
        # Méthode à implémenter dans les sous-classes
        raise NotImplementedError


class SimulatedInstrument(InstrumentBase):
    def __init__(self, yaml_path, resource_name):
        super().__init__(resource_name)
        # Lecture du fichier YAML contenant la configuration du simulateur
        with open(yaml_path, 'r') as f:
            self.yaml_data = yaml.safe_load(f)
        # On récupère les infos de l’appareil simulé (ici ARV2TEST)
        self.device = self.yaml_data['devices']['ARV2TEST']
        # État interne de l’instrument (valeurs par défaut)
        self.state = {
            "sparameter": "S21",
            "power": -10,
            "frequency": 868e6
        }

    def GEN_CURVE(self, start, stop, points):
        """Simule une courbe S21 avec une résonance autour de 868 MHz"""
        # Création d’un vecteur de fréquences
        freqs = np.linspace(start, stop, int(points))
        # Génération d’une courbe avec une forme gaussienne simulant une résonance
        values = -20 + 10 * np.exp(-((freqs - 868e6)**2) / (2 * (0.5e6)**2))
        # Conversion en JSON pour imiter une vraie réponse instrument
        return json.dumps({
            "frequencies": freqs.tolist(),
            "values": values.tolist(),
            "parameter": self.state["sparameter"]
        })

    def get_parameter(self, param_name):
        # Recherche de la propriété dans le YAML
        prop = self.device['properties'].get(param_name)
        if not prop or 'getter' not in prop:
            raise ValueError(f"Propriété inconnue : {param_name}")

        # Extraction de la fonction à appeler depuis le champ 'getter'
        r = prop['getter']['r']
        match = re.search(r"\{(\w+)\((.*?)\)\}", r)
        if match:
            func, args = match.groups()
            # Conversion des arguments en float
            args = [float(a) for a in args.split(',')]
            # Appel de la fonction simulée correspondante
            if func == "GEN_CURVE":
                return self.GEN_CURVE(*args)
        # Sinon, on renvoie la valeur actuelle de l’état interne
        return self.state.get(param_name, None)

    def set_parameter(self, param_name, value):
        # Mise à jour d’un paramètre dans l’état de l’instrument
        if param_name in self.device['properties']:
            self.state[param_name] = value
            return "OK"
        raise ValueError(f"Paramètre {param_name} non reconnu.")

    def measure(self):
        # Appelle la fonction de mesure définie dans le YAML et renvoie les données
        return json.loads(self.get_parameter("measure_curve"))


class InstrumentManager:
    def __init__(self, yaml_path):
        # Chargement du fichier YAML principal contenant les ressources disponibles
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        self.resources = config['resources']
        self.yaml_path = yaml_path

    def get_instrument(self, resource_name, simulate=False):
        # Retourne soit un instrument simulé, soit un vrai (non implémenté ici)
        if simulate:
            return SimulatedInstrument(self.yaml_path, resource_name)
        pass


manager = InstrumentManager("instrument.yaml")
# On crée un instrument simulé à partir du YAML
instr = manager.get_instrument("TCPIP::localhost::INSTR", simulate=True)
instr.set_parameter("power", -5)
# On récupère une courbe simulée de mesure
courbe = instr.measure()

# Affichage des résultats simulés
print("Paramètre mesuré :", courbe["parameter"])
print("Nombre de points :", len(courbe["frequencies"]))
print("Premier point :", courbe["frequencies"][0], courbe["values"][0])
