# from src.solarmboa.database import get_db
import sys
from pathlib import Path
from statistics import median


sys.path.insert(0, str(Path(__file__).parent.parent))

from src.solarmboa.database import get_db

db = get_db()
col = db["installations"]
# A COMPLETER — produire un rapport complet :



rapport = {
    "total_documents": col.count_documents({}),
    "total_actifs": col.count_documents({"status": "active"}),
    "total_gps_manquant": col.count_documents({"gps_available": False}),
    "par_type": {},  # groupby client_type
    "par_statut": {},  # groupby status
    "par_region": {},  # groupby location.region
    "par_plan": {},  # groupby contract.plan
    "ca_mensuel_total_xaf": sum(doc.get("contract", {}).get("monthly_xaf", 0) for doc in col.find({"status": "active"})),  # sum contract.monthly_xaf (actifs)
    "ca_mensuel_moyen_xaf":None, # ratio de ca_mensuel_total_xaf / total_actifs
    "ca_mensuel_median_xaf": None,  # median de contract.monthly_xaf (actifs)
    "Summary": "Rapport d'audit des installations solaires",
    "action": sum(col.get("contract", {}).get("monthly_xaf",0) for col in col.find({}))
}


rapport["ca_mensuel_moyen_xaf"] = rapport["ca_mensuel_total_xaf"] / rapport["total_actifs"] if rapport["total_actifs"] > 0 else 0

active_monthly_xaf = [
    doc.get("contract", {}).get("monthly_xaf", 0)
    for doc in col.find({"status": "active"})
]
rapport["ca_mensuel_median_xaf"] = median(active_monthly_xaf)

# Hint distribution :
for ct in col.distinct("client_type"):
    rapport["par_type"][ct] = col.count_documents({"client_type": ct})
 
# Hint status    
for ct in col.distinct("status"):
    rapport["par_statut"][ct] = col.count_documents({'status':ct})    

# Hint region
for ct in col.distinct('region'):
    rapport['par_region'][ct] = col.count_documents({'region':ct})
    
# Hint Plan
for ct in col.distinct('tariff_plan'):
    rapport['par_plan'][ct] = col.count_documents({'tariff_plan':ct})        
    
print(rapport)
