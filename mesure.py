from ARV_S2VNA import Mesure_ARV

class S11Measure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="S11", unit="dB")

    def do_mesures(self):
        self.instrument.set_parametre_S("S11")
        self.instrument.query("CALC:MARK1:FUNC:TYPE MIN")
        self.instrument.query("CALC:MARK1:FUNC:EXEC")
        val_db = self.marker_y_db()
        return {"name": self.name, "value": val_db, "unit": self.unit}

class FCS21MaxMeasure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="FC:S21max(MHZ)", unit="MHz")

    def do_mesures(self):
        self.instrument.set_parametre_S("S21")
        self.instrument.device.query("CALC:MARK1:FUNC:TYPE MAX")
        self.instrument.device.query("CALC:MARK1:FUNC:EXEC")
        f0_hz = self.marker_x_hz()
        return {"name": self.name, "value": f0_hz / 1e6, "unit": self.unit}

class DeltaBPMeasure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="deltaBP(MHZ)", unit="MHz")

    def do_mesures(self):
        self.instrument.set_parametre_S("S21")
        self.instrument.device.query("CALC:MARK:BWID ON")
        self.instrument.device.query("CALC:MARK:BWID:REF MAX")
        self.instrument.device.query("CALC:MARK:BWID:THR -3")
        self.instrument.device.query("CALC:MARK:BWID:TYPE BPAS")
        raw = self.instrument.query("CALC:MARK1:BWID:DATA?")
        parts = raw.split(",")
        bw_hz = float(parts[0])
        return {"name": self.name, "value": bw_hz / 1e6, "unit": self.unit}

class DeltaBRMeasure(Mesure_ARV):
    def __init__(self, instrument):
        super().__init__(instrument, name="deltaBR(MHZ)", unit="MHz")

    def do_mesures(self):
        self.instrument.set_parametre_S("S21")
        self.instrument.device.query("CALC:MARK:BWID ON")
        self.instrument.device.query("CALC:MARK:BWID:REF MAX")
        self.instrument.device.query("CALC:MARK:BWID:THR -20")
        self.instrument.device.query("CALC:MARK:BWID:TYPE BPAS")
        raw = self.instrument.query("CALC:MARK1:BWID:DATA?")
        parts = raw.split(",")
        bw_hz = float(parts[0])
        return {"name": self.name, "value": bw_hz / 1e6, "unit": self.unit}