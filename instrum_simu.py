import pyvisa
import yaml
import re
import numpy as np
import json


class InstrumentBase:
    def __init__(self, resource_name):
        self.resource_name = resource_name

    def set_parameter(self, name, value):
        raise NotImplementedError

    def get_parameter(self, name):
        raise NotImplementedError

    def measure(self):
        raise NotImplementedError

class SimulatedInstrument(InstrumentBase):
    def __init__(self, yaml_path, resource_name):
        super().__init__(resource_name)
        with open(yaml_path, 'r') as f:
            self.yaml_data = yaml.safe_load(f)
        self.device = self.yaml_data['devices']['ARV2TEST']
        self.state = {
            "sparameter": "S21",
            "power": -10,
            "frequency": 868e6
        }

    def GEN_CURVE(self, start, stop, points):
        """Simule une courbe S21 avec une résonance autour de 868 MHz"""
        freqs = np.linspace(start, stop, int(points))
        values = -20 + 10 * np.exp(-((freqs - 868e6)**2) / (2 * (0.5e6)**2))
        return json.dumps({
            "frequencies": freqs.tolist(),
            "values": values.tolist(),
            "parameter": self.state["sparameter"]
        })

    def get_parameter(self, param_name):
        prop = self.device['properties'].get(param_name)
        if not prop or 'getter' not in prop:
            raise ValueError(f"Propriété inconnue : {param_name}")

        r = prop['getter']['r']
        match = re.search(r"\{(\w+)\((.*?)\)\}", r)
        if match:
            func, args = match.groups()
            args = [float(a) for a in args.split(',')]
            if func == "GEN_CURVE":
                return self.GEN_CURVE(*args)
        return self.state.get(param_name, None)

    def set_parameter(self, param_name, value):
        if param_name in self.device['properties']:
            self.state[param_name] = value
            return "OK"
        raise ValueError(f"Paramètre {param_name} non reconnu.")

    def measure(self):
        return json.loads(self.get_parameter("measure_curve"))



class InstrumentManager:
    def __init__(self, yaml_path):
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        self.resources = config['resources']
        self.yaml_path = yaml_path

    def get_instrument(self, resource_name, simulate=False):
        if simulate:
            return SimulatedInstrument(self.yaml_path, resource_name)
        pass


# On charge le YAML
manager = InstrumentManager("instrument.yaml")

# On crée un instrument simulé
instr = manager.get_instrument("TCPIP::localhost::INSTR", simulate=True)

# On change un paramètre
instr.set_parameter("power", -5)

# On récupère la courbe simulée
courbe = instr.measure()

print("Paramètre mesuré :", courbe["parameter"])
print("Nombre de points :", len(courbe["frequencies"]))
print("Premier point :", courbe["frequencies"][0], courbe["values"][0])