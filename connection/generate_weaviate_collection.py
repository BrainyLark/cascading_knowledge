import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import Auth
from vectordb_conn import Connection

from sentence_transformers import SentenceTransformer

def generate_weaviate_collection():
    
    conn = Connection()

    try:
        golomt_regulations = conn.get_client().collections.create(
            name="GolomtbankRegulations",
            properties=[
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="chunk_id", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="filepath", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="chunk_index", data_type=wvc.config.DataType.INT),
                wvc.config.Property(name="last_updated", data_type=wvc.config.DataType.NUMBER),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_jinaai(model='jina-embeddings-v3'),
            generative_config=wvc.config.Configure.Generative.openai(model='gpt-4o-mini')
        )
    finally:
        conn.close()


def main():
    print(f"Connecting to  the WCD server...")
    generate_weaviate_collection();
    print(f"Created golomtpedia in terms of question and answer.")
    print(f"Successful! Exiting now...")

if __name__ == "__main__":
    main()
