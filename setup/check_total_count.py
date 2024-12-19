import weaviate
client = weaviate.connect_to_local()
faq = client.collections.get("GolomtRegulations")
aggregation = faq.aggregate.over_all(total_count=True)
print(f"Total count of GolomtRegulations={aggregation.total_count}")
client.close()
