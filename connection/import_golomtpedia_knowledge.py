import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure

import os, json
import _pickle as cPickle
from vectordb_conn import Connection


def load_and_deserialize():
    with open('golomtqa/golomt_docqa.pkl', 'rb') as fp:
        data = cPickle.load(fp)

    return data

def main():

    conn = Connection()

    qas = load_and_deserialize()['qas']
    
    golomtpedia = conn.get_client().collections.get("Golomtpedia")
    
    with golomtpedia.batch.dynamic() as batch:
        for record in qas:
            entity = { 'question': record[0], 'answer': record[1] }
            batch.add_object(entity)


    conn.close()


if __name__ == '__main__':
    main()
