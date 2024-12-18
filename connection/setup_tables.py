import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import Auth
from vectordb_conn import Connection

from sentence_transformers import SentenceTransformer

def setup_policy_table(client):
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
    except Exception as e:
        print(f"An error occured in creating GolomtRegulations collection: {e}")

def restart_faq_table(client):
    try:
        client.collections.delete("GolomtFAQ")
        print("GolomtFAQ table has been deleted.")
    except Exception as e:
        print(f"Exception happened with restarting faq table: {e}")
    finally:
        setup_faq_table(client)

def setup_faq_table(client):
    try:
        golomt_faq = client.collections.create(
            name="GolomtFAQ",
            properties=[
                wvc.config.Property(name="question", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="response", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="last_updated", data_type=wvc.config.DataType.DATE),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            generative_config=wvc.config.Configure.Generative.openai(model="gpt-4o-mini")
        )
    except Exception as e:
        print(f"Error appeared in creating GolomtFAQ: {e}")


def main():

    print(f"Connecting to  the WCD server...")
    connection = Connection()
    client = connection.get_client()
    restart_faq_table(client);
    print(f"Constructed GolomtFAQ successfully...")
    connection.close()

if __name__ == "__main__":
    main()
