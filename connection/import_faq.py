import os
import json
import logging
import _pickle as cPickle
from vectordb_conn import Connection
from weaviate.util import generate_uuid5
from datetime import datetime
from sentence_transformers import SentenceTransformer

def load_and_deserialize():
    
    with open("../golomtqa/golomt_docqa.pkl", "rb") as fp:
        data = cPickle.load(fp)
    
    return data

def main():
    logging.basicConfig(filename=f"logs/faq_import_data_xpmt_003.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Data import has started: GolomtFAQ.")

    model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)

    qas_dataset = load_and_deserialize()["qas"]
    connection = Connection()
    faq = connection.client.collections.get("GolomtFAQ")
   
    batch_size=200
    starting_pt=0
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    for i in range(starting_pt, len(qas_dataset), batch_size):
        batch_data = []
        question_batch = [pair[0] for pair in qas_dataset[i:i+batch_size]]
        response_batch = [pair[1] for pair in qas_dataset[i:i+batch_size]]

        logger.info(f"\nBatch={i}-{i+batch_size} encoding happens:")
        question_vectors = model.encode(question_batch, task="retrieval.query")
        logger.info(f"Batch={i}-{i+batch_size} vectorization done.")
        
        for qa_tuple in zip(question_batch, response_batch, question_vectors):
            batch_data.append(qa_tuple)

        with faq.batch.dynamic() as batch:
            for qa_tuple in batch_data:
                record_dict = {
                    "question" : qa_tuple[0],
                    "response" : qa_tuple[1],
                    "last_updated": datetime.now().strftime(datetime_format)
                }
                uuid = generate_uuid5(record_dict)
                batch.add_object(properties=record_dict, vector=qa_tuple[2].tolist(), uuid=uuid)

        logger.info(f"golomtfaq.batch.failed_objects:")
        logger.info(faq.batch.failed_objects)
        logger.info(f"Batch from {i} to {i+batch_size} insertion done.\n")
        
        del question_batch
        del response_batch
        del question_vectors
        del batch_data
        
    logger.info("Data import executed so far.")
    connection.close()


if __name__ == '__main__':
    main()
