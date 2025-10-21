from tracer_courbes import TracerCourbes
from PDF import Creation_PDF
from gabarit import Gabarit
from ARV_S2VNA import ARV_S2VNA
from resultat_arv import ResultatARV
from mesure import Mesure_ARV, S11Mesure, DeltaBPMeasure, DeltaBRMeasure
from datetime import datetime

# Programme Principal 
S2VNA = ARV_S2VNA("127.0.0.1", 5025, "ARV")  # Création de l'instrument S2VNA
S2VNA.connect()
param_S = input("Choisissez une des paramètre S  (S11;S21;S12;S22) : ")
S2VNA.set_parametre_S(param_S)
mesure_S2VNA = Mesure_ARV(S2VNA)

# 2. Demande à l'instrument de sauvegarder la trace dans un fichier CSV
chemin_local = "E:/BUT_GE2I/SDK_SAE/mesures/"
nom_fichier = "mes"
fichier_sur_instrument = mesure_S2VNA.get_trace_data(chemin_local, base_nom = nom_fichier)

if fichier_sur_instrument is None:
    print("Erreur lors de la sauvegarde des mesures sur l'instrument.")
    exit(1)

# # 3. Créer les gabarits
gabarit1 = Gabarit(freq_min=0.0, freq_max=2.8e9, att_min=-30, att_max=10.0)
gabarit2 = Gabarit(freq_min=3.2e9, freq_max=5.5e9, att_min=-80, att_max=-5)
gabarit3 = Gabarit(freq_min=5.90e9, freq_max=9.0e9, att_min=-30, att_max=10.0)
liste_gabarit = [gabarit1, gabarit2, gabarit3]

# # 4. Tracer la courbe
chemin_local_fichier = f"E:/BUT_GE2I/SDK_SAE/mesures/{nom_fichier}.csv"
tracer = TracerCourbes(fichier_csv=chemin_local_fichier, titre=f"Gain {param_S} mesuré")
tracer.ajouter_gabarit(liste_gabarit)
tracer.tracer()  # Ne pas oublier de lancer le tracé

# # 5. Créer le PDF
pdf = Creation_PDF()
pdf.ajouter_page()
nom_technicien = input("Entrez le nom du technicien : ")
pdf.set_xy(10, 10); pdf.cell(100, 10, f"Le technicien est : {nom_technicien}", ln=0)
pdf.set_xy(150, 10); pdf.cell(50, 10, f"Date : {datetime.today().strftime('%d/%m/%Y')}", align='R')
pdf.ln(10)  # ajoute un saut de ligne vertical de 10 mm
pdf.multi_cell(0, 10, "Rapport de Mesures Hyperfréquences :\n------------------------", align='C')
pdf.ajouter_texte(
    f"Gabarits appliqués :\n"
    f"- [{gabarit1.freq_min/1e9:.1f} GHz – {gabarit1.freq_max/1e9:.1f} GHz] : {gabarit1.att_min} à {gabarit1.att_max} dB\n"
    f"- [{gabarit2.freq_min/1e9:.1f} GHz – {gabarit2.freq_max/1e9:.1f} GHz] : {gabarit2.att_min} à {gabarit2.att_max} dB\n"
    f"- [{gabarit3.freq_min/1e9:.1f} GHz – {gabarit3.freq_max/1e9:.1f} GHz] : {gabarit3.att_min} à {gabarit3.att_max} dB\n"
)
pdf.ajouter_courbe(tracer, f"Courbe {param_S} avec Gabarit")

# # 6. Vérification de la conformité du test
conforme = tracer.verifier_conformite(liste_gabarit) if hasattr(tracer, "verifier_conformite") else None

if conforme is not None:
    if conforme:
        pdf.ajouter_texte("\n Le dispositif est conforme aux spécifications du gabarit.\n")
    else:
        pdf.ajouter_texte("\n Le dispositif est non conforme aux spécifications du gabarit.\n")
else:
    pdf.ajouter_texte("\n Impossible de déterminer la conformité (méthode `verifier_conformite` manquante dans `TracerCourbes`).\n")


# # 7. Ajouter les résultats au PDF
pdf.ajouter_page()
pdf.multi_cell(0, 10, "Résultats des Mesures :\n------------------------", align='C')  #Crée un texte centré


#Pose bcp de problèmes : 

resultat = ResultatARV(1000e6)  #1Ghz
donnees = resultat.mesurer()
bp = donnees["bande_passante"]["value"]
cf = donnees["centre_freq"]["value"]
pi = donnees["perte_insertion"]["value"]
f  = donnees["frequence"]["value"]
pdf.ajouter_texte( f"- La fréquence choisie est :{f} GHz\n")  #Renverra None car le simulateur ne répond pas aux commandes query
pdf.ajouter_texte( f"- La fréquence centrale est :{cf} GHz\n")
pdf.ajouter_texte( f"- La bande passante est :{bp} dB\n")
pdf.ajouter_texte( f"- La perte d'insertion est :{pi} dB\n")


# # 8. Générer le PDF final
pdf.generer("E:/BUT_GE2I/SDK_SAE/test_rapports/rapports_SAE_2.pdf")  # endroit de sauvegarde


