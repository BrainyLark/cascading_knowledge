import logging
from setup.vectordb_conn import Connection
from weaviate.classes.query import Filter

def main():
    
    logging.basicConfig(filename="logs/faq_query_results_001.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    connection = Connection()
    client = connection.get_client()
    collection = client.collections.get("GolomtFAQ")
    
    i = 0
    for qa_pair in collection.iterator(include_vector=True):
        logger.info(qa_pair)
        logger.info("\n\n")
        i += 1
        if i > 10:
            break

    connection.close()

if __name__ == "__main__":
    main()
