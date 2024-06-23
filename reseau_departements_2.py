import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

CONVERSION_KILOMETRES = 111.139
ECHELLE_MIN = 20
ECHELLE_MAX = 300
HEURES_PAR_ANNEE = 8760


class Reseau:

  def __init__(self, graphe_connexions, production, consommation, alimentation, legende):
    self.graphe = graphe_connexions
    self.production = production
    self.consommation = consommation
    self.alimentation = alimentation
    self.legende = legende


  def ajouteElement(self, nom, valeur, x, y, legende='Point'):
    if (legende == 'Centrale'):
      self.production[nom] = valeur
    if (legende == 'Département'):
      self.consommation[nom] = valeur
      self.alimentation[nom] = 0.

    self.legende[nom] = legende
    self.graphe.add_node(nom, pos=(x, y))


  def ajouteListeElements(self, liste_elements):
    for element in liste_elements:
      self.ajouteElement(*element)

  def distance(self, point1, point2):
    x1, y1 = self.graphe.nodes[point1]['pos']
    x2, y2 = self.graphe.nodes[point2]['pos']
    distance_x = (x1 - x2) * CONVERSION_KILOMETRES
    distance_y = (y1 - y2) * CONVERSION_KILOMETRES
    dist = np.sqrt(distance_x**2 + distance_y**2)
    return dist

  def ajouteConnexion(self, point1, point2):
    if (point1 not in self.graphe.nodes or point2 not in self.graphe.nodes):
      raise KeyError("Un des éléments ne fait pas partie du graphe.")
    
    dist = self.distance(point1, point2)
    self.graphe.add_edge(point1, point2, weight=dist)


  def ajouteListeConnexions(self, liste_elements):
    for element1, element2 in liste_elements:
      self.ajouteConnexion(element1, element2)
      
      
  def estAlimente(self, point):
    if (self.legende[point] != 'Département'):
      return False
    departement = point
    return self.alimentation[departement] >= self.consommation[departement]

    
  def affiche(self, avecDistances=True):
    pos = nx.get_node_attributes(self.graphe, 'pos')
    pos_departements = {dep: pos[dep] for dep in self.consommation}
    pos_centrales = {cen: pos[cen] for cen in self.production}

    def echelle(x):
      valeurs = self.consommation | self.production
      valeur_min = min(valeurs.values())
      valeur_max = max(valeurs.values())
      b = (ECHELLE_MIN * valeur_max - ECHELLE_MAX * valeur_min) / (valeur_max - valeur_min)
      a = (ECHELLE_MIN - b) / valeur_min
      return a * x + b
      
    conso_liste = [echelle(self.consommation[dep]) for dep in self.consommation] 
    prod_liste = [echelle(self.production[c]) for c in self.production] 

    couleurs_departements = [couleur_point("Département", self.estAlimente(point)) for point in self.consommation]
    
    nx.draw_networkx_nodes(self.graphe,
                           pos=pos_departements,
                           nodelist=self.consommation.keys(),
                           node_size=conso_liste,
                           node_color=couleurs_departements,
                           )
    
    nx.draw_networkx_nodes(self.graphe,
                           pos=pos_centrales,
                           nodelist=self.production.keys(),
                           node_size=prod_liste,
                           node_color="blue",
                           )
    
    nx.draw_networkx(self.graphe,
                     pos=pos,
                     node_size=0,
                     with_labels=True,
                     font_size=6
                     )
    
    if avecDistances:
      labels = nx.get_edge_attributes(self.graphe, 'weight')
      labels = {edge : f"{round(labels[edge])} km"  for edge in labels}
      nx.draw_networkx_edge_labels(self.graphe, 
                                  pos, 
                                  edge_labels=labels, 
                                  font_size=8)



def reseauVide():
  graphe = nx.Graph()
  production = {}
  consommation = {}
  legende = {}
  alimentation = {}
  reseau_vide = Reseau(graphe, production, consommation, legende, alimentation)
  return reseau_vide


def couleur_point(legende_point, est_alimente):
  if (legende_point == "Département"):
    if (est_alimente):
      return "green"
    else:
      return "red"

  if (legende_point == "Centrale"):
    return "blue"
  
  else:
    return "grey"



def conso_departement(couple_dep):
  production = couple_dep[1]
  return production



def autoConnexionsGlouton(res : Reseau):
  puissance_requise = {dep: (res.consommation[dep] - res.alimentation[dep]) for dep in res.consommation}
  production_decroissante = sorted(res.production.items(), key= lambda item : item[1], reverse=True)


  for centrale, prod_centrale in production_decroissante:
    puissance_restante = prod_centrale

    while (puissance_restante > 0 and puissance_requise != {}):
      def peut_etre_alimente(couple_dep_conso):
        conso = couple_dep_conso[1]
        return conso <= puissance_restante
      
      #Les départements pouvant être alimentés intégralement par la centrale
      pouvant_etre_alimentes = dict(filter(peut_etre_alimente, puissance_requise.items()))

      if (pouvant_etre_alimentes == {}):
        #S'il n'y en a pas, on prend le plus gros consommateur de tous les départements
        departement_prio = max(puissance_requise, key=puissance_requise.get)
      else:
        #Sinon, le plus gros consommateur pouvant être alimenté
        departement_prio = max(pouvant_etre_alimentes, key=pouvant_etre_alimentes.get)
      consommation_departement_prio = res.consommation[departement_prio]
      alimentation_departement_prio = res.alimentation[departement_prio]
      
      res.ajouteConnexion(centrale, departement_prio)

      if (alimentation_departement_prio + puissance_restante < consommation_departement_prio):
        #Le département n'est pas totalement alimenté, la centrale a utilisé toute sa puissance
        res.alimentation[departement_prio] += puissance_restante
        puissance_requise[departement_prio] -= puissance_restante
        puissance_restante = 0
      else:
        #Il est totalement alimenté, il reste de la puissance à la centrale
        res.alimentation[departement_prio] = consommation_departement_prio
        del puissance_requise[departement_prio]
        puissance_restante -= consommation_departement_prio


      


## Exemple : petit réseau

reseau1 = reseauVide()

reseau1.ajouteElement('C1', 10, 3, 2, "Centrale")
reseau1.ajouteElement('C2', 5, 7, 1, "Centrale")
reseau1.ajouteElement('C3', 6, 0, 6, "Centrale")
reseau1.ajouteElement('D1', 3, 0, 0, "Département")
reseau1.ajouteElement('D2', 4, 7, 7, "Département")
reseau1.ajouteElement('D3', 8, 1, 2, "Département")
reseau1.ajouteElement('D4', 6, 6, 3, "Département")


autoConnexionsGlouton(reseau1)
#reseau1.ajouteConnexion('C1', 'D3')
#reseau1.ajouteConnexion('C3', 'D3')
#reseau1.alimentation['D3'] = 8

#reseau1.affiche(avecDistances=False)


## Départements

import pandas as pd

departements = 'conso-departement-annuelle.csv'

df = pd.read_csv(departements)
df = df[df['Année'] == 2022]

df['Consommation électricité (MW)'] = df['Consommation électricité totale (MWh)'].astype(float).multiply(1/HEURES_PAR_ANNEE).round(decimals=0)
df = df.drop(columns=['Année', 'Consommation électricité totale (MWh)'])


def liste_vers_departement(liste):
  nom = liste[0]
  valeur = liste[2]
  y, x = eval(liste[1])
  
  if (nom == 'Martinique'):
    y, x = 46.4, -4.06
  if (nom == 'Guadeloupe'):
    y, x = 45.8, -4.06
  if (nom == 'Guyane'):
    y, x = 45.2, -4.06
  if (nom == 'La Réunion'):
    y, x = 44.6, -4.06
  if (nom == 'Mayotte'):
    y, x = 44.0, -4.06
  #On met les outre-mer dans le golfe de Gascogne pour avoir une carte lisible

  return (nom, valeur, x, y, "Département")


departements_liste = df.values.tolist()
departements_elements = list(map(liste_vers_departement, departements_liste))

# Centrales nucléaires

centrales_nucleaires = 'liste-reacteurs-nucleaires.csv'

dfc = pd.read_csv(centrales_nucleaires)
dfc = dfc.drop(columns=['Nom du réacteur', 'Commune', 'Département', 'Rg', 'Palier',
                        'Puissance thermique (MWt)', 'Puissance brute (MWe)',
                        'Début construction', 'Raccordement au réseau', 'Mise en service'])
dfc = dfc.groupby(['Centrale nucléaire', 'Commune Lat', 'Commune Long'])['Puissance nette (MWe)'].sum().reset_index()
print(dfc)

def liste_vers_centrale(liste):
  nom = liste[0]
  latitude = liste[1]
  longitude = liste[2]
  valeur = liste[3]
  return (nom, valeur, longitude, latitude, "Centrale")

centrales_liste = dfc.values.tolist()
centrales_liste = list(map(liste_vers_centrale, centrales_liste))

#plt.figure()
#from PIL import Image
#carte_france = np.asarray(Image.open("carte_france.png"))
#plt.imshow(carte_france, alpha=0.5)

centrale1 = ("Centrale 1", 7000, 4.6, 46.9, "Centrale")
centrale2 = ("Centrale 2", 8000, 0.0, 43.9, "Centrale")

reseau_france = reseauVide()

reseau_france.ajouteListeElements(departements_elements)
reseau_france.ajouteListeElements(centrales_liste)

#reseau_france.ajouteElement(*centrale1)
#reseau_france.ajouteElement(*centrale2)

#reseau_france.ajouteConnexion("Centrale 1", "Var")
#reseau_france.ajouteConnexion("Centrale 2", "Gironde")
#autoConnexionsGlouton(reseau_france)
#reseau_france.ajouteConnexion("Blayais", "Finistère")

#reseau_france.affiche(avecDistances=True)


plt.show()