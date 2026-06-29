from solarmboa_influxdb.client import ping

if __name__ == "__main__":
    if ping():
        print("Connexion InfluxDB OK")
    else:
        print("Connexion InfluxDB échouée")