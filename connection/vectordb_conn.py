import weaviate, os
from weaviate.classes.init import Auth
from dotenv import load_dotenv

class Connection:

    def __init__(self):

        load_dotenv()

        self.WCD_URL = os.getenv('WCD_URL')
        self.WCD_APIKEY = os.getenv('WCD_APIKEY')
        self.JINA_APIKEY = os.getenv('JINA_APIKEY')
        self.OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')

        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.WCD_URL,
            auth_credentials=Auth.api_key(self.WCD_APIKEY),
            headers={ 
                'X-JinaAI-Api-Key' : self.JINA_APIKEY,
                'X-OpenAI-Api-Key' : self.OPENAI_APIKEY
                }
        )
        
        print(f"Client has been set up. Client readiness: {self.client.is_ready()}")

        
    def get_client(self):
        return self.client


    def close(self):
        self.client.close()
        print(f"Client has been shut down!")


def main():
    conn = Connection()
    
    conn.close()


if __name__ == "__main__":
    main()
