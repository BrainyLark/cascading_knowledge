# Cascading Knowledge Service (IVA)

## Premise

#### 1.1 Objective

Create a service that tracks an update down on the documents in a specified directory, update the vector database collection A with it and subsequently update the cached responses to the frequently asked questions B in the same database in an embedded form.

#### 1.2 Scope

There exist in the vector database a collection of 8170 faq 4-tuples with duplicate records present. A 4-tuple is composed of 2 text properties for the question and the response, whilst the remaining two arrays correspond to their vectorizations. Simultaneously, in a different collection, approximately 300 chunks are embedded into vectors. The flow of cascading effect takes place from the latter to the former, never the other way around.

### Plan

The following table illustrates task descriptions needed to complete the service. The tasks are broken down into broader categories of *setup*, *regulation handling*, *cascade handling* and *response regeneration*. The status of a task is either completed (🟢), found obsolete (🔴), ongoing (🔵) and planned (🟡). Some tasks are accomplished but found obsolete (i.e. 🟢🔴). This is to certify a portion of my time went into the task despite its uselessness at the moment.

| Category      | Task                           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
| ------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| Setup         | 1.1 Set up database            | Started a local Weaviate server. Used a client to create the two collections of schemas in the aforementioned criterion. Both text and vectorization are stored altogether.                                                                                                                                                                                                                                                                              | 🟢     |
| Setup         | 1.2 Populate database (FAQ)    | Batched the QA pairs with their vectorization counterparts (through batch encoding of both questions and responses) in two hundreds and submitted them to the faq collection. (p.s. QA Data could have been cleaner, sentences with a lot of special characters caused so much delay and unnecessary computing loads in CPU in the course of batch encoding. Enough for me to reduce the batch size to 10 to avoid getting my insertion process killed.) | 🟢     |
| Setup         | 1.3 Populate database (chunks) | Used Langchain's HTML parser in addition to Recursive text splitters to create chunks with the length of 1500 chars and the overlap of 100 chars. Chunks are saved in terms of content, id, filepath, index and last modified date.                                                                                                                                                                                                                      | 🟢     |
| Chunk manager | 2.1.a Listen to update         | Created a watchdog listener to the directory of regulation documents regarding Golomt policies. However, it turned obsolete due to rearrangement of all the chunks related to the tampered file. This was done through deleting all the chunks in the collection and creating chunks anew out of the updated document and inserting them again.                                                                                                          | 🟢🔴   |
| Chunk manager | 2.1.b Chunk hashing            | An incoming html document is loaded through unstructured html reader and split into chunks through the recursive text splitter and hashed with md5.                                                                                                                                                                                                                                                                                                      | 🟢     |
| Chunk manager | 2.2 Chunk update               | For a document, the existing chunks and coming chunks are compared in their hashes alone, working out two lists: chunks to delete and chunks to add.                                                                                                                                                                                                                                                                                                     | 🟢     |
| Chunk manager | 2.3 Chunk persistence          | A function to delete the chunks not present in the new chunks, and add the chunks defined by the new document hashes that were not present in the database apriori.                                                                                                                                                                                                                                                                                      | 🟢     |
| Chunk manager | 2.4 Document listener          | A module to listen to the changes in the given directory and invoke 2.1.b to 2.3.                                                                                                                                                                                                                                                                                                                                                                        | 🟢     |
| QA manager    | 3.1 Identify Q'                | Q' is a set of queries subject to change in light of updates on the document chunks. A query's response is updated if and only if the last updated date of one of the chunks related to the query is later than the query's last updated date.                                                                                                                                                                                                           | 🔵     |
| QA manager    | 3.2 Update Q' responses        | Policy chunks are fed into the LLM alongside with the question and the previous response to generate a new response.                                                                                                                                                                                                                                                                                                                                     | 🟡     |
| Other         | 3.3 Connect modules            | Connect Watchdog, QAManager and ChunkManager to synthesize their functions.                                                                                                                                                                                                                                                                                                                                                                              | 🟡     |

### Prerequisite

* Create an environment with Python=3.12 and install `requirements.txt`.

* Place `golomtqa` directory inside the project directory (with .pkl and golomt_docs subdirectory).

* Have `.env` inside`setup` directory, with currently only `OPENAI_APIKEY` in use.

* In `setup/vectordb_conn.py`, configure the connection metadata. 

```python
self.client = weaviate.connect_to_local(headers={'X-OpenAI-Api-Key':os.getenv('OPENAI_APIKEY')}) 
```

### Setup

Create DB collections using `setup/setup_tables.py` via `reset_table(client, table_name)` function. `table_name` can only be `GolomtFAQ` or `GolomtRegulations`, with the former for faq tuples and the latter to store policy document chunks. 

Please add to the schemas of `GolomtFAQ` and `GolomtRegulations` since your current use case may differ, but do not remove any schema property out of it because `ChunkManager.py` and `QAManager.py` functionalities hinge on it.

By running `setup/import_faq.py`, populate `GolomtFAQ` in compliance with the schema. Not to mention, you could also use `setup/check_total_count.py` to see if they're imported.

To populate `GolomtRegulations`, use `ChunkManager.py`'s `populate_table_chunks` function. Remember, here I am not using a batch encoding due to the possibility that a large number of chunks could come in.

### Logs

Create `logs` directory both inside `./setup` and the project root `./`, to track down the flow of the scripts running. Run `query.py` to retrieve some `GolomtRegulations` chunks into the `logs/faq_query_results_001.log` to see its structure.

## License
