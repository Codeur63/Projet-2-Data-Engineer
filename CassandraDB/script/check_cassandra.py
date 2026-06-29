from cassandradb.client import get_session

if __name__ == "__main__":
    print("=="*40)
    print("Test de connnection a cassandra\n")
    print("==" *40)
    
    try:
        conn = get_session()
        print("Connection with : ", conn)
    except Exception as e:
        print(f"Vous avez une erreur ed Connexion a CassandraDB : {e}")       