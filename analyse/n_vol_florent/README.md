# Détection d'anomalies sur plusieurs vols

## Données

On dispose des données de 6 vols :
* E190-E2_20001_0083_29106_52495_request.txt
* E190-E2_20001_0085_29472_53398_request.txt
* E190-E2_20001_0085_29472_53399_request.txt
* E190-E2_20001_0086_30023_54638_request.txt
* E190-E2_20001_0088_29574_53580_request.txt
* E190-E2_20001_0089_29800_54082_request.txt

qu'on abrègera par un numéro pour les identifier (E190-E2_20001_XXXX_XXXXX_XXXXX_request.txt).

## regul

Dans un premier temps, je travaille en n'utilisant que les signaux de régulation (signaux continus), sans utiliser les signaux de targets ni les signaux discrets.

### regul/PCA

*Script : lien*
*Résultats : lien*

### regul/KMeans

*Script : lien*
*Résultats : lien*

## targets

Ici, je me servirai également des signaux targets (continus).

## all

Enfin, on prend en compte tous les signaux, y compris les signaux binaires.