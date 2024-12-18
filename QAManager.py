import logging

from connection.vectordb_conn import Connection
from weaviate.classes.query import Filter


class QAManager:

    def __init__(self, logger, collection_label):

        self.logger = logger
        self.connection = Connection()
        self.client = self.connection.get_client()
        self.collection = self.client.collections.get(collection_label)
        
    def retrieve_cached_queries(self):
        """ 
            You only need a question to find out what chunks correspond to it
            Plus, last updates dates of the chunks and the question determine whether
            the regeneration takes place.
        """
        queries = [(obj.properties.question_v) for obj in self.collection.iterator()]
        logger.info(f"{len(queries)} queries are transferred onto memory.")
        return queries

def main():

    collection_label = "GolomtFAQ"

    logging.basicConfig(filename="qamanager_xpmt_001.log", level=logging.INFO)
    logger = logging.getLogger(__name__)

    manager = QAManager(logger, collection_label)

    manager.connection.close()

if __name__ == "__main__":
    main()
