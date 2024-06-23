import reseau as r
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time

HEURES_PAR_ANNEE = 8760 


#########################################
#-------- Algorithme glouton 1 ---------#
#########################################

def conso_departement(couple_dep):
  production = couple_dep[1]
  return production


def autoConnexionsGlouton(res : r.Reseau):
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


#########################################
#-------- Algorithme glouton 2 ---------#
#-------------- aléatoire --------------#
#########################################

def h_voisin(res, point, voisin, dict_voisins, alpha=1):
  puissance_demandee = dict_voisins[voisin]
  dist = res.distance(point, voisin)
  if (dist == 0):
    return 0
  else:
    return puissance_demandee / dist**alpha


def choix_voisin_aleatoire(res, centrale, dict_voisins, beta=1):
  somme_scores = sum([(h_voisin(res, centrale, voisin, dict_voisins)**beta) for voisin in dict_voisins])
  probas_voisins = [(h_voisin(res, centrale, voisin, dict_voisins)**beta) / somme_scores for voisin in dict_voisins]
  voisin_choisi = np.random.choice(list(dict_voisins.keys()), 1, p=probas_voisins)
  return voisin_choisi[0]


def autoConnexionsGlouton2(res : r.Reseau):
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
        #departement_prio = max(puissance_requise, key=puissance_requise.get)
        #departement_prio = max(puissance_requise, 
        #                       key=lambda v: h_voisin(res, centrale, v, puissance_requise))
        departement_prio = choix_voisin_aleatoire(res, centrale, puissance_requise, beta=2)

      else:
        #Sinon, le plus gros consommateur pouvant être alimenté
        #departement_prio = max(pouvant_etre_alimentes, key=pouvant_etre_alimentes.get)
        #departement_prio = max(pouvant_etre_alimentes, 
        #                       key=lambda v: h_voisin(res, centrale, v, pouvant_etre_alimentes))
        departement_prio = choix_voisin_aleatoire(res, centrale, pouvant_etre_alimentes, beta=2)
        
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


def autoConnexionsGlouton3(res : r.Reseau):
  puissance_restante = res.production.copy()
  puissance_decroissante = sorted(res.consommation.items(), key= lambda item : item[1], reverse=True)


  for departement, puissance_dep in puissance_decroissante:
    puissance_requise = puissance_dep

    while (puissance_requise > 0 and puissance_restante != {}):
      def peut_alimenter(couple_centrale_prod):
        prod = couple_centrale_prod[1]
        return prod <= puissance_requise
      
      #Les départements pouvant être alimentés intégralement par la centrale
      pouvant_alimenter = dict(filter(peut_alimenter, puissance_restante.items()))

      if (pouvant_alimenter == {}):
        #S'il n'y en a pas, on prend le plus gros consommateur de tous les départements
        #departement_prio = max(puissance_requise, key=puissance_requise.get)
        #departement_prio = max(puissance_requise, 
        #                       key=lambda v: h_voisin(res, centrale, v, puissance_requise))
        centrale_prio = choix_voisin_aleatoire(res, departement, puissance_restante, beta=2)

      else:
        #Sinon, le plus gros consommateur pouvant être alimenté
        #departement_prio = max(pouvant_etre_alimentes, key=pouvant_etre_alimentes.get)
        #departement_prio = max(pouvant_etre_alimentes, 
        #                       key=lambda v: h_voisin(res, centrale, v, pouvant_etre_alimentes))
        centrale_prio = choix_voisin_aleatoire(res, departement, pouvant_alimenter, beta=2)
        
      consommation_departement_prio = res.consommation[departement]
      alimentation_departement_prio = res.alimentation[departement]
      puissance_centrale = puissance_restante[centrale_prio]
      
      res.ajouteConnexion(departement, centrale_prio)

      if (alimentation_departement_prio + puissance_centrale < consommation_departement_prio):
        #Le département n'est pas totalement alimenté, la centrale a utilisé toute sa puissance
        res.alimentation[departement] += puissance_centrale
        del puissance_restante[centrale_prio]
        puissance_requise -= puissance_centrale

      else:
        #Il est totalement alimenté, il reste de la puissance à la centrale
        res.alimentation[departement] = consommation_departement_prio
        puissance_restante[centrale_prio] -= puissance_requise
        puissance_requise = 0


#########################################
#-------- Algorithme glouton 4 ---------#
#----------- avec des arbres -----------#
#########################################

def indices_valeur_max(matrice, filtre):
  i_max, j_max = 0, 0
  val_max = matrice[0][0]
  for i in filtre:
    ligne = matrice[i]
    for j, val in enumerate(ligne):
      if (val > val_max):
        val_max = val
        i_max, j_max = i, j
  return i_max, j_max


def arbre_centrale(res, centrale):
  puissance_requise = {centrale : 0} | {dep : res.consommation[dep] - res.alimentation[dep] for dep in res.consommation}
  noms = list(puissance_requise.keys())
  scores = np.array([[h_voisin(res, i, j, puissance_requise, alpha=2) for j in puissance_requise] for i in puissance_requise])
  puissance_restante = res.production[centrale]
  connectes = [0]
  while puissance_restante > 0:
    id_depart, id_arrivee = indices_valeur_max(scores, connectes)
    if (id_depart == id_arrivee):
      break
    depart = noms[id_depart]
    arrivee = noms[id_arrivee]
    print(f"{depart} -> {arrivee}")
    # Le meilleur chemin possible va de depart a arrivee
    scores[:, id_arrivee] = 0
    # On met toute la colonne du nouvel élément à 0 puisqu'il est à présent connecté
    res.ajouteConnexion(depart, arrivee)
    res.alimentation[arrivee] = min(
      res.consommation[arrivee], 
      res.alimentation[arrivee] + puissance_restante
    )
    puissance_restante -= res.consommation[arrivee]
    print(f"Puissance restante : {puissance_restante}")
    # On connecte depart et arrivee
    connectes.append(id_arrivee)
    # arrivee est à présent accessible


def numerotation_composantes(res):
  i = 0
  composantes = [None for _ in res.consommation]
  composantes.extend(range(len(res.production)))
  return composantes

def update_composantes(composantes, puissance_composantes, id_depart, id_arrivee, puissance_arrivee):
  nouvelle_composante = composantes[id_depart]
  if (composantes[id_arrivee] == None):
    composantes[id_arrivee] = nouvelle_composante
    # On ajoute arrivee à la composante de depart
    puissance_composantes[nouvelle_composante] = max(0, puissance_composantes[nouvelle_composante] - puissance_arrivee)
  else:
    ancienne_composante = composantes[id_arrivee]
    puissance_composantes[nouvelle_composante] += puissance_composantes[ancienne_composante]
    # On fusionne les deux composantes 
    puissance_composantes[nouvelle_composante] = max(0, puissance_composantes[nouvelle_composante] - puissance_arrivee)
    for i, comp in enumerate(composantes):
      if (comp == ancienne_composante):
        composantes[i] = nouvelle_composante
    # On met à jour la liste des composantes
  
  #print(f"composantes : {composantes}")
  #print(f"puissance_composantes : {puissance_composantes}")

def update_scores(res, scores, puissance_requise, id_arrivee, arrivee):
  if (puissance_requise[arrivee] == 0):
    scores[:, id_arrivee] = 0
    # On met toute la colonne du nouvel élément à 0 puisqu'il est à présent connecté
  else:
    scores[:, id_arrivee] = [h_voisin(res, point, arrivee, puissance_requise, alpha=2) for point in puissance_requise | res.production]
    # On recalcule les scores pour ce point

def update_reseau(res, puissance_requise, depart, arrivee, puissance_restante):
  res.ajouteConnexion(depart, arrivee)
  res.alimentation[arrivee] = min(
    res.consommation[arrivee], 
    res.alimentation[arrivee] + puissance_restante
  )
  # On connecte arrivee au réseau
  puissance_requise[arrivee] = max(0, puissance_requise[arrivee] - puissance_restante)
  # On recalcule sa puissance requise


def autoConnexionsForet(res):
  puissance_requise = {dep : res.consommation[dep] - res.alimentation[dep] for dep in res.consommation}
  scores = np.array([[h_voisin(res, i, j, puissance_requise, alpha=2) 
                      for j in puissance_requise] 
                      for i in puissance_requise | res.production])
  # Matrice de taille (d + c)*d ou c est le nombre de centrales et d le nombre de départements
  noms = list(res.consommation.keys()) + list(res.production.keys())
  connectes = list(range(len(puissance_requise), len(scores)))
  # Au début, seules les centrales sont connectées
  composantes = numerotation_composantes(res)
  puissance_composantes = [prod for prod in res.production.values()]
  # La puissance disponible dans chaque composante connexe du graphe
  while True:
    def non_vide(i):
      return puissance_composantes[composantes[i]] != 0
    
    points_de_depart = list(filter(non_vide, connectes))
    id_depart, id_arrivee = indices_valeur_max(scores, points_de_depart)

    depart = noms[id_depart]
    arrivee = noms[id_arrivee]
    # Le meilleur chemin possible va de depart a arrivee
    if (id_depart == id_arrivee or scores[id_depart][id_arrivee] == 0):
      break

    print(f"{depart} -> {arrivee}")
    puissance_arrivee = puissance_requise[arrivee]
    puissance_restante = puissance_composantes[composantes[id_depart]]

    update_composantes(composantes, puissance_composantes, id_depart, id_arrivee, puissance_arrivee)  

    update_reseau(res, puissance_requise, depart, arrivee, puissance_restante)

    update_scores(res, scores, puissance_requise, id_arrivee, arrivee)
    # On connecte depart et arrivee
    connectes.append(id_arrivee)
    # arrivee est à présent accessible







## Exemple : petit réseau

reseau1 = r.reseauVide()

reseau1.ajouteElement('C1', 10, 3, 2, "Centrale")
reseau1.ajouteElement('C2', 5, 7, 1, "Centrale")
reseau1.ajouteElement('C3', 6, 0, 6, "Centrale")
reseau1.ajouteElement('D1', 3, 0, 0, "Département")
reseau1.ajouteElement('D2', 4, 7, 7, "Département")
reseau1.ajouteElement('D3', 8, 1, 2, "Département")
reseau1.ajouteElement('D4', 6, 6, 3, "Département")


#arbre_centrale(reseau1, 'C1')
#autoConnexionsForet(reseau1)

#autoConnexionsGlouton(reseau1)
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

def liste_vers_centrale(liste):
  nom = liste[0]
  latitude = liste[1]
  longitude = liste[2]
  valeur = liste[3]
  return (nom, valeur, longitude, latitude, "Centrale")

centrales_liste = dfc.values.tolist()
centrales_liste = list(map(liste_vers_centrale, centrales_liste))

## Réseau français

centrale1 = ("Centrale 1", 7000, 4.6, 46.9, "Centrale")
centrale2 = ("Centrale 2", 8000, 0.0, 43.9, "Centrale")

reseau_france = r.reseauVide()

reseau_france.ajouteListeElements(departements_elements)
reseau_france.ajouteListeElements(centrales_liste)

#reseau_france.ajouteElement(*centrale1)
#reseau_france.ajouteElement(*centrale2)

#reseau_france.ajouteConnexion("Centrale 1", "Var")
#reseau_france.ajouteConnexion("Centrale 2", "Gironde")
#autoConnexionsGlouton3(reseau_france)
#reseau_france.ajouteConnexion("Blayais", "Finistère")
""""
mega_centrale = ("Méga centrale", 60_000, 2.9, 46.8, "Centrale")
reseau_france.ajouteElement(*mega_centrale)

start = time.perf_counter()
arbre_centrale(reseau_france, 'Méga centrale')
end = time.perf_counter()

print(f"Temps d'éxecution : {end - start} s")
reseau_france.affiche(avecDistances=False)
"""

autoConnexionsForet(reseau_france)
reseau_france.affiche(avecDistances=False)

plt.show()