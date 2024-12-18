import weaviate
client = weaviate.connect_to_local()
faq = client.collections.get("GolomtFAQ")
aggregation = faq.aggregate.over_all(total_count=True)
print(f"Total count of GolomtFAQ={aggregation.total_count}")
client.close()
