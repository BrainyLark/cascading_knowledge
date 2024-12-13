import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
from connection.vectordb_conn import Connection

def main():
    
    conn = Connection()
    golomt_collection = conn.get_client().collections.get("GolomtbankRegulations")
    
    text_query = ''

    while text_query != 'exit':
        text_query = input("юу мэдмээр байна: ")
        response = golomt_collection.generate.near_text(query=text_query, grouped_task="Describe nicely and formally in Mongolian: {text}", limit=3)

        print(f"Generated output:\n")
        print(response.generated)

    conn.close()

if __name__ == "__main__":
    main()
