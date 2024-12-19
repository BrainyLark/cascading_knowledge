import os
import weaviate
import weaviate.classes as wvc 
from weaviate.classes.init import Auth
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

class Connection:

    def __init__(self):
        
        _ = load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_APIKEY")
        self.client = weaviate.connect_to_local(
            headers = {
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        ) 
        
        print(f"Client has been set up. Client readiness: {self.client.is_ready()}")
        
    def get_client(self):
        return self.client

    def close(self):
        self.client.close()
        print(f"Client has been shut down!")

def main():
    connection = Connection()
    connection.close()


if __name__ == "__main__":
    main()
