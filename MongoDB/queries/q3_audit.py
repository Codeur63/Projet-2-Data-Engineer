# queries/q3_health_centers.py
# Trouver tous les centres de sante actifs sans chaine du froid
# (facility.has_cold_chain = false OU champ absent)
# Grouper par region, calculer le ROI d'un upgrade :
# investissement : nb x 2 500 000 XAF
# revenu additionnel : nb x 35 000 XAF/mois
# A COMPLETER

# Question CTO Operateurs MQL cles 
# Resultat attendu
# Q
# 4 Top 10 distributeurs par CA mensuel
# gere (installations actives seulement) groupby distributor_id, $sum
# monthly_xafListe de 10 distributeurs avec
# CA total
# Q
# 5Installations avec plus de 3 interventions
# correctives dans maintenance_history$expr,
# $size,
# $elemMatchN installations identifiees
# Q
# 6Installations ayant change de plan
# Standard vers Premium dans les 6
# derniers mois$elemMatch
# sur
# contract.history, $dateDiffN installations, X XAF/mois
# additionnel
# Q
# 7Centres de sante actifs sans SLA defini
# (sla_uptime_pct absent ou null)$and, $or, $exists, $typeListe des centres sans SLA
# Q
# 8Clients 'Platinum' : loyalty_score > 75
# ET contrat depuis > 2 ans$gte, $lt, $dateDiff, $andN clients Platinum avec CA
# total
