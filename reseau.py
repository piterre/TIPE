import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

CONVERSION_KILOMETRES = 111.139
ECHELLE_MIN = 20
ECHELLE_MAX = 300


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
