from solarmboa_graph.client import get_driver, verify_connection,get_session

if __name__  == "__main__":
    try:
        connection = get_driver()
        print("$"*20)
        print("--- Neo4J Connection to Database --- ")
        print("$"*20)
        session = get_session()
        print(f"\n{connection}\n")
        print(verify_connection())
        print(f'Sur la session : {session}')
    except Exception as e :
        print(f"Connexion as fail to neo4j, please retry {e}")       