from pymongo import MongoClient
from .mongo_db_configs import mongo_db_infos


class DBConnectionHandler():
    """
    This class is reponsible to connect with a MongoDB Database.
    """
    def __init__(self) -> None:
        """
        Initilize an object of the class.
        """
        # Makes path to connect with MongoDB.
        self.__connection_string = "mongodb://{}:{}/:?authSource=admin".format(
            mongo_db_infos["HOST"],
            mongo_db_infos["PORT"]
        )
        self.__database_name = mongo_db_infos["DB_NAME"]
        self.__client = None
        self.__db_connection = None
    
    
    def connect_to_db(self):
        """
        Method to connect with the Database.
        """
        self.__client = MongoClient(self.__connection_string)
        self.__db_connection = self.__client[self.__database_name]
    
    
    def get_db_connection(self):
        """
        Method to get the Database connection.

        Returns:
            MongoDb Connection: Connection with the Database.
        """
        return self.__db_connection
    
    
    def get_db_client(self):
        """
        Method do get MogoDB client.

        Returns:
            MongoDB Client: Client of the MongoDB Database.
        """
        return self.__client
    
    
    def close_connection(self):
        """
        Method to end the Database connection.
        """
        self.__client.close()
