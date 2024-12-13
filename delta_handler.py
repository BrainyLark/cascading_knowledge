import os, hashlib, time, weaviate

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from typing import List, Sequence, Dict
from connection.vectordb_conn import Connection
from weaviate.classes.query import Filter

from langchain_core.documents import Document
from langchain_text_splitters import HTMLSectionSplitter, RecursiveCharacterTextSplitter

class DocumentAlterationHandler(FileSystemEventHandler):
    
    def __init__(self, client, collection_name: str, chunk_size: int = 1500, chunk_overlap=100) -> None:
        self.client = client
        self.collection = self.client.collections.get(collection_name)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        """
            Файлтай холбоотой чанкуудыг бүгдийг нь устгаж эргэж бүтэцлэж оруулахын сул тал.
            Энэ операцийг аль болох бага хиймээр байгаа учраас дараах идеал кейсүүд дээр ажиллавал зохино:
                1. Файлын өөрчлөлтийг өөр газар хийчхээд адилхан файлын нэртэйгээр фолдерт файлыг replace хийх
                2. Файлын өөрчлөлтийг эх дээр нь удаан хийгээд суугаад байхгүй байх.
        """

        self.last_modified_times: Dict[str, float] = {}
        self.debounce_interval = 60


    def should_process_file(self, filepath: str) -> bool:
        current_time = time.time()
        last_modified = self.last_modified_times.get(filepath, 0)
        if current_time - last_modified >= self.debounce_interval:
            self.last_modified_times[filepath] = current_time
            return True

        return False


    def load_html_document(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return ""


    def chunk_html_string(self, html_string: str) -> List[Document]:
        
        headers_to_split_on = [("h1", "Header 1"), ("h2", "Header 2"), ("h3", "Header 3"), ("h4", "Header 4")]
        html_splitter = HTMLSectionSplitter(headers_to_split_on)
        html_header_splits = html_splitter.split_text(html_string)
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        splits = text_splitter.split_documents(html_header_splits)

        return splits

    def read_and_chunk_document(self, filepath: str) -> List[Document]:
        html_string = self.load_html_document(filepath)
        print(f'{filepath} has been read successfully.')
        chunk_splits = self.chunk_html_string(html_string)
        print(f'Chunking {filepath} is executed right! Sending back...')
        return chunk_splits

    def create_new_chunks(self, filepath: str, chunks: List[Document]):
        try:
            dataset = []
            for i, document in enumerate(chunks):
                chunk_id = f"{filepath}_{i}"
                data_record = {
                    "content": document.page_content,
                    "chunk_id": chunk_id,
                    "filepath": filepath,
                    "chunk_index": i,
                    "last_updated": time.time()
                }
                dataset.append(data_record)

            with self.collection.batch.dynamic() as batch:
                for record in dataset:
                    batch.add_object(properties=record)

        except Exception as e:
            print(f"There occured an error creating new chunks with filepath={filepath}: \n\n {e}")


    def delete_document_chunks(self, filepath: str):
        try:
            self.collection.data.delete_many(where=Filter.by_property("filepath").like(filepath))

        except Exception as e:
            print(f"There came across an error deleting the file chunks with filepath={filepath}. See more as follows: \n\n {e}")

        finally:
            print(f"Deletion with respect to filepath={filepath} has been carried out successfully!\n\n")

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.html'):
            return

        filepath = event.src_path

        print(f"filepath={filepath} has been updated.")
        
        if not self.should_process_file(filepath):
            print("However, {filepath} is still yet to be processed.")
            return
        try:
            print(f"Proceeding with the {filepath} updates...\n\n")
            print(f"Deleting everything associated with {filepath}.")
            self.delete_document_chunks(filepath)

            split_chunks = self.read_and_chunk_document(filepath)
            print(f"Inserting the new chunks into {filepath}.")
            self.create_new_chunks(filepath, split_chunks)

        except Exception as e:
            print(f"An error took place in updating {filepath}. Please look for an elaborate error stack that must've been revealed in advance.")

        finally:
            print(f"Successfully updated.")

def main():

    conn = Connection()
    
    event_handler = DocumentAlterationHandler(conn.get_client(), 'GolomtbankRegulations', chunk_size=500, chunk_overlap=30)
    directory_path = './golomtqa/golomt_docs'
    
    observer = Observer()
    observer.schedule(event_handler, directory_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    conn.close()

if __name__ == "__main__":
    main()
