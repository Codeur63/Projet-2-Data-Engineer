from typing import Dict, Any
from cassandra.cluster import Cluster
from api.core.config import settings


class CassandraService:
    def __init__(self):
        hosts = [host.strip() for host in settings.cassandra_hosts.split(",")]

        self.cluster = Cluster(
            contact_points=hosts,
            port=settings.cassandra_port,
        )

        self.session = self.cluster.connect(settings.cassandra_keyspace)

        self.insert_stmt = self.session.prepare(
            """
            INSERT INTO sensor_readings (
                sensor_id,
                bucket,
                timestamp,
                installation_id,
                region,
                solar_output_w,
                battery_level_pct,
                consumption_w,
                alert_code
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        
        
        # self.insert_stmt = self.session.prepare(
        #     """
        #     INSERT INTO daily_stats (
        #         installation_id,
        #         start_date,
        #         sensor_id,
        #         avg_solar_w,
        #         max_battery_pct,
        #         max_solar_w, 
        #         min_battery_pct,
        #         timestamp,
        #         total_kwh
        #     )
        #     VALUES (?, ?, ?, ?, ? , ?, ?, ?, ?)
        #     """
        # )
        
        self.query_stmt = self.session.prepare("""
            SELECT * FROM sensor_readings WHERE sensor_id = ? AND bucket = ?
            ORDER BY timestamp desc""")

    def write_telemetry(self, payload: Dict[str, Any]) -> None:
        timestamp = payload["timestamp"]
        bucket = timestamp.strftime("%Y-%m-%d")

        self.session.execute(
            self.insert_stmt,
            (
                payload["sensor_id"],
                bucket,
                timestamp,
                int(payload["installation_id"]),
                payload["region"],
                float(payload["solar_output_w"]),
                float(payload["battery_level_pct"]),
                float(payload["consumption_w"]),
                payload.get("alert_code"),
            )            
        )
    
    def get_telemetry(self, installation_id: int) -> None:
        self.session.execute(
            self.query_stmt, (
                installation_id
            )
        )    


cassandra_service = CassandraService()



# Flashage : Copiez le fichier sur une clé USB vierge à l'aide d'un utilitaire de gravure d'images (comme BalenaEtcher ou Ventoy).Démarrage : Redémarrez l'ordinateur et choisissez la clé USB au démarrage (en utilisant les touches de boot de votre carte mère, type F12 ou F11).Exécution : Sélectionnez l'option de jailbreak dans le menu épuré. Les pilotes optimisés élimineront la détection erronée du CPID à 0x0000. L'iPhone recevra l'exploit à coup sûr. Vous pourrez ensuite réinitialiser votre ordinateur sous votre système habituel et finaliser le nettoyage des fichiers d'activation comme lors de nos étapes précédentes.