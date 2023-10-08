from typing import Dict, List


class CollectionRepository():
    def __init__(self, db_connection) -> None:
        """
        Initialize the Collection Repository. This class contains methods to
        interate in a MongoDB Database.

        Args:
            db_connection (MongoDB connection): Connection with MongoDB
        """
        self.__collection_name = "tjsp" # Collection where the data is storaged.
        self.__db_connection = db_connection
    
    
    def insert_document(self, document: Dict) -> Dict:
        """
        Method to insert documents in the collection.

        Args:
            document (Dict): Document that will be inserted int the collection.

        Returns:
            Dict: documented inserted in the collection.
        """
        # Get collection in the MongoDB
        collection = self.__db_connection.get_collection(self.__collection_name)
        document['_id'] = document['Número processo'] # The document ID is the lawsuit number
        
        try:
            # Try to insert the document in the collection
            collection.insert_one(document)
        except Exception as e:
            # If a error ocurred probably is because the document already exists
            # in the collection. So this methods removes previous registers existing
            # in the collection to insert a new version of the document.
            collection.delete_one({"_id": document["_id"]})
            collection.insert_one(document)
            
        return document
    
    
    def insert_list_of_documents(self, list_of_documents: List[Dict]) -> List[Dict]:
        """
        This method inserts a list of documents into the collection.

        Args:
            list_of_documents (List[Dict]): List of documents to be inserted into the collection.

        Returns:
            List[Dict]: List of documents inserted into the collection.
        """
        collection = self.__db_connection.get_collection(self.__collection_name)
        collection.insert_many(list_of_documents)
        
        return list_of_documents
    
    
    def select_many(self, order: Dict) -> List[Dict]:
        """
        This method selects documents into the collection using the specified
        order.

        Args:
            order (Dict): Parâmeters to find documents into the collection.

        Returns:
            List[Dict]: List of documents founded into the collection.
        """
        collection = self.__db_connection.get_collection(self.__collection_name)        
        data = collection.find(order)
        answer = []
        
        for x in data:
            answer.append(x)
            
        return answer
    
    
    def delete_documents(self, documents: List[Dict]):
        """
        This method deletes documents of the collection.

        Args:
            documents (List[Dict]): List of documents to be deleted
        """
        collection = self.__db_connection.get_collection(self.__collection_name)
        
        for document in documents:
            print(document['_id'])
            collection.delete_one({"_id": document["_id"]})
