# Plan de développement

## Description du projet

### Objectifs

Titre du PIE : détection d'anomalies dans des données d’essai de systèmes de gestion d’air aéronautiques

* détection automatique d'anomalies dans des données d'essai
* recherche et analyse des causes/corrélations des comportements anormaux
* 


### Parties prenantes

Le projet répond à un besoin de Liebherr Aerospace.

### Hypothèses, contraintes et exigences connues

Hypothèses :
* premier PIE de Liebherr à supaero
* pas encore d'expertise dans le domaine du machine learning

Contraintes et exigences :
* confidentialité des données du client
* solution déployable chez le client
* date de fin de projet
* utilisation du sharepoint de Liebherr


## Organisation

**R**esponsible : responsable du projet

Florent

**A**ccountable : celui qui paie

N/A

**S**upport : équipes support

* équipe pédagogique de sup
* Liebherr

**C**onsult : personnes consultées 

* Marie-Antoinette Gerat

**I**nform : personnes informées

* Rob Vingerhoeds

## Processus du développement

Le projet représente le début d'une expertise en machine learning/data science chez Liebherr.


## WBS/PBS

### Jalons

* Début du projet : octobre 2016
* **Phase 1 (octobre - 21.11)** : Etude bibliographique, Formation sur les systèmes d'air (livrable : Planning de la phase 2)
* 02.11 Revue gestion de projet
* **Phase 2 (21.11 - 13.03)** : Développement et validation d'une/de plusieurs solutions
* 06.12 Revue
* 31.01 Revue
* **Présentation école** (semaine 13.03 - 17.03)


## Définition du projet détaillé

* Gestion de projet 
Communication au sein de l'équipe, et entre l'équipe et les donneurs d'ordre
Compte-rendus de réunions
Respect du planning
Rapports

* Gestion du code
Gestionnaire de version git + Github
Suivi des tâches (tableau de bord agile Github)
Qualité du code
S'assurer de la compatibilité chez le client
Doc technique (généré automatiquement à partir du code)

* Développement

Regroupe les tâches de développement du livrable.

* * Data processing et visualisation

Extraire les données des signaux bruts issus des essais en vol/simulations
Visualisation des signaux pour mettre en évidence les anomalies
Visualisation des résultats

* * Algorithmes de détection d'anomalies

Développement d'algorithmes automatisant la détection des anomalies.
à suivre...

* Documentation

Rédiger une documentation détaillant :
* * les logiciels pré-requis à mettre en place chez le client
* * manuel d'utilsation du livrable.
* * état d'avancement et de validation du livrable

* Bibliographie

Fiches de lecture. Recherche sur l'état de l'art de la détection d'anomalies et sur les méthodes applicables à notre problème.

## Livrables

* Rapport école
* Code + Doc (wiki)


## Risques opportunités

Risques :
* Sujet et critères pas entièrement définis, nécessité de définir un cadre (car nouveau projet, et pas d’expertise côté donneurs d’ordre)
* Passer trop de temps sur la bibliographie
* Ne pas trouver de solution adaptée au problème lors de nos recherches
* Livrer une solution qui ne correspond pas aux attentes des donneurs d’ordre (communication)
* Développer une solution trop spécialisée sur un pb donné, non réutilisable pour d’autres problèmes
* Confidentialité des données

Opportunités :
* améliorer la détection des anomalies

## Suivi

* Tableau de bord agile Github pour le suivi des tâches
* Sharepoint Liebherr pour gestion du calendrier, compte-rendus de rénunions, fiches de lecture
* Communication : e-mail, discussion Sharepoint, Github
* Moyens techniques : git, github, sourcetree, Python, Anaconda
* Réunions régulières, toutes les 2 semaines au début, puis moins souvent (mais des récaps par e-mail)
