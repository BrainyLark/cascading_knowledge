import logging

from setup.vectordb_conn import Connection
from weaviate.classes.query import Filter
from sentence_transformers import SentenceTransformer

class QAManager:

    def __init__(self, logger, collection_label):
        """ Like ChunkManager, it's given a logger and model to transform the data """
        self.logger = logger
        self.connection = Connection()
        self.client = self.connection.get_client()
        self.collection = self.client.collections.get(collection_label)
        self.model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)
        
    def process_query_chunks(self):
        """ 
            You only need a question to find out what chunks correspond to it
            Plus, last updates dates of the chunks and the question determine whether
            the regeneration takes place.
        """
        chunks_table = self.client.collections.get("GolomtRegulations")
        for qa in self.collection.iterator(include_vector=True):
            uuid = qa.uuid
            last_updated = qa.properties["last_updated"]
            search_vector = qa.vector["default"]
            results = chunks_table.query.near_vector(near_vector=search_vector, limit=3)
            for result in results.objects:
                if result.properties["last_updated"] > last_updated:
                    self.logger.info(f"{uuid} is getting updated because it is updated at \
                            {result.properties['last_updated']} later than \
                            {last_updated} when the QA is updated.")

            break
                

def main():

    logging.basicConfig(filename="logs/qamanager_xpmt_4.log", level=logging.INFO)
    logger = logging.getLogger(__name__)

    table_name = "GolomtFAQ"
    qa_manager = QAManager(logger, table_name)
    
    qa_manager.process_query_chunks()

    qa_manager.connection.close()

if __name__ == "__main__":
    main()
