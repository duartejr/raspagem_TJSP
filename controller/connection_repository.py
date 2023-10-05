from typing import Dict, List


class CollectionRepository:
    def __init__(self, db_connection) -> None:
        self.__collection_name = "tjsp"
        self.__db_connection = db_connection
    
    
    def insert_document(self, document: Dict) -> Dict:
        collection = self.__db_connection.get_collection(self.__collection_name)
        document['_id'] = document['Número processo']
        
        try:
            collection.insert_one(document)
        except Exception as e:
            collection.delete_one({"_id": document["_id"]})
            collection.insert_one(document)
            
        return document
    
    
    def insert_list_of_documents(self, list_of_documents: List[Dict]) -> List[Dict]:
        collection = self.__db_connection.get_collection(self.__collection_name)
        collection.insert_many(list_of_documents)
        
        return list_of_documents
    
    
    def select_many(self, order: Dict) -> List[Dict]:
        collection = self.__db_connection.get_collection(self.__collection_name)        
        data = collection.find(order)
        answer = []
        
        for x in data:
            answer.append(x)
            
        return answer
    
    
    def delete_documents(self, documents):
        collection = self.__db_connection.get_collection(self.__collection_name)
        
        for document in documents:
            print(document['_id'])
            collection.delete_one({"_id": document["_id"]})

        
