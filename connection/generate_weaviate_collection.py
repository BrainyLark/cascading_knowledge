import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import Auth
from vectordb_conn import Connection

from sentence_transformers import SentenceTransformer

def generate_reg_collection(client):
    try:
        golomt_regulations = client.collections.create(
            name="GolomtRegulations",
            properties=[
                wvc.config.Property(name="doc_id", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="chunk_index", data_type=wvc.config.DataType.INT),
                wvc.config.Property(name="chunk_hash", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            generative_config=wvc.config.Configure.Generative.openai(model="gpt-4o-mini")
        )
    except Exception as exception:
        print(f"An error occured in creating GolomtRegulations collection: {exception}")


def generate_faq_collection(client):
    try:
        golomt_faq = client.collections.create(
            name="GolomtFAQ",
            properties=[
                wvc.config.Property(name="question", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="response", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="question_v", data_type=wvc.config.DataType.NUMBER_ARRAY),
                wvc.config.Property(name="response_v", data_type=wvc.config.DataType.NUMBER_ARRAY),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            generative_config=wvc.config.Configure.Generative.openai(model="gpt-4o-mini")
        )
    except Exception as exception:
        print(f"Error appeared in creating GolomtFAQ: {exception}")


def main():

    print(f"Connecting to  the WCD server...")
    connection = Connection()
    client = connection.get_client()
    generate_reg_collection(client);
    print(f"Constructed GolomtRegulations successfully...")
    connection.close()

if __name__ == "__main__":
    main()
