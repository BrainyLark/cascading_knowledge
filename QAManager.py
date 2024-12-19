import os
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
        update_dict = {}
        chunks_table = self.client.collections.get("GolomtRegulations")

        # Every query has to be thoroughly inspected for update.
        for qa in self.collection.iterator(include_vector=True):
            last_updated = qa.properties["last_updated"]
            search_vector = qa.vector["default"]
            chunks = chunks_table.query.near_vector(near_vector=search_vector, limit=5)
            for chunk in chunks.objects:
                if chunk.properties["last_updated"] > last_updated:
                    update_dict[str(qa.uuid)] = [x.properties['chunk_hash'] for x in chunks.objects]
                    break

        self.process_query_responses(update_dict)

    def process_query_responses(self, update_dict):
        """
            The process is provided with a dictionary containing QA UUIDs to be updated as keys
            and lists of chunk hashes, as values, used for regenerating the new responses. Remember
            you're required to update the last_updated property of the updated QAs with current
            timestamps, otherwise it'll keep regenerating responses in the future.
        """
        # DIY to prompt your local LLM using the prompt template at your disposal
        for key, value in update_dict.items():
            self.logger.info("{key} : {value}\n\n")

        return True

def main():

    logging.basicConfig(filename="logs/qamanager_xpmt_4.log", level=logging.INFO)
    logger = logging.getLogger(__name__)

    qa_manager = QAManager(logger, "GolomtFAQ")
    qa_manager.process_query_chunks()
    qa_manager.connection.close()

if __name__ == "__main__":
    main()
