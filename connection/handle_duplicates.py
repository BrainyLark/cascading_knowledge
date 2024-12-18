import weaviate
import weaviate.classes as wvc
from weaviate.classes.aggregate import GroupByAggregate

import logging

def main():
    client = weaviate.connect_to_local()
    logging.basicConfig(filename="aggregation.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    faq = client.collections.get("GolomtFAQ")
    response = faq.aggregate.over_all(
                group_by=GroupByAggregate(prop="question"),
                total_count=True,
            )

    logger.info(response)
    client.close()


if __name__ == "__main__":
    main()
