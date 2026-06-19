from solarmboa.database import get_db

db = get_db('cheveux')
col = db['installations']


rapport = {
    "Totat_documents": col.count_documents({}),
    "Total_actifs": col.count_documents({'status':'active'})
}

if __name__ == '__main__':
    # print("Base de données connecté : ", get_db('admin'))  
    print('-'*40)
    print('\n')
    print(rapport)