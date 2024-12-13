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
        response = golomt_collection.generate.near_text(
                query=text_query, 
                grouped_task="Describe {text} in a formal text in Mongolian.", 
                limit=3
            )
        

        for obj in response.objects:
            print(f"Information chunk relayed to the chatbot: \n\n{obj.properties} \n\n")

        print(f"Чатботоос ирсэн хариулт:\n")

        print(f"\n{response.generated}\n\n")

    conn.close()

if __name__ == "__main__":
    main()
