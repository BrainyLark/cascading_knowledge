import logging
from connection.vectordb_conn import Connection
from weaviate.classes.query import Filter

def main():
    
    logging.basicConfig(filename="logs/filtering_regulation_data.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    conn = Connection()
    collection = conn.get_client().collections.get("GolomtRegulations")
    
    response = collection.query.fetch_objects(
        filters=Filter.by_property("chunk_hash").equal("edf9b1e7f435f7068d26749d3ac29961"),
        limit=1
    )

    logger.info(response)

    conn.close()

if __name__ == "__main__":
    main()
