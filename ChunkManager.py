import hashlib
import logging
from datetime import datetime
from weaviate.util import generate_uuid5 
from weaviate.classes.query import Filter
from setup.vectordb_conn import Connection
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredHTMLLoader
from sentence_transformers import SentenceTransformer

class ChunkManager:

    def __init__(self, logger, chunk_size=1200, chunk_overlap=200, collection_name="GolomtRegulations"):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.connection = Connection()
        self.client = self.connection.get_client()
        self.collection = self.client.collections.get(collection_name)
        self.model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)
        self.logger = logger

    
    def calculate_chunk_hash(self, text):
        """ A unique fingerprint on the chunk. """
        return hashlib.md5(text.encode()).hexdigest()

    
    def get_document_chunks(self, doc_path):
        loader = UnstructuredHTMLLoader(doc_path)
        document = loader.load()
        return self.text_splitter.split_documents(document)
    
    def store_chunk_metadata(self, doc_id, chunks):
        chunk_metadata = []

        for i, chunk in enumerate(chunks):
            chunk_hash = self.calculate_chunk_hash(chunk.page_content)
            last_updated = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            metadata = {
                "doc_id": doc_id,
                "chunk_index": i,
                "chunk_hash": chunk_hash,
                "content": chunk.page_content,
                "last_updated": last_updated
            }

            chunk_metadata.append(metadata)

        return chunk_metadata

    def update_chunks(self, doc_id, new_chunks):
        """Update doc_id chunks based on differences from new chunks"""
        response = self.collection.query.fetch_objects(filters=Filter.by_property("doc_id").equal(doc_id))
        existing_chunks = [obj.properties for obj in response]
        new_chunk_metadata = self.store_chunk_metadata(doc_id, new_chunks)

        self.process_chunk_updates(existing_chunks, new_chunk_metadata)
        
    def process_chunk_updates(self, existing_chunks, new_chunk_metadata):
        """ Identify differences using hashes much faster than raw string matching """
        existing_hashes = {chunk['chunk_hash'] for chunk in existing_chunks}
        new_hashes = {chunk['chunk_hash'] for chunk in new_chunk_metadata}

        chunks_to_add = [chunk for chunk in new_chunk_metadata if chunk['chunk_hash'] not in existing_hashes]
        chunks_to_delete = [chunk for chunk in new_chunk_metadata if chunk['chunk_hash'] not in new_hashes]
        self.batch_update_weaviate(chunks_to_add, chunks_to_delete)
    
    def batch_update_weaviate(self, chunks_to_add, chunks_to_delete):
        hashes_to_delete = {chunk["chunk_hash"] for chunk in chunks_to_delete}
        deleted = self.collection.data.delete_many(where=Filter.by_property("chunk_hash").contains_any(list(hashes_to_delete)))
        
        self.logger.info(f"Hashes chosen to be deleted: {hashes_to_delete}")
        self.logger.info(f"Deletion summary: {deleted}")

        with self.collection.batch.dynamic() as batch:
            for metadata in chunks_to_add:
                content_encoded = self.model.encode(metadata["content"], task="retrieval.passage")
                batch.add_object(properties=metadata, uuid=generate_uuid5(metadata), vector=content_encoded.tolist())

        self.logger.info(f"Num. of chunks added: {len(chunks_to_add)}")


    def populate_table_chunks(self, doc_id, new_chunks):
        """ Initial population with document chunks upon truncation """
        chunk_metadata = self.store_chunk_metadata(doc_id, new_chunks)
        with self.collection.batch.dynamic() as batch:
            for metadata in chunk_metadata:
                content_encoded = self.model.encode(metadata['content'], task='retrieval.passage')
                batch.add_object(properties=metadata, uuid=generate_uuid5(metadata), vector=content_encoded.tolist())
                self.logger.info("Metadata vector:")
                self.logger.info(content_encoded)
                self.logger.info("Metadata properties:")
                self.logger.info(metadata)
                
        self.logger.info(f"{len(new_chunks)} new chunks populated the collection is inserted.")

    def truncate_table_chunks(self, doc_id):
        deleted = self.collection.data.delete_many(where=Filter.by_property("doc_id").equal(doc_id))
        self.logger.info(f"Collection truncate summary: {deleted}")


def main():
    
    logging.basicConfig(filename="logs/chunk_import_xpmt_002.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    chunk_manager = ChunkManager(logger=logger)
    doc_id = "golomtqa/golomt_docs/Зээл.html"
    chunk_manager.truncate_table_chunks(doc_id)
    chunks = chunk_manager.get_document_chunks(doc_id)
    chunk_manager.populate_table_chunks(doc_id, chunks)
    chunk_manager.connection.close()

if __name__ == "__main__":
    main()
