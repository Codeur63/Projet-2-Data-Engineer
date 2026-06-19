"""
Pipeline d'importation des données Json brut -> MongoDB
Gerer les impureter des fichiers Json et les importer dans MongoDB
"""

import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError
from solarmboa.database import get_db

logger = logging.getLogger(__name__)


# ------- Mapping des régions et status ----------
REGIONS = {
    "littoral": "Littoral",
    "centre": "Centre",
    "adamaoua": "Adamaoua",
    "ouest": "Ouest",
    "est": "Est",
    "nord": "Nord",
    "extreme-nord": "Extrême-Nord",
    "sud": "Sud",
    "sud-ouest": "Sud-Ouest",
}


STATUS = {
    "active": "active",
    "suspended": "suspended",
    "decommissioned": "decommissioned",
    "actif": "active",
    "en attente": "pending",
    "pending": "pending",
    "churned": "churned",
    "maintenance": "maintenance",
    "resilie": "churned",
}

PLAN_PRICES = {
        "basic": (5000, 10000),
        "standard": (12000, 18000),
        "premium": (22000, 30000),
        "custom": (32000, 45000),
    }

CLIENT_TYPES = {
            "residential": 1.0,
            "school": 1.2,
            "sme": 1.5,
            "health_center": 1.8,
        }
    
GENERATED_PRICES = {
        plan: random.randint(min_val, max_val) 
        for plan, (min_val, max_val) in PLAN_PRICES.items()
    }

DATE_FORMATS = [
    "%d-%m-%Y",  # 30-12-2022
    "%Y-%m-%d",  # 2022-12-30
    "%d/%m/%Y",  # 30/12/2022
    "%Y/%m/%d",  # 2022/12/30
    "%Y-%m-%d",  # 2022-12-30
    "%d-%b-%Y",  # 30-Dec-2022
    "%b-%d-%Y",  # Dec-30-2022
    "%d %b %Y",  # 30 Dec 2022
    "%b %d %Y",  # Dec 30 2022
    "%Y %b %d",  # 2022 Dec 30
    "%Y-%m-%dT%H:%M:%S",  # 2022-12-30T14:48:00
]


def parse_date(date_str: str) -> Optional[datetime]:
    if not date_str or not isinstance(date_str, str):
        logger.warning(f"Invalid date value: {date_str}")
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue


def map_raw_cannonical(raw: dict) -> dict:
    """
        Transformation du format plat vers un schema attendu
        pour mongodb (ex: location.region -> location.region)
    """
    
    cannocial = {
        "installation_id": raw.get("installation_id"),
        "client_name": raw.get("client_name"),
        "client_type": raw.get("client_type"),
        "distributor_id": raw.get("distributor_id"),
        "status": raw.get("status"),
        "location": {
            "city": raw.get("city"),
            "region": raw.get("region"),
            "gps": {
                "type": "Point",
                "coordinates": [
                    raw.get("gps_lon"),
                    raw.get("gps_lat"),
                ],
            }
        },        
        "contract": {
            "plan": raw.get("tariff_plan"),
            "monthly_xaf": raw.get("monthly_xaf", estimate_monthly_xaf(raw)),
            "history": build_contract_history(raw),
        },
         "solar_system": {
            "installation_date": raw.get("install_date"),
            "panel_capacity_wp": raw.get("panel_capacity_wp"),
            "battery_capacity_wh": raw.get("battery_capacity_wh"),
            "num_appliances": raw.get("num_appliances"),
        },
        "metrics": {
            "battery_pct": raw.get("battery_pct"),
            "last_payment_date": raw.get("last_payment_date"),
        },
        "maintenance_history": raw.get("maintenance_history", []),
        "last_alert_code": raw.get("last_alert_code"),
        "facility": build_facility(raw),
        "maintenance_history": build_maintenance_history(raw),
        "sla_uptime_pct": build_sla(raw),
        "loyalty_score": build_loyalty_score(raw),
        "created_at": raw.get("created_at", datetime.utcnow()),
        "updated_at": raw.get("updated_at", datetime.utcnow()),
        
        }
    
    return cannocial
    
def estimate_monthly_xaf(raw: dict) -> Optional[float]:
    """
    Estime un revenu mensuel si le dataset brut ne contient pas monthly_xaf.
    Ce n'est pas une vérité métier, c'est une hypothèse documentée pour permettre
    les analyses CA du TP.
    """

    plan = str(raw.get("tariff_plan", "")).strip().lower()
    client_type = str(raw.get("client_type", "")).strip().lower()

   

    base_price = GENERATED_PRICES.get(plan, 10000)
    
    multiplier = CLIENT_TYPES.get(client_type, 1.0)

    return float(base_price * multiplier)

def build_facility(raw: dict) -> dict:
    client_type = raw.get("client_type")

    if client_type != "health_center":
        return {}

    installation_id = int(raw.get("installation_id", 0))

    return {
        "has_cold_chain": installation_id % 3 != 0
    }


def build_sla(raw: dict) -> float | None:
    if raw.get("client_type") != "health_center":
        return None

    installation_id = int(raw.get("installation_id", 0))

    if installation_id % 4 == 0:
        return None

    return 98.5

def build_loyalty_score(raw: dict) -> int:
    installation_id = int(raw.get("installation_id", 0))
    base = 50 + (installation_id % 51)
    return min(base, 100)

def build_maintenance_history(raw: dict) -> list[dict]:
    installation_id = int(raw.get("installation_id", 0))
    interventions_count = installation_id % 6

    history = []

    for i in range(interventions_count):
        history.append({
            "type": "corrective" if i % 2 == 0 else "preventive",
            "date": datetime.utcnow() - timedelta(days=30 * (i + 1)),
            "technician_id": f"TECH-{(installation_id % 20) + 1:04d}",
            "comment": "Intervention simulée pour enrichissement analytique"
        })

    return history

    
def build_contract_history(raw: dict) -> list[dict]:
    installation_id = int(raw.get("installation_id", 0))
    current_plan = raw.get("tariff_plan")

    if current_plan == "Premium" and installation_id % 5 == 0:
        return [
            {
                "from_plan": "Standard",
                "to_plan": "Premium",
                "change_date": datetime.utcnow() - timedelta(days=90),
                "monthly_xaf_before": 15000,
                "monthly_xaf_after": estimate_monthly_xaf(raw),
            }
        ]

    return []    

def normalize_region(region: str) -> Optional[str]:
    if not region or not isinstance(region, str):
        logger.warning(f"Invalid region value: {region}")
        return None
    for key, value in REGIONS.items():
        if key in region.lower():
            return value.capitalize()


def normalize_gps(loc: Dict) -> Tuple[Dict, List[str]]:
    warns = []
    if "gps" not in loc:
        if "lat" in loc and "lon" in loc:
            lat, lon = float(loc.pop("lat")), float(loc.pop("lon"))
            loc["gps"] = {"type": "Point", "coordinates": [lon, lat]}
        else:
            loc["gps_available"] = False
            warns.append("Missing GPS coordinates")
            return loc, warns
    coords = loc["gps"].get("coordinates", [])
    if len(coords) != 2:
        c0, c1 = float(coords[0]), float(coords[1])
        if not (8 <= c0 <= 16 and 2 <= c1 <= 13):
            loc["gps"]["coordinates"] = [c1, c0]
            warns.append(f"Swapped GPS coordinates: [{c0}, {c1}] -> [{c1}, {c0}]")
        else:
            warns.append(f"GPS coordinates hors cameroun: [{c0}, {c1}]")

    loc["gps_available"] = True
    return loc, warns


def normaliser_document(doc: Dict) -> Tuple[Dict, List[str]]:
    warns = []
    now = datetime.utcnow()

    # Region
    if "location" in doc and "region" in doc["location"]:
        raw = str(doc["location"]["region"]).strip().lower()
        doc["location"]["region"] = REGIONS.get(raw, doc["location"]["region"].strip())

    # GPS
    if "location" in doc:
        doc["location"], gw = normalize_gps(doc["location"])
        warns.extend(gw)

    # Statut
    raw_s = str(doc.get("status", "")).strip().lower()
    doc["status"] = STATUS.get(raw_s, "unknown")
    if doc["status"] == "unknown":
        warns.append(f"Statut inconnu: {raw_s}")

    # Dates
    for path in [("solar_system", "installation_date"), ("contract", "start_date")]:
        obj = doc
        for k in path[:-1]:
            obj = obj.get(k, {})
        if isinstance(obj, dict) and path[-1] in obj:
            val = obj[path[-1]]
            if isinstance(val, str):
                parsed = parse_date(val)
                if parsed:
                    obj[path[-1]] = parsed
            else:
                warns.append(f"Date non parsable: {val}")

    # Battery
    batt = doc.get("metrics", {}).get("battery_pct")
    if batt is not None and batt > 100:
        warns.append(f"battery_pct={batt} plafonne a 100")
        doc.setdefault("metrics", {})["battery_pct"] = 100.0

    # Alert code
    if "last_alert_code" in doc and doc["last_alert_code"]:
        doc["last_alert_code"] = str(doc["last_alert_code"]).upper()

    # Horodatages
    doc.setdefault("created_at", now)
    doc["updated_at"] = now
    return doc, warns


class ImportPipeline:
    """Orchestre l'import complet dans MongoDB local.
    - Charge le fichier Json brut
    - Normalise les données (region, statut, gps, dates...)
    - Gère les doublons (installation_id)
    - Insère dans MongoDB et gère les erreurs d'insertion
    - Retourne un rapport structuré des résultats
    """

    def __init__(self, col: Collection = None):
        self.col = col if col is not None else get_db()["installations"]

    def run(self, json_path: str) -> Dict:
        """Lance le pipeline et retourne un rapport structure."""
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            print(f"Charge : {len(raw):,} documents")

        # Deduplication
        id_count, seen_ids = {}, set()
        for d in raw:
            iid = d.get("installation_id")
            if iid:
                id_count[iid] = id_count.get(iid, 0) + 1
        doublons = {k for k, v in id_count.items() if v > 1}

        # Normalisation
        docs_norm, all_warns = [], []
        for i, doc in enumerate(raw):
            iid = doc.get("installation_id")
            if iid in seen_ids:
                all_warns.append(f"Doublon id={iid} ignore")
                continue
            if iid:
                seen_ids.add(iid)
            canonical_doc = map_raw_cannonical(doc)    
            norm, warns = normaliser_document(canonical_doc)
            docs_norm.append(norm)
            all_warns.extend([f"[id={iid}] {w}" for w in warns])
        # Insertion
        inseres = ignores = 0
        try:
            res = self.col.insert_many(docs_norm, ordered=False)
            inseres = len(res.inserted_ids)
        except BulkWriteError as bwe:
            inseres = bwe.details["nInserted"]
            ignores = len(docs_norm) - inseres
        # Rapport
        rapport = {
            "total_brut": len(raw),
            "doublons": len(doublons),
            "inseres": inseres,
            "ignores": ignores,
            "avertissements": len(all_warns),
            "top_warns": all_warns[:10],
            "distribution_type": {},
            "distribution_statut": {},
        }
        for ct in self.col.distinct("client_type"):
            rapport["distribution_type"][ct] = self.col.count_documents(
                {"client_type": ct}
            )
        for st in self.col.distinct("status"):
            rapport["distribution_statut"][st] = self.col.count_documents(
                {"status": st}
            )
        return rapport
