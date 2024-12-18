import os, json
import _pickle as cPickle
from vectordb_conn import Connection
from weaviate.util import generate_uuid5

from sentence_transformers import SentenceTransformer

import logging

def load_and_deserialize():
    
    with open("../golomtqa/golomt_docqa.pkl", "rb") as fp:
        data = cPickle.load(fp)
    
    return data

def main():
    logging.basicConfig(filename=f"logs/golomt_faq_data_import.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Data import has been set off. Collection: GolomtFAQ.")

    model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)

    qas_dataset = load_and_deserialize()["qas"]
    
    connection = Connection()
    golomtfaq = connection.client.collections.get("GolomtFAQ")
   
    batch_size=10
    starting_pt=5375
    for i in range(starting_pt, len(qas_dataset), batch_size):
        batch_complex = []
        question_set = [pair[0] for pair in qas_dataset[i:i+batch_size]]
        response_set = [pair[1] for pair in qas_dataset[i:i+batch_size]]

        logger.info(f"\nBatch={i} embedding kicks off:")
        question_set_embedded = model.encode(question_set, task="text-matching")
        response_set_embedded = model.encode(response_set, task="text-matching")
        logger.info(f"Batch={i} embedding done: set_question/response_embedded={len(question_set_embedded)}")
        
        for pair_complex in zip(question_set, response_set, question_set_embedded, response_set_embedded):
            batch_complex.append(pair_complex)

        with golomtfaq.batch.dynamic() as batch:
            for record_complex in batch_complex:
                complex_record_dict = {
                    "question" : record_complex[0],
                    "response" : record_complex[1],
                    "question_v" : record_complex[2].tolist(),
                    "response_v" : record_complex[3].tolist()
                }
                batch.add_object(properties=complex_record_dict)

        logger.info(f"golomtfaq.batch.failed_objects:")
        logger.info(golomtfaq.batch.failed_objects)
        logger.info(f"Batch={i} insertion done.\n")
        
        del question_set
        del response_set
        del question_set_embedded
        del response_set_embedded
        del batch_complex
        
    logger.info("Data import executed so far.")
    connection.close()


if __name__ == '__main__':
    main()
