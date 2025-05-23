import asyncio
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
import agent_ia_test_recup as agent
import os
import json
from datetime import datetime
from agent_ia_test_recup import answer_sport_question
from agent_ia_test_recup import answer_association_question
import random
import webbrowser  # Pour ouvrir les liens

class UniversityChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistant Universitaire Paris Nanterre")
        self.root.geometry("1000x600")  # Augmentation de la largeur pour accommoder le panneau d'historique
        self.root.configure(bg="white")  # Fond blanc pour toute l'application

        # Chargement des données
        self.data = agent.load_data_from_file()
        self.cached_data = agent.load_cached_data()

        # Historique des conversations
        self.conversation_history = self.load_conversation_history()
        self.current_conversation_id = None
        self.title_label = None
        self.subtitle_label = None

        # URLs par défaut si aucune n'est fournie
        self.urls = {
            "https://api.parisnanterre.fr/aide-a-la-vie-etudiante": ["service", "aide", "vie étudiante", "aide université", "aide étudiant", "orientation", "bien-être étudiant", "accompagnement"],
            "https://api.parisnanterre.fr/accueil-sha": ["service", "handicap", "sha", "aide", "accessibilité", "inclusion", "étudiants en situation de handicap"],
            "https://aca2.parisnanterre.fr/associations/accompagnement-des-associations-etudiantes/creer-domicilier-renouveler-son-association-etudiante#:~:text=R%C3%A9diger%20les%20statuts%20avec%20les,la%20R%C3%A9publique%2C%2092001%20Nanterre%20Cedex": ["créer association", "rejoindre association", "vie associative", "statuts association", "domiciliation association"],
            "https://aca2.parisnanterre.fr/associations/accompagnement-des-associations-etudiantes/les-subventions-aux-associations": ["subvention association", "cvec", "aide association", "financement", "budget association", "dossier subvention"],
            "https://etudiants.parisnanterre.fr/residences-universitaires#:~:text=Les%20tarifs%20sont%20compris%20entre%20239.60%20%E2%82%AC%20et%20461.70%20%E2%82%AC%20charges%20comprises": ["chambre crous", "loyer", "prix", "coûte", "tarif logement", "logement crous prix", "taille logement crous", "résidence universitaire", "disponibilité logement", "CROUS logement"],
            "https://bu.parisnanterre.fr/travailler-en-groupe": ["bibliothèque", "BU", "étude", "groupe", "travailler", "salle", "réservation salle", "espace collaboratif", "travail collectif"],
            "https://bu.parisnanterre.fr/horaires-et-calendrier": ["bibliothèque", "BU", "horaires", "heures", "ouverture", "fermeture", "jours fériés", "vacances universitaires"],
            "https://candidatures-inscriptions.parisnanterre.fr/accueil/faq-redoubler-dans-une-formation": ["inscription", "redoubler", "redoublement", "FAQ", "scolarité", "formation", "réorientation", "conditions redoublement", "dossier étudiant"],
            "https://aca2.parisnanterre.fr/agenda": ["association", "agenda", "événement", "aca2", "activité", "manifestation étudiante", "rencontre", "planning"],
            "https://api.parisnanterre.fr/faq": ["service", "handicap", "faq", "sha", "aide", "questions fréquentes", "support étudiant", "infos pratiques"],
            "https://etudiants.parisnanterre.fr/precarite-les-dispositifs-daide-a-luniversite": ["aide", "aide étudiant", "précarité", "services aide", "urgence sociale", "allocations", "fonds d’aide"],
            "https://api.parisnanterre.fr/accueil-suio": ["service", "aide", "orientation", "insertion professionnelle", "conseil en carrière"],
            "https://www.crous-versailles.fr/": ["services étudiants", "aides financières", "solidarité étudiante", "CROUS", "informations pratiques", "accompagnement CROUS"],
            "https://www.crous-versailles.fr/contacts/": ["contacts", "aide étudiante", "CROUS", "logement", "téléphone CROUS", "bureau accueil"],
            "https://bu.parisnanterre.fr/sinscrire": ["bibliothèque", "bu", "inscription", "carte BU", "accès bibliothèque", "adhésion"],
            "https://bu.parisnanterre.fr/accueil-handicap-1": ["bibliothèque", "bu", "handicap", "accueil handicap", "accessibilité", "matériel adapté"],
            "https://www.crous-versailles.fr/contacts/bourses-et-aides-financieres/": ["bourses", "aides financières", "CROUS", "précarité étudiante", "dossier social étudiant", "calendrier versements"],
            "https://www.crous-versailles.fr/contacts/social-et-accompagnement/": ["aide sociale", "accompagnement", "CROUS", "solidarité étudiante", "psychologue", "service social"],
            "https://www.crous-versailles.fr/contacts/logement-et-vie-en-residence/": ["logement étudiant", "vie en résidence", "CROUS", "aide au logement", "chambre étudiante", "règles résidence"],
            "https://www.crous-versailles.fr/contacts/compte-izly/": ["compte Izly", "CROUS", "services étudiants", "paiement universitaire", "recharger Izly", "restauration universitaire"],
            "https://www.lescrous.fr/2024/09/comment-beneficier-du-repas-crous-a-1e/#:~:text=Ainsi%20tous%20les%20%C3%A9tudiants%20peuvent,ou%20en%20situation%20de%20pr%C3%A9carit%C3%A9": ["restaurant universitaire Crous", "ru", "tarif", "prix", "repas", "repas 1 euro", "ticket RU", "alimentation étudiante"],
            "https://www.crous-versailles.fr/contacts/contribution-vie-etudiante-et-de-campus-cvec/": ["CVEC", "vie étudiante", "contribution universitaire", "paiement CVEC", "obligatoire", "justificatif CVEC"],
            "https://www.iledefrance-mobilites.fr/titres-et-tarifs": ["transport", "tarifs", "transports en commun", "abonnement", "réduction étudiante", "carte Navigo"],
            "https://www.iledefrance-mobilites.fr/titres-et-tarifs/detail/forfait-imagine-r-scolaire": ["transport", "forfait", "offre étudiante", "prix", "pass navigo", "imagineR", "mobilité", "réduction scolaire"],
            "https://www.iledefrance-mobilites.fr/titres-et-tarifs/detail/forfait-imagine-r-etudiant": ["transport", "forfait", "offre étudiante", "prix", "pass navigo", "imagineR", "mobilité étudiante", "tarif réduit"],
            "https://www.iledefrance-mobilites.fr/imagine-r#slice": ["transport", "pass navigo", "imagineR", "carte transport", "IDFM", "abonnement annuel"],
            "https://www.iledefrance-mobilites.fr/aide-et-contacts/generalites-supports-validations/comment-obtenir-un-forfait-imagine-r-et-ou-une-carte-de-transport-scolaire": ["transport", "forfait", "offre étudiante", "prix", "pass navigo", "imagineR", "obtenir carte", "démarches navigo"],
            "https://www.1jeune1solution.gouv.fr/logements/aides-logement": ["logement", "APL", "CAF", "jeunes", "étudiants"],
            "https://bienvenue.parisnanterre.fr/vie-du-campus/restauration-et-autres-lieux-de-convivialite": ["restaurant", "manger", "restauration", "cafet", "cafétariat", "pause repas", "lieux sociaux"],
            "https://licence.math.u-paris.fr/informations/modalites-de-controle-des-connaissances/#:~:text=Validation%20du%20dipl%C3%B4me&text=Une%20ann%C3%A9e%20est%20valid%C3%A9e%20si,les%20six%20semestres%20sont%20valid%C3%A9s": ["licence", "valider", "crédits", "validation année", "valider semestre", "réussir l'année", "MCC", "contrôle continu"],
            "https://www.1jeune1solution.gouv.fr/logements/conseils": ["logement", "conseils logement", "trouver logement", "astuces logement étudiant", "recherche appartement"],
            "https://suaps.parisnanterre.fr/la-piscine": ["sport", "suaps", "activités nautiques"],
            "https://suaps.parisnanterre.fr/la-salle-cardio": ["sport", "suaps", "éducation corporelle et remise en forme","fitness"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites": ["sport", "suaps"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/les-sports-collectifs": ["sport", "suaps", "sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/basket-ball": ["sport", "suaps", "basket-ball","sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/futsal": ["sport", "suaps", "futsal","sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/handball": ["sport", "suaps", "handball","sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/rugby": ["sport", "suaps", "rugby", "sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/tchoukball-kabadji": ["sport", "suaps", "tchoukball","sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/volley-ball": ["sport", "suaps", "volley-ball",
                                                                                   "sport collectif"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/les-sports-individuels": ["sport", "suaps",
                                                                                              "sport individuel"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/athletisme": ["sport", "suaps", "athlétisme",
                                                                                  "sport individuel"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/escalade": ["sport", "suaps", "escalade",
                                                                                "sport individuel"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/tir-a-larc": ["sport", "suaps", "tir à l'arc",
                                                                                  "sport individuel"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/les-sports-de-raquettes": ["sport", "suaps",
                                                                                               "sport de raquettes"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/badminton": ["sport", "suaps", "badminton",
                                                                                 "sport de raquettes"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/tennis": ["sport", "suaps", "tennis",
                                                                              "sport de raquettes"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/tennis-de-table": ["sport", "suaps", "tennis de table",
                                                                                       "sport de raquettes"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/les-sports-de-combat": ["sport", "suaps",
                                                                                            "sport de combat"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/jiu-jitsu": ["sport", "suaps", "jiu-jitsu",
                                                                                 "sport de combat"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/boxe": ["sport", "suaps", "boxe", "sport de combat"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/judo": ["sport", "suaps", "judo", "sport de combat"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/mma-grappling": ["sport", "suaps", "mma",
                                                                                     "sport de combat"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/self-defense": ["sport", "suaps", "self-defense",
                                                                                    "sport de combat"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/education-corporelle-et-remise-en-forme": ["sport",
                                                                                                               "suaps",
                                                                                                               "éducation corporelle et remise en forme"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/education-posturale": ["sport", "suaps",
                                                                                           "éducation posturale",
                                                                                           "éducation corporelle et remise en forme"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/fitness": ["sport", "suaps", "fitness",
                                                                               "éducation corporelle et remise en forme"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/musculation": ["sport", "suaps", "musculation",
                                                                                   "éducation corporelle et remise en forme"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/arts-du-mouvement": ["sport", "suaps",
                                                                                         "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/arts-du-cirque": ["sport", "suaps", "arts du cirque",
                                                                                      "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/atelier-choregraphie": ["sport", "suaps",
                                                                                            "atelier chorégraphie",
                                                                                            "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/bachata": ["sport", "suaps", "bachata",
                                                                               "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/danse-africaine": ["sport", "suaps", "danse africaine",
                                                                                       "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/danse-contemporaine": ["sport", "suaps",
                                                                                           "danse contemporaine",
                                                                                           "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/zumba": ["sport", "suaps", "zumba",
                                                                             "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/tango-argentin": ["sport", "suaps", "tango argentin",
                                                                                      "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/salsa": ["sport", "suaps", "salsa",
                                                                             "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/rocknroll": ["sport", "suaps", "rock'n'roll",
                                                                                 "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/piloxing": ["sport", "suaps", "piloxing",
                                                                                "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/kizomba": ["sport", "suaps", "kizomba",
                                                                               "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/hip-hop": ["sport", "suaps", "hip-hop",
                                                                               "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/danse-orientale": ["sport", "suaps", "danse orientale",
                                                                                       "arts du mouvement"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/activites-nautiques": ["sport", "suaps",
                                                                                           "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/aquabike-aquagym-circuit-training": ["sport", "suaps",
                                                                                                         "aquabike",
                                                                                                         "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/plongee": ["sport", "suaps", "plongée",
                                                                               "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/natation-perfectionnement": ["sport", "suaps",
                                                                                                 "natation",
                                                                                                 "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/natation-intermediaire": ["sport", "suaps", "natation",
                                                                                              "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/natation-competition": ["sport", "suaps", "natation",
                                                                                            "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/natation-apprentissage": ["sport", "suaps", "natation",
                                                                                              "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/bnssa": ["sport", "suaps", "BNSSA",
                                                                             "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/baignade-libre": ["sport", "suaps", "baignade libre",
                                                                                      "activités nautiques"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/activite-detente": ["sport", "suaps",
                                                                                        "activité détente"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/yoga": ["sport", "suaps", "yoga", "activité détente"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/taichi-qi-gong": ["sport", "suaps", "taichi",
                                                                                      "activité détente"],
            "https://suaps.parisnanterre.fr/les-sports-et-activites/relaxation": ["sport", "suaps", "relaxation",
                                                                                  "activité détente"],
            "https://ufr-lce.parisnanterre.fr/associations": ["association", "annuaire"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/dix-de-choeur": ["association",
                                                                                                              "musique"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/melodix": ["association",
                                                                                                        "musique"],
            "http://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/la-volt": ["association",
                                                                                                       "musique"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/revolte-toi-nanterre": [
                "association", "éloquence et débat"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/les-unis-verts": [
                "association", "écologie"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/mun-society-paris-nanterre": [
                "association", "éloquence et débat"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/acfa": ["association",
                                                                                                     "représentation étudiante"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/amnesty-international-groupe-jeunes-3047": [
                "association", "caritatif"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/faun": ["association",
                                                                                                     "représentation étudiante"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/association-psychologie-du-developpement": [
                "association", "médias, lecture et écriture"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/les-indifferents": [
                "association", "théâtre"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/les-impunis-ligue-dimprovisation": [
                "association", "théâtre"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/eloquentia-nanterre": [
                "association", "éloquence et débat"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/lysias": ["association",
                                                                                                       "éloquence et débat"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/lcc-production": [
                "association", "audiovisuel/cinéma"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/nuits-noires": ["association",
                                                                                                             "audiovisuel/cinéma"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/atelier-decriture": [
                "association", "médias, lecture et écriture"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/lili-blooms-book-club": [
                "association", "médias, lecture et écriture"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/pile-a-lire": ["association",
                                                                                                            "médias, lecture et écriture"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/rcva": ["association",
                                                                                                     "culture scientifique"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/altiski": ["association",
                                                                                                        "sport"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/cheerleading-paris-nanterre-1": [
                "association", "sport"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/laocho": ["association",
                                                                                                       "sport"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/la-nav-nanterre-association-de-voile": [
                "association", "sport"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/aumonerie-catholique-des-etudiant-es": [
                "association", "solidarité et entraide"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/asega": ["association",
                                                                                                      "solidarité et entraide"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/cercle-marxiste-de-nanterre": [
                "association", "citoyenneté"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/etudiants-musulmans-de-france-nanterre": [
                "association", "solidarité et entraide"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/ucph": ["association",
                                                                                                     "solidarité et entraide"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/union-etudiants-juifs-france-nanterre": [
                "association", "solidarité et entraide"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/lathena": ["association",
                                                                                                        "caritatif"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/antenne-jeunes-unicef-nanterre": [
                "association", "caritatif"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/amicale-des-etudiant-es-senegalais-es": [
                "association", "cultures du monde"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/compagnie-ptdr": [
                "association", "théâtre"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/paris-nanterre-maroc-1": [
                "association", "cultures du monde"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/le-poing-leve": ["association",
                                                                                                              "citoyenneté"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/union-etudiante-nanterre": [
                "association", "représentation étudiante"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/unef-nanterre": ["association",
                                                                                                              "représentation étudiante"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/ugen-fse": ["association",
                                                                                                         "représentation étudiante"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/promet": ["association",
                                                                                                       "association de filiere, ssa, sciences sociales et administrations"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/hypothemuse": ["association",
                                                                                                            "association de filiere, ssa, sciences sociales et administrations"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/gang": ["association",
                                                                                                     "association de filiere, ssa, sciences sociales et administrations"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/enape": ["association",
                                                                                                      "association de filiere, ssa, sciences sociales et administrations"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/bde-staps-rhinos": [
                "association", "sciences et techniques des activites physiques et sportives (staps)"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/psychx": ["association",
                                                                                                       "sciences psychologiques et sciences de l'éducation (spse)"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/comite-dactions-et-reseau-des-etudiants-en-sante-et-societe": [
                "association", "sciences psychologiques et sciences de l'éducation (spse)"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/les-alhumes": ["association",
                                                                                                            "sciences psychologiques et sciences de l'éducation (spse)"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/cine-rebelle": ["association",
                                                                                                             "philosophie, information-communication, langage, littérature, arts du spectacle (phillia)"],
            "https://aca2.parisnanterre.fr/associations/annuaire-des-associations-etudiantes/association-west-street": [
                "association", "sciences economiques, gestion, mathematiques, infomatique (segmi)"],
            "https://etudiants.parisnanterre.fr/precarite-les-dispositifs-daide-a-luniversite/ouverture-des-inscriptions-a-lepicerie-solidaire-agorae": [
                "precarité", "epicerie", "solidarite"]
        }
        self.jokes = [
            "Un étudiant, c’est un peu comme une mise à jour. Toujours prévu pour demain.",
            "Pourquoi les partiels s’appellent 'partiels' ? Parce que je les réussis… partiellement.",
            "Comment les étudiants en maths font la cuisine ? Ils pèsent leur sel avec des intégrales.",
            "Pourquoi les étudiants en info ne se perdent jamais ? Parce qu’ils suivent toujours la bonne arborescence.",
            "Un étudiant en info qui drague : 'Je veux compiler nos cœurs en un seul exécutable.'",
            "Un étudiant en informatique va chez le psy. Il dit : 'Je crois que je suis dans une boucle infinie.' Le psy répond : 'Encore ?'",
            "Humour de prof : 'Première heure de cours. Étape 1 : S'enfermer dans sa salle '\n' Étape 2 : Laisser les élèves frapper à la porte '\n' Étape 3 : Attendre qu'ils disent : ‘Il n’est pas là !!! '\n' Étape 4 : Ouvrir.",
            "Pourquoi est-ce qu'il faut mettre tous les crocos en prison ? Parce que les crocos dealent.",
            "Comment fait-on pour allumer un barbecue breton ? On utilise des breizh.",
            "Pourquoi est-ce que les vêtements sont toujours fatigués quand ils sortent de la machine ? Parce qu’ils sont lessivés.",
            "Pourquoi est-ce que les livres ont-ils toujours chaud ? Parce qu’ils ont une couverture.",
            "Où est-ce que les super-héros vont-ils faire leurs courses ? Au supermarché.",
            "Que se passe-t-il quand 2 poissons s'énervent ? Le thon monte.",
            "Que dit une imprimante dans l'eau ? J’ai papier.",
            "Pourquoi les girafes n'existent pas ? Parce que c’est un coup monté.",
            "Pourquoi est-ce que Hulk a un beau jardin ? Parce qu’il a la main verte.",
            "Que fait un employé de chez Sephora à sa pause clope ? Il parfumer.",
            "Comment appelle-t-on un combat entre un petit pois et une carotte ? Un bon duel."
        ]

        self.current_joke_index = -1
        self.waiting_for_another_joke = False
        self.create_widgets()
        self.title_label = None
        self.subtitle_label = None
        self.current_task = None
        self.start_new_conversation()

    def load_conversation_history(self):
        """Charge l'historique des conversations depuis un fichier JSON."""
        try:
            if os.path.exists("conversation_history.json"):
                with open("conversation_history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement de l'historique des conversations: {e}")
            return {}

    def save_question_response(self, question, response):
        try:
            questions_responses = self.load_conversation_history()

            # Ajouter la nouvelle paire question/réponse
            questions_responses[question] = response

            # Sauvegarder le tout
            with open("questions_responses.json", "w", encoding="utf-8") as f:
                json.dump(questions_responses, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la question/réponse: {e}")

    def detect_informal_conversation(self, message):
        """Détecte si le message est une salutation ou conversation informelle"""

        # Convertir en minuscules pour faciliter la détection
        message_lower = message.lower().strip()

        # Détecter les salutations
        salutations = ["salut", "hello", "bonjour", "coucou", "hey", "yo", "bonsoir", "wesh",
                       "slt", "bjr", "cc", "kikou", "hi", "hola"]

        # Détecter les variantes de "ça va"
        ca_va_variants = ["ça va", "ca va", "comment vas-tu", "comment tu vas", "comment va",
                          "la forme", "tu vas bien", "vous allez bien", "comment allez-vous",
                          "comment ça va", "comment ca va", "ça dit quoi", "ca dit quoi"]

        # Détecter les expressions positives
        positive_mood = ["je vais bien", "ça va bien", "ca va bien", "je me sens bien",
                         "super", "génial", "content", "heureux", "trop bien", "bonne journée",
                         "je suis heureux", "je suis content", "je suis joyeux"]

        # Détecter les expressions négatives
        negative_mood = ["je vais mal", "ça va pas", "ca va pas", "je me sens mal",
                         "pas bien", "triste", "déprimé", "déprime", "mauvaise journée",
                         "je suis triste", "je suis pas bien", "je suis déprimé"]

        # Réponses pour les salutations
        salutation_responses = [
            "Bonjour ! En quoi puis-je vous aider aujourd'hui ?",
            "Salut ! Comment ça va aujourd'hui ?",
            "Hello ! Comment vous sentez-vous aujourd'hui ?",
            "Coucou ! Que puis-je faire pour vous aider ?",
            "Hey ! Tout se passe bien de votre côté ?"
        ]

        # Réponses positives
        positive_responses = [
            "C'est super de l'entendre ! En quoi puis-je vous aider aujourd'hui ?",
            "Je suis content pour vous ! Comment puis-je vous être utile ?",
            "Excellente nouvelle ! N'hésitez pas à me poser vos questions sur l'université.",
            "Ça fait plaisir ! Que puis-je faire pour vous aujourd'hui ?"
        ]

        # Réponses de réconfort
        comfort_responses = [
            "Je suis désolé de l'entendre. N'hésitez pas à me poser des questions sur l'université, je suis là pour vous aider du mieux que je peux.",
            "Courage, les choses vont s'améliorer. En attendant, je suis là pour répondre à vos questions sur l'université.",
            "Je comprends que ce n'est pas facile. N'hésitez pas à me demander des informations qui pourraient vous être utiles.",
            "Prenez soin de vous. Si vous avez besoin d'informations sur les services d'aide psychologique de l'université, je peux vous renseigner."
        ]

        # Réponses aux "ça va"
        ca_va_responses = [
            "Je vais bien, merci ! Je suis là pour répondre à vos questions sur l'université. Comment puis-je vous aider ?",
            "Tout va bien, merci de demander ! En quoi puis-je vous être utile aujourd'hui ?",
            "Tout roule pour moi, je suis opérationnel et prêt à vous aider. Quelle information recherchez-vous ?",
            "Oui, Je suis toujours prêt à aider ! Que souhaitez-vous savoir sur l'université ?"
        ]

        # Vérifier si c'est une salutation simple
        is_just_greeting = any(greeting in message_lower for greeting in salutations) and len(
            message_lower.split()) <= 3

        # Vérifier si c'est une variante de "ça va"
        is_ca_va = any(variant in message_lower for variant in ca_va_variants)

        # Vérifier l'humeur positive
        is_positive = any(pos in message_lower for pos in positive_mood)

        # Vérifier l'humeur négative
        is_negative = any(neg in message_lower for neg in negative_mood)

        # Retourner le type de message et une réponse appropriée
        if is_just_greeting:
            return True, random.choice(salutation_responses)
        elif is_ca_va:
            return True, random.choice(ca_va_responses)
        elif is_positive:
            return True, random.choice(positive_responses)
        elif is_negative:
            return True, random.choice(comfort_responses)

        # Si ce n'est pas une conversation informelle
        return False, None
    def save_conversation_history(self):
        """Sauvegarde l'historique des conversations dans un fichier JSON."""
        try:
            with open("conversation_history.json", "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'historique des conversations: {e}")

    def format_text_for_display(self, text):
        """
        Convertit le texte brut avec des balises Markdown en texte formaté pour l'affichage.
        Gère les titres (##), le texte en gras (**), les liens et ajoute des espaces appropriés.
        """
        # Créer des tags s'ils n'existent pas déjà
        if not hasattr(self, "format_tags_created"):
            self.chat_display.tag_configure("bold", font=("Arial", 14, "bold"))
            self.chat_display.tag_configure("heading", font=("Arial", 16, "bold"), foreground="#1a73e8")
            self.chat_display.tag_configure("subheading", font=("Arial", 15, "bold"), foreground="#1a73e8")
            self.chat_display.tag_configure("link", foreground="#1a73e8", underline=1)
            self.format_tags_created = True

            # Stocker les URLs associées aux tags de lien
            if not hasattr(self, "link_urls"):
                self.link_urls = {}

        self.enable_chat_display(tk.NORMAL)

        # Indice courant pour l'insertion de texte
        current_index = self.chat_display.index(tk.END)

        # Diviser le texte en paragraphes pour un meilleur espacement
        paragraphs = text.split('\n\n')

        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue

            # Traiter les titres (##)
            if paragraph.strip().startswith('## '):
                heading_text = paragraph.strip()[3:]
                self.chat_display.insert(tk.END, heading_text + "\n", "heading")

            # Traiter les sous-titres (###)
            elif paragraph.strip().startswith('### '):
                heading_text = paragraph.strip()[4:]
                self.chat_display.insert(tk.END, heading_text + "\n", "subheading")

            else:
                # Position de départ pour ce paragraphe
                start_pos = self.chat_display.index(tk.END)

                # Insérer le texte du paragraphe
                self.chat_display.insert(tk.END, paragraph)

                # Traiter le gras (**texte**)
                start_search = start_pos
                while True:
                    bold_start = self.chat_display.search('**', start_search, tk.END)
                    if not bold_start:
                        break

                    bold_end = self.chat_display.search('**', f"{bold_start}+2c", tk.END)
                    if not bold_end:
                        break

                    # Appliquer le tag bold
                    self.chat_display.tag_add("bold", f"{bold_start}+2c", bold_end)

                    # Supprimer les marqueurs **
                    self.chat_display.delete(bold_end, f"{bold_end}+2c")
                    self.chat_display.delete(bold_start, f"{bold_start}+2c")

                    # Mettre à jour la position de départ pour la prochaine recherche
                    start_search = bold_end

                # Traiter les liens - format simple [texte](url)
                start_search = start_pos
                link_counter = 0  # Compteur pour créer des tags de lien uniques

                while True:
                    link_start = self.chat_display.search('[', start_search, tk.END)
                    if not link_start:
                        break

                    text_end = self.chat_display.search(']', link_start, tk.END)
                    if not text_end:
                        break

                    url_start = self.chat_display.search('(', text_end, tk.END)
                    if not url_start or self.chat_display.get(text_end, f"{text_end}+2c") != "](":
                        start_search = f"{text_end}+1c"
                        continue

                    url_end = self.chat_display.search(')', url_start, tk.END)
                    if not url_end:
                        break

                    # Extraire le texte et l'URL
                    link_text = self.chat_display.get(f"{link_start}+1c", text_end)
                    url = self.chat_display.get(f"{url_start}+1c", url_end)

                    # Supprimer l'ancienne syntaxe
                    self.chat_display.delete(link_start, f"{url_end}+1c")

                    # Insérer le texte du lien
                    link_pos = link_start
                    self.chat_display.insert(link_pos, link_text)

                    # Créer un tag de lien unique pour ce lien spécifique
                    link_tag = f"link_{self.current_conversation_id}_{link_counter}"
                    link_counter += 1

                    # Appliquer le style du tag "link" à notre nouveau tag unique
                    self.chat_display.tag_configure(link_tag, foreground="#1a73e8", underline=1)

                    # Appliquer le tag au texte
                    self.chat_display.tag_add(link_tag, link_pos, f"{link_pos}+{len(link_text)}c")

                    # Ajouter un gestionnaire de clic pour ouvrir le lien avec une fonction lambda statique
                    self.chat_display.tag_bind(link_tag, "<Button-1>",
                                               lambda e, u=url: self.open_url(u))

                    # Changer le curseur lorsqu'on survole le lien
                    self.chat_display.tag_bind(link_tag, "<Enter>",
                                               lambda e: self.chat_display.config(cursor="hand2"))
                    self.chat_display.tag_bind(link_tag, "<Leave>",
                                               lambda e: self.chat_display.config(cursor=""))

                    # Mettre à jour la position de départ
                    start_search = f"{link_pos}+{len(link_text)}c"

                # Ajouter un saut de ligne après chaque paragraphe
                self.chat_display.insert(tk.END, "\n\n")

        # Supprimer le dernier saut de ligne supplémentaire
        if paragraphs:
            self.chat_display.delete(f"{tk.END}-2c", tk.END)

        self.enable_chat_display(tk.DISABLED)

    def open_url(self, url):
        """Ouvre l'URL dans le navigateur par défaut."""
        import webbrowser
        webbrowser.open(url)

    def improve_ui(self):
        """
        Améliore l'apparence générale de l'interface utilisateur.
        À appeler après l'initialisation des widgets.
        """
        # Améliorer l'apparence de la zone de chat
        self.chat_display.configure(
            padx=20,  # Augmenter les marges latérales
            pady=10,  # Augmenter les marges verticales
            spacing1=5,  # Espace avant un paragraphe (réduit de 10 à 5)
            spacing2=2,  # Espace entre les lignes
            spacing3=5   # Espace après un paragraphe (réduit de 10 à 5)
        )

        # Configuration plus attrayante pour les messages
        self.chat_display.tag_configure("user", foreground="#0b57d0",
                                        font=("Arial", 14, "bold"),
                                        spacing1=10, spacing3=5)  # spacing3 réduit de 8 à 5

        self.chat_display.tag_configure("assistant", foreground="#1a73e8",
                                        font=("Arial", 14),
                                        spacing1=10, spacing3=3)  # spacing3 réduit de 5 à 3

        # Améliorer le cadre d'historique
        self.history_frame.configure(padx=5, pady=10)

        # Style pour les boutons d'historique de conversation
        for child in self.history_scrollable_frame.winfo_children():
            if isinstance(child, tk.Frame):
                for button in child.winfo_children():
                    if isinstance(button, tk.Button):
                        if "Supprimer" not in button.cget("text"):
                            button.configure(
                                relief=tk.FLAT,
                                borderwidth=0,
                                padx=15,
                                pady=12,
                                font=("Arial", 10),
                                anchor="w",
                                cursor="hand2"
                            )

        # Améliorer l'apparence des suggestions
        if hasattr(self, 'suggestions_frame'):
            for child in self.suggestions_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(
                        relief=tk.FLAT,
                        borderwidth=0,
                        highlightbackground="#dadce0",
                        highlightthickness=1,
                        padx=8,
                        pady=8
                    )

                    # Polir les labels dans les suggestions
                    for label in child.winfo_children():
                        if isinstance(label, tk.Label):
                            label.configure(
                                padx=10,
                                pady=6
                            )

    def create_widgets(self):
        # Diviser l'écran en deux parties principales : historique à gauche, chat à droite
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="white",
                                         sashwidth=5, showhandle=False, sashrelief=tk.SUNKEN)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Panneau d'historique à gauche
        self.history_frame = tk.Frame(self.main_paned, bg="#f8f9fa")
        self.main_paned.add(self.history_frame, minsize=200)

        # Titre pour le panneau d'historique
        history_title = tk.Label(self.history_frame, text="Historique des conversations",
                                 font=("Arial", 12, "bold"), bg="#f8f9fa", fg="#1a73e8", pady=10)
        history_title.pack(fill=tk.X)

        # Bouton pour nouvelle conversation
        new_conv_button = tk.Button(self.history_frame, text="Nouvelle conversation",
                                    command=self.start_new_conversation, bg="#1a73e8", fg="white",
                                    font=("Arial", 10), bd=0, pady=5)
        new_conv_button.pack(fill=tk.X, padx=10, pady=5)

        # Zone d'historique des conversations (avec scrollbar)
        self.history_container = tk.Frame(self.history_frame, bg="#f8f9fa")
        self.history_container.pack(fill=tk.BOTH, expand=True, pady=10)

        self.history_canvas = tk.Canvas(self.history_container, bg="#f8f9fa",
                                        highlightthickness=0, borderwidth=0)
        self.history_scrollbar = ttk.Scrollbar(self.history_container, orient="vertical",
                                               command=self.history_canvas.yview)
        self.history_scrollable_frame = tk.Frame(self.history_canvas, bg="#f8f9fa")

        self.history_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            )
        )

        self.history_canvas.create_window((0, 0), window=self.history_scrollable_frame, anchor="nw")
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)

        self.history_canvas.pack(side="left", fill="both", expand=True)
        self.history_scrollbar.pack(side="right", fill="y")

        # Panneau de chat à droite
        self.chat_pane = tk.Frame(self.main_paned, bg="white")
        self.main_paned.add(self.chat_pane, minsize=600)

        # Configuration du panneau de chat
        self.chat_pane.grid_rowconfigure(0, weight=1)
        self.chat_pane.grid_columnconfigure(0, weight=1)

        # Zone d'affichage du chat
        self.chat_frame = tk.Frame(self.chat_pane, bg="white")
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, bg="white", font=("Arial", 14),
                                                      borderwidth=0, highlightthickness=0, padx=100)
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_display.tag_configure("user", foreground="#0b57d0",
                                        font=("Arial", 14, "bold"))  # Bleu pour l'utilisateur
        self.chat_display.tag_configure("assistant", foreground="#1a73e8",
                                        font=("Arial", 14))  # Bleu légèrement plus clair pour l'assistant
        self.chat_display.tag_configure("system", foreground="#5f6368",
                                        font=("Arial", 11))  # Gris pour les messages système
        self.chat_display.tag_configure("error", foreground="#d93025", font=("Arial", 11))  # Rouge pour les erreurs

        # Nouveau tag pour le titre centré
        self.chat_display.tag_configure("welcome_centered", foreground="#1a73e8",
                                        font=("Arial", 18, "bold"), justify='center')
        self.chat_display.tag_add("center", "1.0", "end")
        self.chat_display.config(state=tk.DISABLED)

        # Séparateur
        separator = ttk.Separator(self.chat_pane, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # Zone de saisie en bas avec un style ChatGPT
        self.input_frame = tk.Frame(self.chat_pane, bg="white", height=80)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        # Centrer la zone de saisie et ajouter une bordure arrondie
        self.inner_input_frame = tk.Frame(self.input_frame, bg="white")
        self.inner_input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Créer un cadre pour la zone de texte avec une bordure arrondie
        self.entry_container = tk.Frame(self.inner_input_frame, bg="#f0f0f5", bd=1, relief=tk.SOLID,
                                        highlightbackground="#dadce0", highlightthickness=1)
        self.entry_container.pack(fill=tk.X, padx=0, pady=0)

        # Zone de saisie
        self.question_entry = tk.Entry(self.entry_container, font=("Arial", 12), bd=0, highlightthickness=0,
                                       bg="#f0f0f5")
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        self.question_entry.bind("<Return>", self.ask_question)
        self.question_entry.focus_set()  # Mettre le focus sur la zone de saisie au démarrage

        self.question_entry = tk.Entry(self.entry_container, font=("Arial", 12), bd=0, highlightthickness=0,
                                       bg="#f0f0f5")
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        self.question_entry.bind("<Return>", self.ask_question)
        self.question_entry.focus_set()

        # Ajouter les suggestions initiales
        self.create_suggestion_boxes()
        # Bouton d'envoi arrondi
        send_button = tk.Button(self.entry_container, text="Envoyer",
                                command=lambda: self.ask_question(),  # Utiliser lambda ici
                                bg="#1a73e8", fg="white", font=("Arial", 11), bd=0, padx=15, pady=5,
                                activebackground="#0b57d0", activeforeground="white")
        send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # S'assurer que la touche Entrée est bien liée à la fonction ask_question
        self.question_entry.bind("<Return>", lambda event: self.ask_question())

        # Indicateur de chargement (placé au-dessus de la zone de saisie)
        self.progress_bar = ttk.Progressbar(self.chat_pane, mode="indeterminate")

        # Barre de statut
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        status_bar = tk.Label(self.chat_pane, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              bg="#f8f9fa", fg="#5f6368")
        status_bar.grid(row=3, column=0, sticky="ew")
        self.root.after(100, lambda: self.main_paned.sash_place(0, 250, 0))  # 250px depuis la gauche

        # Remplir l'historique des conversations
        self.populate_history()

        # Améliorer l'apparence de l'interface
        self.improve_ui()

    def generate_contextual_suggestions(self, question_or_topic=""):
        """
        Génère 3 suggestions contextuelles basées sur le sujet de la conversation actuelle.
        """
        import random  # Ajoutez cette ligne pour s'assurer que random est disponible

        # Créer un graphe de relations entre les sujets
        topic_graph = {
            "crous": ["restauration", "logement", "bourse", "cvec", "aide etudiante"],
            "restauration": ["crous", "trouver un batiment", "logement"],
            "logement": ["restauration", "aller a l'université", "crous"],
            "aide etudiante": ["association", "service handicap", "service precarité", "reussir son année", "crous"],
            "reussir son année": ["service precarité", "service handicap", "blagues", "travailler a la bu",
                                  "aller a l'université"],
            "travailler a la bu": ["trouver un batiment", "suaps", "reussir son année"],
            "blagues": ["hey", "reussir son année"],
            "aller a l'université": ["logement", "trouver un batiment", "reussir son année"],
            "trouver un batiment": ["restauration", "travailler a la bu", "aller a l'université"],
            "suaps": ["travailler a la bu", "sport"],
            "sport": ["suaps"],
            "association": ["aide etudiante"],
            "service handicap": ["aide etudiante", "reussir son année"],
            "service precarité": ["aide etudiante", "reussir son année"],
            "bourse": ["crous", "aide etudiante"],
            "cvec": ["crous"]
        }

        topic_questions = {
            "crous": ["Numéro de téléphone du crous",
                      "Quelles sont les aides financières proposées par le Crous?",
                      "Comment avoir un logement étudiant Crous ?"],
            "restauration": ["Où manger à l'université ?"],
            "logement": ["Quels sont les types de logements disponibles au Crous?",
                         "Quel est le prix du loyer d'un logement crous?"],
            "aide etudiante": ["Quelles sont les aides financières pour les étudiants?",
                               "Comment contacter le service social de l'université?"],
            "reussir son année": ["Comment se passe le redoublement ?",
                                  "Comment réussir l'année ?"],
            "travailler a la bu": ["Quelles sont les horaires de la bibliothèque?",
                                   "est -il possible de travailler en groupe à la bibliothèque?"],
            "blagues": ["Raconte-moi une blague sur les étudiants",
                        "As-tu une blague drôle à me proposer?",
                        "Fais-moi rire avec une blague"],
            "aller a l'université": ["Comment aller à l'université en transports en commun?",
                                     "Comment aller à l'université en voiture ?",
                                     "Quelle est l'adresse de l'université ?"],
            "trouver un batiment": ["Comment trouver le bâtiment Grappin sur le campus?",
                                    "Où se trouve l'UFR SEGMI ?",
                                    "Ou est le batiment Z"],
            "suaps": ["Quelles activités sportives sont proposées par le SUAPS?",
                      "A quelle heure est le judo à l'université ?",
                      "Y a til du tennis à l'université ?"],
            "association": ["Quelles sont les associations étudiantes à Paris Nanterre?",
                            "Comment créer son association ?",
                            "Quel est l'agenda de la semaine ?"],
            "service handicap": ["Quels aménagements sont disponibles pour les étudiants en situation de handicap?",
                                 "Comment contacter le service handicap de l'université?"],
            "service precarité": ["Quelles aides existent pour les étudiants en difficulté financière?",
                                  "Où trouver une aide alimentaire sur le campus?",
                                  "Comment accéder à l'épicerie solidaire de l'université?"],
            "bourse": ["Comment faire une demande de bourse ?",
                       "Numéro de téléphone du crous pour aides financières et bourse?",
                       "Quelles sont les conditions pour obtenir une bourse?"],
            "cvec": ["Comment payer la CVEC?",
                     "À quoi sert la CVEC?"]
        }

        question_lower = question_or_topic.lower()
        current_topic = None

        # Chercher des mots-clés dans la question pour déterminer le sujet
        for topic in topic_graph.keys():
            if topic in question_lower or any(keyword in question_lower for keyword in topic_graph[topic]):
                current_topic = topic
                break

        # Si aucun sujet n'est détecté, choisir un sujet aléatoire
        if not current_topic:
            import random
            current_topic = random.choice(list(topic_graph.keys()))

        # Obtenir les sujets connexes
        related_topics = topic_graph.get(current_topic, [])
        if len(related_topics) < 2:  # S'assurer d'avoir au moins 3 sujets au total
            # Ajouter quelques sujets aléatoires
            all_topics = list(topic_graph.keys())
            random.shuffle(all_topics)
            for topic in all_topics:
                if topic not in related_topics and topic != current_topic:
                    related_topics.append(topic)
                if len(related_topics) >= 2:
                    break

        # Sélectionner les 3 sujets pour les suggestions
        suggestion_topics = [current_topic] + related_topics[:2]
        random.shuffle(suggestion_topics)  # Mélanger pour plus de variété

        # Générer une question pour chaque sujet
        suggestions = []
        for topic in suggestion_topics:
            if topic in topic_questions:
                suggestions.append(random.choice(topic_questions[topic]))

        # S'assurer d'avoir exactement 3 suggestions
        while len(suggestions) < 3:
            random_topic = random.choice(list(topic_questions.keys()))
            random_question = random.choice(topic_questions[random_topic])
            if random_question not in suggestions:
                suggestions.append(random_question)

        return suggestions[:3]  # Retourner exactement 3 suggestions

    def create_suggestion_boxes(self):
        """
        Crée les boîtes de suggestions au-dessus de la barre de recherche.
        """
        # Supprimer les anciennes suggestions s'il y en a
        if hasattr(self, 'suggestions_frame'):
            self.suggestions_frame.destroy()

        # Créer un nouveau cadre pour les suggestions
        self.suggestions_frame = tk.Frame(self.inner_input_frame, bg="white")
        self.suggestions_frame.pack(fill=tk.X, padx=0, pady=(0, 5))

        # Configurer la grille pour les 3 suggestions côte à côte
        self.suggestions_frame.columnconfigure(0, weight=1)
        self.suggestions_frame.columnconfigure(1, weight=1)
        self.suggestions_frame.columnconfigure(2, weight=1)

        # Générer les suggestions contextuelles
        suggestions = self.generate_contextual_suggestions(self.get_current_context())

        # Fonction pour gérer le clic sur une suggestion
        def handle_suggestion_click(text):
            self.question_entry.delete(0, tk.END)
            self.question_entry.insert(0, text)
            self.ask_question()

        # Créer les trois boîtes de suggestions
        for i, suggestion in enumerate(suggestions):
            suggestion_box = tk.Frame(self.suggestions_frame, bg="#e8f0fe", bd=1, relief=tk.SOLID,
                                      highlightbackground="#dadce0", highlightthickness=1)
            suggestion_box.grid(row=0, column=i, padx=5, sticky="ew")

            # Texte de la suggestion (limité en longueur)
            max_length = 40
            display_text = suggestion if len(suggestion) <= max_length else suggestion[:max_length - 3] + "..."

            suggestion_label = tk.Label(suggestion_box, text=display_text,
                                        font=("Arial", 10), fg="#1a73e8", bg="#e8f0fe",
                                        padx=5, pady=5, wraplength=180)
            suggestion_label.pack(fill=tk.X)

            # Rendre cliquable
            suggestion_box.bind("<Button-1>", lambda e, text=suggestion: handle_suggestion_click(text))
            suggestion_label.bind("<Button-1>", lambda e, text=suggestion: handle_suggestion_click(text))

            # Changer le curseur au survol
            suggestion_box.bind("<Enter>", lambda e, w=suggestion_box: w.config(cursor="hand2"))
            suggestion_box.bind("<Leave>", lambda e, w=suggestion_box: w.config(cursor=""))
            suggestion_label.bind("<Enter>", lambda e, w=suggestion_label: w.config(cursor="hand2"))
            suggestion_label.bind("<Leave>", lambda e, w=suggestion_label: w.config(cursor=""))

    def get_current_context(self):
        """
        Récupère le contexte actuel de la conversation (dernières questions/réponses).
        """
        context = ""
        if self.current_conversation_id and self.current_conversation_id in self.conversation_history:
            messages = self.conversation_history[self.current_conversation_id]["messages"]
            # Récupérer les 3 derniers messages de l'utilisateur
            user_messages = [msg["content"] for msg in messages if msg["role"] == "user"][-3:]
            context = " ".join(user_messages)
        return context

    def update_suggestions(self, question=""):
        """
        Met à jour les suggestions basées sur la dernière question.
        """
        self.create_suggestion_boxes()
    def setup_ui(self):
        """Initialise l'interface avec le cadre de l'historique et du bouton."""
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Cadre parent commun qui régule la largeur
        self.container = tk.Frame(self.main_frame)
        self.container.pack(fill=tk.X, padx=10, pady=5)

        # Cadre pour l'historique
        self.history_frame = tk.Frame(self.container)
        self.history_frame.grid(row=0, column=0, sticky="ew")  # Remplir horizontalement

        # Cadre pour le bouton de "Nouvelle Conversation"
        self.new_conversation_button = tk.Button(
            self.container,
            text="Nouvelle conversation",
            bg="#4CAF50", fg="white", font=("Arial", 12),
            command=self.start_new_conversation
        )
        self.new_conversation_button.grid(row=1, column=0, sticky="ew", pady=5)  # Remplir horizontalement

        # Créer le cadre défilant pour les conversations
        self.history_scrollable_frame = tk.Frame(self.history_frame)
        self.history_scrollable_frame.pack(fill=tk.X, expand=True)

        # Mettre en place l'historique des conversations
        self.populate_history()


    def populate_history(self):
        """Remplit le panneau d'historique avec les conversations sauvegardées."""
        # Effacer d'abord tous les widgets existants
        for widget in self.history_scrollable_frame.winfo_children():
            widget.destroy()

        # Trier les conversations par date (la plus récente en premier)
        sorted_history = sorted(self.conversation_history.items(),
                                key=lambda x: x[1].get("timestamp", 0),
                                reverse=True)

        # Organiser les conversations en colonne
        for row, (conv_id, conv_data) in enumerate(sorted_history):
            # Créer un titre pour la conversation (première question ou horodatage)
            title = conv_data.get("title", "Conversation")
            timestamp = conv_data.get("timestamp", 0)
            date_str = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")

            # Créer un cadre pour chaque conversation
            conv_frame = tk.Frame(self.history_scrollable_frame, bg="#f8f9fa")
            conv_frame.pack(fill=tk.X, padx=5, pady=5)  # Utiliser fill=tk.X pour s'étirer en largeur

            # Créer le bouton pour la conversation
            conv_button = tk.Button(
                conv_frame,
                text=f"{title}\n{date_str}",
                bg="#f0f0f5",
                fg="#202124",
                font=("Arial", 9),
                bd=0,
                justify=tk.LEFT,
                anchor="w",
                padx=10,
                pady=8,
                wraplength=180,
                command=lambda cid=conv_id: self.load_conversation(cid)
            )

            # Étirement horizontal pour s'assurer que le bouton prend toute la largeur
            conv_button.pack(fill=tk.X, padx=5, pady=2)
            if conv_id == self.current_conversation_id:
                conv_button.configure(bg="#e8f0fe", fg="#1a73e8")

            # Ajouter le bouton de suppression à côté de chaque conversation
            delete_button = tk.Button(
                conv_frame,
                text="Supprimer",
                command=lambda cid=conv_id: self.delete_conversation(cid),
                bg="#d93025", fg="white", font=("Arial", 8), bd=0, padx=5, pady=2
            )
            delete_button.pack(side="right", padx=5, pady=2)

        self.history_scrollable_frame.update_idletasks()  # Met à jour l'interface après ajout de widgets

    def delete_conversation(self, conversation_id):
        """Supprime une conversation de l'historique et du fichier JSON."""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]  # Supprimer l'élément de l'historique
            self.save_conversation_history()  # Sauvegarder l'historique mis à jour
            self.populate_history()  # Mettre à jour l'affichage de l'historique

    def start_new_conversation(self):
        """Démarre une nouvelle conversation avec une interface améliorée."""
        # Générer un nouvel ID pour la conversation
        self.current_conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # Initialiser directement la nouvelle conversation dans l'historique
        self.conversation_history[self.current_conversation_id] = {
            "title": "Nouvelle conversation",
            "timestamp": datetime.now().timestamp(),
            "messages": []
        }

        # Effacer l'affichage du chat
        self.enable_chat_display(tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)

        # Créer un conteneur pour l'écran d'accueil
        welcome_container = tk.Frame(self.chat_display, bg="white")
        self.chat_display.window_create("1.0", window=welcome_container)

        # Sauvegarder l'historique
        self.save_conversation_history()

        # Mettre à jour l'affichage de l'historique
        self.populate_history()

        # Configurer welcome_container pour qu'il s'étende sur toute la largeur
        welcome_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)  # Marges augmentées

        # Ajouter de l'espace vertical pour centrer le contenu
        spacer_top = tk.Frame(welcome_container, height=100, bg="white")  # Hauteur augmentée
        spacer_top.pack(side=tk.TOP, fill=tk.X)

        # Créer un Frame pour le contenu (titre + sous-titre)
        content_frame = tk.Frame(welcome_container, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Logo ou icône (optionnel)
        try:
            # Créer un canvas pour dessiner une icône si pas d'image disponible
            icon_canvas = tk.Canvas(content_frame, width=190, height=80, bg="white",
                                    highlightthickness=0)
            icon_canvas.pack(pady=(0, 20))

            # Dessiner un cercle bleu avec un "U" à l'intérieur
            icon_canvas.create_oval(10, 10, 70, 70, fill="#1a73e8", outline="")
            icon_canvas.create_text(40, 40, text="U", font=("Arial", 32, "bold"), fill="white")

            # Cercle avec P au centre (collé au cercle de gauche)
            icon_canvas.create_oval(65, 10, 125, 70, fill="#1a73e8", outline="")
            icon_canvas.create_text(95, 40, text="P", font=("Arial", 32, "bold"), fill="white")

            # Cercle avec N à droite (collé au cercle du centre)
            icon_canvas.create_oval(120, 10, 180, 70, fill="#1a73e8", outline="")
            icon_canvas.create_text(150, 40, text="N", font=("Arial", 32, "bold"), fill="white")
        except Exception:
            pass  # En cas d'échec, continuer sans l'icône

        # Ajouter le titre avec une police plus grande et élégante
        self.title_label = tk.Label(
            content_frame,
            text="Assistant Universitaire Paris Nanterre",
            font=("Arial", 28, "bold"),
            fg="#1a73e8",
            bg="white"
        )
        self.title_label.pack(fill=tk.X, pady=(0, 25))  # Plus d'espace après le titre

        # Ajouter le sous-titre avec un aspect plus élégant
        detailed_welcome = """Je suis là pour vous aider avec toutes vos questions concernant l'université.
    Posez-moi n'importe quelle question sur les services, les cours, 
    les bâtiments ou la vie étudiante à Paris Nanterre."""

        self.subtitle_label = tk.Label(
            content_frame,
            text=detailed_welcome,
            font=("Arial", 15),
            fg="#5f6368",  # Gris plus clair et élégant
            bg="white",
            wraplength=550,  # Plus large pour éviter des retours à la ligne trop fréquents
            justify="center"
        )
        self.subtitle_label.pack(fill=tk.X, pady=(0, 30))  # Plus d'espace après le sous-titre

        # Créer un frame pour les suggestions avec plus d'espacement
        suggestions_frame = tk.Frame(content_frame, bg="white")
        suggestions_frame.pack(fill=tk.X, pady=(15, 30))

        # Configuration de la grille pour les suggestions
        suggestions_frame.columnconfigure(0, weight=1)
        suggestions_frame.columnconfigure(1, weight=1)
        suggestions_frame.columnconfigure(2, weight=1)

        # Fonction pour gérer le clic sur une suggestion
        def handle_suggestion_click(text):
            self.question_entry.delete(0, tk.END)
            self.question_entry.insert(0, text)
            self.ask_question()

        # Suggestion 1: Blagues (style amélioré)
        suggestion1_frame = tk.Frame(
            suggestions_frame,
            bg="#e8f0fe",
            bd=0,  # Pas de bordure
            highlightbackground="#dadce0",
            highlightthickness=1
        )
        suggestion1_frame.grid(row=0, column=0, padx=12, sticky="nsew")  # Plus d'espace

        suggestion1_title = tk.Label(
            suggestion1_frame,
            text="Blagues",
            font=("Arial", 14, "bold"),  # Police plus grande
            fg="#1a73e8",
            bg="#e8f0fe",
            pady=8  # Plus d'espace vertical
        )
        suggestion1_title.pack(fill=tk.X)

        suggestion1_subtitle = tk.Label(
            suggestion1_frame,
            text="Je peux vous proposer des blagues pour égayer votre journée",
            font=("Arial", 11),
            fg="#5f6368",  # Gris plus clair pour le sous-titre
            bg="#e8f0fe",
            pady=5,
            wraplength=190,  # Légèrement plus large
            justify="center"  # Centré pour plus d'esthétique
        )
        suggestion1_subtitle.pack(fill=tk.X, pady=(0, 12))

        # Suggestion 2: Crous (style amélioré)
        suggestion2_frame = tk.Frame(
            suggestions_frame,
            bg="#e8f0fe",
            bd=0,
            highlightbackground="#dadce0",
            highlightthickness=1
        )
        suggestion2_frame.grid(row=0, column=1, padx=12, sticky="nsew")

        suggestion2_title = tk.Label(
            suggestion2_frame,
            text="CROUS",
            font=("Arial", 14, "bold"),
            fg="#1a73e8",
            bg="#e8f0fe",
            pady=8
        )
        suggestion2_title.pack(fill=tk.X)

        suggestion2_subtitle = tk.Label(
            suggestion2_frame,
            text="Toutes vos questions concernant le CROUS et ses services d'aide aux étudiants",
            font=("Arial", 11),
            fg="#5f6368",
            bg="#e8f0fe",
            pady=5,
            wraplength=190,
            justify="center"
        )
        suggestion2_subtitle.pack(fill=tk.X, pady=(0, 12))

        # Suggestion 3: Services (style amélioré)
        suggestion3_frame = tk.Frame(
            suggestions_frame,
            bg="#e8f0fe",
            bd=0,
            highlightbackground="#dadce0",
            highlightthickness=1
        )
        suggestion3_frame.grid(row=0, column=2, padx=12, sticky="nsew")

        suggestion3_title = tk.Label(
            suggestion3_frame,
            text="Services Étudiants",
            font=("Arial", 14, "bold"),
            fg="#1a73e8",
            bg="#e8f0fe",
            pady=8
        )
        suggestion3_title.pack(fill=tk.X)

        suggestion3_subtitle = tk.Label(
            suggestion3_frame,
            text="Découvrez tous les services disponibles pour vous aider durant vos études",
            font=("Arial", 11),
            fg="#5f6368",
            bg="#e8f0fe",
            pady=5,
            wraplength=190,
            justify="center"
        )
        suggestion3_subtitle.pack(fill=tk.X, pady=(0, 12))

        # Ajouter des effets de survol plus élégants
        for frame, title, subtitle, question in [
            (suggestion1_frame, suggestion1_title, suggestion1_subtitle, "Propose-moi une blague"),
            (suggestion2_frame, suggestion2_title, suggestion2_subtitle,
             "Comment fonctionne le CROUS à Paris Nanterre?"),
            (suggestion3_frame, suggestion3_title, suggestion3_subtitle,
             "Quels sont les services d'aide pour les étudiants?")
        ]:
            # Lier les événements de clic
            frame.bind("<Button-1>", lambda e, q=question: handle_suggestion_click(q))
            title.bind("<Button-1>", lambda e, q=question: handle_suggestion_click(q))
            subtitle.bind("<Button-1>", lambda e, q=question: handle_suggestion_click(q))

            # Effets de survol améliorés
            def on_enter(e, f=frame, t=title):
                f.config(bg="#d2e3fc")  # Bleu plus foncé au survol
                t.config(bg="#d2e3fc")
                for widget in f.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(bg="#d2e3fc")
                f.config(cursor="hand2")

            def on_leave(e, f=frame, t=title):
                f.config(bg="#e8f0fe")  # Retour à la couleur normale
                t.config(bg="#e8f0fe")
                for widget in f.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(bg="#e8f0fe")
                f.config(cursor="")

            frame.bind("<Enter>", on_enter)
            frame.bind("<Leave>", on_leave)
            title.bind("<Enter>", on_enter)
            title.bind("<Leave>", on_leave)
            subtitle.bind("<Enter>", on_enter)
            subtitle.bind("<Leave>", on_leave)

        # Ajouter de l'espace en bas pour équilibrer le centrage vertical
        spacer_bottom = tk.Frame(welcome_container, height=100, bg="white")
        spacer_bottom.pack(side=tk.BOTTOM, fill=tk.X)

        # Assurer une hauteur suffisante pour le conteneur
        self.chat_display.insert(tk.END, "\n" * 20)
        self.chat_display.see("1.0")  # Remonter en haut
        self.enable_chat_display(tk.DISABLED)

    def get_random_joke(self):
        """Retourne une blague aléatoire de la liste."""
        import random
        # Assurez-vous de ne pas répéter la même blague immédiatement
        available_jokes = [i for i in range(len(self.jokes)) if i != self.current_joke_index]
        if not available_jokes:  # Si toutes les blagues ont été utilisées
            self.current_joke_index = -1
            available_jokes = list(range(len(self.jokes)))

        self.current_joke_index = random.choice(available_jokes)
        return self.jokes[self.current_joke_index]

    def load_conversation(self, conversation_id):
        """Charge une conversation existante."""
        if conversation_id not in self.conversation_history:
            return

        self.current_conversation_id = conversation_id
        self.populate_history()
        self.enable_chat_display(tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)

        # Récupérer les données de la conversation
        conv_data = self.conversation_history[conversation_id]
        title = conv_data.get("title", "Conversation")

        # Afficher les messages de la conversation avec un formatage correct
        for msg in conv_data.get("messages", []):
            if msg["role"] == "user":
                self.chat_display.insert(tk.END, "Vous: ", "user")
                self.chat_display.insert(tk.END, msg["content"] + "\n\n")  # Deux sauts de ligne
            elif msg["role"] == "assistant":
                self.chat_display.insert(tk.END, "Assistant: ", "assistant")
                self.chat_display.insert(tk.END, msg["content"] + "\n\n")  # Deux sauts de ligne
            elif msg["role"] == "system":
                # Pour les messages système, on peut les afficher différemment ou les omettre
                # Si vous voulez les omettre complètement, commentez ou supprimez ces deux lignes
                self.chat_display.insert(tk.END, msg["content"] + "\n\n", "system")
            elif msg["role"] == "error":
                self.chat_display.insert(tk.END, f"Erreur: {msg['content']}\n\n", "error")

        self.chat_display.see(tk.END)
        self.enable_chat_display(tk.DISABLED)

        # S'assurer que le titre et sous-titre de bienvenue sont supprimés s'ils existent
        if hasattr(self, 'title_label') and self.title_label and self.title_label.winfo_exists():
            # Récupérer le parent jusqu'au conteneur principal
            parent = self.title_label.master
            while parent and parent.master != self.chat_display:
                parent = parent.master

            # Supprimer le conteneur entier si trouvé
            if parent:
                parent.destroy()
            else:
                # Fallback si structure modifiée
                if self.title_label: self.title_label.destroy()
                if hasattr(self, 'subtitle_label') and self.subtitle_label: self.subtitle_label.destroy()

    def enable_chat_display(self, state):
        self.chat_display.config(state=state)

    def show_user_question(self, question):
        # Vérifier si c'est la première question dans une nouvelle conversation
        is_first_question = False
        if self.current_conversation_id and not self.conversation_history[self.current_conversation_id]["messages"]:
            is_first_question = True

        self.enable_chat_display(tk.NORMAL)

        # Si c'est la première question, effacer tout le contenu (y compris le titre)
        if is_first_question:
            self.chat_display.delete(1.0, tk.END)

            # Suppression explicite des widgets de bienvenue s'ils existent
            if hasattr(self, 'title_label') and self.title_label and self.title_label.winfo_exists():
                try:
                    # Trouver le conteneur parent des widgets de bienvenue
                    parent = self.title_label.master
                    while parent and parent != self.chat_display and parent.master != self.chat_display:
                        parent = parent.master

                    # Si on trouve le conteneur parent, le détruire
                    if parent and parent != self.chat_display:
                        parent.destroy()
                    else:
                        # Fallback: détruire les widgets individuellement
                        self.title_label.destroy()
                        if hasattr(self, 'subtitle_label') and self.subtitle_label:
                            self.subtitle_label.destroy()
                except Exception as e:
                    print(f"Erreur lors de la suppression des widgets de bienvenue: {e}")

        self.chat_display.insert(tk.END, "Vous: ", "user")
        self.chat_display.insert(tk.END, question + "\n\n")  # S'assurer qu'il y a bien deux sauts de ligne
        self.chat_display.see(tk.END)
        self.enable_chat_display(tk.DISABLED)

        # Ajouter le message à l'historique de la conversation actuelle
        if self.current_conversation_id:
            # Si c'est la première question, utiliser comme titre
            if is_first_question:
                self.conversation_history[self.current_conversation_id]["title"] = question[:30] + (
                    "..." if len(question) > 30 else "")

            self.conversation_history[self.current_conversation_id]["messages"].append({
                "role": "user",
                "content": question
            })
            # Sauvegarder également le message d'accueil dans l'historique si c'est la première question
            if is_first_question:
                detailed_welcome = """Je suis là pour vous aider avec toutes vos questions concernant l'université !?
                Comment puis-je vous aider aujourd'hui ?"""
                self.conversation_history[self.current_conversation_id]["messages"].insert(0, {
                    "role": "system",
                    "content": detailed_welcome
                })

            self.save_conversation_history()
            self.populate_history()

    def show_assistant_response(self, response):
        self.enable_chat_display(tk.NORMAL)
        self.chat_display.insert(tk.END, "Assistant: ", "assistant")
        self.chat_display.insert(tk.END, response + "\n\n")  # S'assurer qu'il y a deux sauts de ligne

        self.chat_display.see(tk.END)
        self.enable_chat_display(tk.DISABLED)

        # Ajouter le message à l'historique de la conversation actuelle
        if self.current_conversation_id:
            self.conversation_history[self.current_conversation_id]["messages"].append({
                "role": "assistant",
                "content": response
            })
            self.save_conversation_history()

        # Mettre à jour les suggestions basées sur la conversation actuelle
        self.update_suggestions()

    def show_error(self, error_message):
        self.enable_chat_display(tk.NORMAL)
        self.chat_display.insert(tk.END, f"Erreur: {error_message}\n\n", "error")
        self.chat_display.see(tk.END)
        self.enable_chat_display(tk.DISABLED)

        # Ajouter le message d'erreur à l'historique de la conversation actuelle
        if self.current_conversation_id:
            self.conversation_history[self.current_conversation_id]["messages"].append({
                "role": "error",
                "content": error_message
            })
            self.save_conversation_history()

    def ask_question(self, event=None):
        question = self.question_entry.get().strip()
        if not question:
            return

        # Effacer complètement l'écran d'accueil si c'est la première question
        self.enable_chat_display(tk.NORMAL)

        # Solution au problème: supprimer tout le contenu du chat_display
        # si c'est la première question d'une nouvelle conversation
        if self.current_conversation_id and len(
                self.conversation_history[self.current_conversation_id]["messages"]) == 0:
            self.chat_display.delete(1.0, tk.END)

        self.enable_chat_display(tk.DISABLED)

        # Si c'est la première question, enregistrer la conversation dans l'historique
        if hasattr(self, 'temp_conversation') and self.temp_conversation:
            # Ajouter la conversation à l'historique
            self.conversation_history[self.current_conversation_id] = self.temp_conversation
            # Réinitialiser la variable temporaire
            self.temp_conversation = None
            # Maintenant, on peut sauvegarder l'historique
            self.save_conversation_history()
            # Mettre à jour l'affichage de l'historique
            self.populate_history()

        # Afficher la question
        self.show_user_question(question)
        self.question_entry.delete(0, tk.END)

        # Indiquer que la recherche est en cours
        self.status_var.set("Recherche en cours...")
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.progress_bar.start(10)
        self.update_suggestions(question)

        # Lancer la recherche dans un thread séparé
        threading.Thread(target=self.process_question_thread, args=(question,), daemon=True).start()

    def process_question_thread(self, question):
        try:
            # Vérifier d'abord si c'est une conversation informelle
            is_informal, informal_response = self.detect_informal_conversation(question)
            if is_informal:
                # Si c'est une conversation informelle, retourner directement la réponse
                self.root.after(0, lambda: self.show_assistant_response(informal_response))
                return

            # Vérifier si c'est une demande de blague
            if ("blague" in question.lower() or
                    "raconte" in question.lower() and "blague" in question.lower() or
                    "propose" in question.lower() and "blague" in question.lower()):
                joke = self.get_random_joke()
                response = f"{joke}\n\nVoulez-vous une autre blague ?"
                self.waiting_for_another_joke = True
                self.root.after(0, lambda: self.show_assistant_response(response))
                return

            # Vérifier si l'utilisateur veut une autre blague
            elif self.waiting_for_another_joke and ("oui" in question.lower() or "yes" in question.lower() or
                                                    "autre" in question.lower() or "ok" in question.lower() or
                                                    "encore" in question.lower()):
                joke = self.get_random_joke()
                response = f"{joke}\n\nVoulez-vous une autre blague ?"
                self.root.after(0, lambda: self.show_assistant_response(response))
                return

            # L'utilisateur ne veut plus de blagues
            elif self.waiting_for_another_joke:
                self.waiting_for_another_joke = False
                self.root.after(0, lambda: self.show_assistant_response(
                    "D'accord ! N'hésitez pas à me demander si vous avez besoin d'autre chose."))
                return

            # Vérifier si c'est une question sur les associations
            elif any(mot in question.lower() for mot in ["association", "club", "asso", "activité",
                                                         "bénévolat", "engagement", "adhérer", "rejoindre",
                                                         "participer", "création", "créer une association"]):
                # Traiter la requête liée aux associations de manière asynchrone
                async def process_association_query_async():
                    try:
                        # Importer la fonction depuis agentiatestrecup
                        from agent_ia_test_recup import answer_association_question
                        association_response = answer_association_question(question)
                        self.root.after(0, lambda: self.show_assistant_response(association_response))
                    except Exception as e:
                        self.root.after(0, lambda: self.show_error(
                            f"Erreur lors du traitement de la question sur les associations : {str(e)}"))

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.current_task = loop.create_task(process_association_query_async())
                loop.run_until_complete(self.current_task)
                loop.close()
                return

            # Vérifier si c'est une question sur le sport
            elif any(mot in question.lower() for mot in ["sport", "activité physique", "suaps", "gym", "fitness",
                                                         "entraînement", "musculation", "football", "basketball",
                                                         "natation", "tennis", "équipe", "stade", "terrain",
                                                         "compétition", "match", "tournoi", "suaps"]):
                # Traiter la requête liée au sport de manière asynchrone
                async def process_sport_query_async():
                    try:
                        sport_response = answer_sport_question(question)
                        self.root.after(0, lambda: self.show_assistant_response(sport_response))
                    except Exception as e:
                        self.root.after(0, lambda: self.show_error(
                            f"Erreur lors du traitement de la question sur le sport : {str(e)}"))

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.current_task = loop.create_task(process_sport_query_async())
                loop.run_until_complete(self.current_task)
                loop.close()
                return

            else:
                # Chercher une réponse similaire dans la base de données
                similar_answer = agent.find_similar_question(self.data, question)

                if similar_answer:
                    self.root.after(0, lambda: self.show_assistant_response(similar_answer))
                else:
                    # Sinon, lancer la recherche asynchrone
                    async def search_async():
                        try:
                            response = await agent.find_info_for_question(question, self.data, self.urls,
                                                                          self.cached_data)
                            self.root.after(0, lambda: self.show_assistant_response(response))
                        except Exception as e:
                            self.root.after(0, lambda: self.show_error(f"Erreur lors de la recherche : {str(e)}"))

                    # Exécuter la recherche asynchrone
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self.current_task = loop.create_task(search_async())
                    loop.run_until_complete(self.current_task)
                    loop.close()

        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erreur inattendue : {str(e)}"))

        finally:
            # Arrêter l'indicateur de chargement
            self.root.after(0, self.stop_progress)

    def stop_progress(self):
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.status_var.set("Prêt")

    def on_closing(self):
        if self.current_task and not self.current_task.done():
            if messagebox.askokcancel("Quitter", "Une recherche est en cours. Êtes-vous sûr de vouloir quitter ?"):
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    # Vérifier que l'Ollama est installé et accessible
    try:
        import ollama
    except ImportError:
        print("Erreur: Le module 'ollama' n'est pas installé.")
        print("Veuillez l'installer avec: pip install ollama")
        exit(1)

    # Vérifier que les fichiers de données existent ou les créer
    if not os.path.exists("questions_responses.json"):
        with open("questions_responses.json", "w") as f:
            f.write("{}")

    if not os.path.exists("cached_pages.json"):
        with open("cached_pages.json", "w") as f:
            f.write("{}")

    # Lancer l'application
    root = tk.Tk()
    app = UniversityChatbotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()