class Gabarit:
    def __init__(self, freq_min, freq_max, att_min, att_max):
        # Définition des bornes du gabarit en fréquence et en atténuation
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.att_min = att_min
        self.att_max = att_max

    def est_dans_gabarit(self, freq, valeur):
        # Vérifie si un point (fréquence, valeur) est à l’intérieur du gabarit
        return (self.freq_min <= freq <= self.freq_max and
                self.att_min <= valeur <= self.att_max)

    def tracer(self, ax, label):
        # Trace les limites du gabarit sur un graphique 
        ax.axvline(self.freq_min, color='r', linestyle='--', alpha=0.5)  # Limite gauche
        ax.axvline(self.freq_max, color='r', linestyle='--', alpha=0.5)  # Limite droite
        ax.axhline(self.att_min, color='g', linestyle='--', alpha=0.5)  # Limite basse
        ax.axhline(self.att_max, color='g', linestyle='--', alpha=0.5)  # Limite haute
        # Remplissage de la zone valide du gabarit en jaune
        ax.fill_between(
            [self.freq_min, self.freq_max],
            self.att_min, self.att_max,
            color='#FFFF00', alpha=0.4, label='Gabarit'
        )
