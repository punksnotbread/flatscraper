from datetime import datetime

import pymongo


class DataCleanPipeline:
    def process_item(self, item, spider):
        clean = {}

        for key, value in item.items():
            if value is None:
                clean[key] = None
                continue

            if key != "description":
                value = value.replace("\n", "").strip()
                value = value.replace("m²", "")
                value = value.replace("€", "")
                value = value.replace("\n", "").strip()

            if key in ["rooms", "floor"]:
                value = int(value)

            if key in ["price", "area"]:
                value = value.replace(",", ".")
                value = value.replace(" ", "")
                value = float(value)

            clean[key] = value

        if "price" in clean and "area" in clean:
            clean["price_per_m2"] = round(clean["price"] / clean["area"], 2)

        clean["scrape_date"] = datetime.now()

        return clean


class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
            collection_name=crawler.spider.name,
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item
