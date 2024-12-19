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

def reset_table(client, table_name):
    table_exists = wclient.collections.exists(table_name)
    if table_exists:
        try:
            client.collections.delete(table_title)
            print("GolomtFAQ table has been deleted.")
        except Exception as e:
            print(f"Exception happened with restarting faq table: {e}")

    if table_name == 'GolomtFAQ':
        setup_faq_table(client)
    elif table_name == 'GolomtRegulations':
        setup_policy_table(client)
    else:
        raise ValueError('Table names can only be GolomtFAQ or GolomtRegulations')

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

    connection = Connection()
    client = connection.get_client()
    reset_table(client);
    connection.close()

if __name__ == "__main__":
    main()
