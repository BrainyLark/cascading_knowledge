import os
import weaviate
import weaviate.classes as wvc 
from weaviate.classes.init import Auth
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

class Connection:

    def __init__(self):
        _ = load_dotenv()
        self.client = weaviate.connect_to_local(headers={'X-OpenAI-Api-Key':os.getenv('OPENAI_APIKEY')}) 
        print(f"Client has been set up. Client readiness: {self.client.is_ready()}")
        
    def get_client(self):
        return self.client


    def close(self):
        self.client.close()
        print(f"Client has been shut down!")

    def generate_faq_collection(self):
        print("Generating FAQ collection...")
        try:
            golomt_faq = self.client.collections.create(
                name="GolomtFAQ",
                properties=[
                    wvc.config.Property(name="question", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="response", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="question_v", data_type=wvc.config.DataType.NUMBER_ARRAY),
                    wvc.config.Property(name="response_v", data_type=wvc.config.DataType.NUMBER_ARRAY),
                ],
                generative_config=wvc.config.Configure.Generative.openai(model="gpt-4o-mini"),
                vectorizer_config=wvc.config.Configure.Vectorizer.none()
            )
                
        except Exception as exception:
            print(f"Error appeared in creating GolomtFAQ: {exception}")

        finally:
            print("FAQ Collection generation went well.")

def main():
    connection = Connection()
    connection.generate_faq_collection()
    connection.close()


if __name__ == "__main__":
    main()
