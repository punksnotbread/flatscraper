import scrapy

MAX_PRICE = 1000


class DomopliusSpider(scrapy.Spider):
    name = "domoplius"
    allowed_domains = ["domoplius.lt"]
    meta = {"impersonate": "chrome"}

    def start_requests(self):
        urls = [
            f"https://domoplius.lt/skelbimai/butai?action_type=3&address_1=461&address_2[3_20]=3_20&address_2[3_27]=3_27&sell_price_to={MAX_PRICE}",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_search, meta=self.meta)

    def parse_search(self, response):
        for listing in response.xpath('.//div[@class="item lt"]/div/a/@href'):
            yield scrapy.Request(
                listing.get(),
                callback=self.parse_product,
                meta=self.meta,
            )

        next_page_url = response.xpath('.//li/a[@class="next"]/@href').extract()
        if next_page_url is not None:
            if not len(next_page_url):
                return

            next_page_url = next_page_url[-1]
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse_search,
                meta=self.meta,
            )

    def parse_product(self, response):
        data = {}
        data["price"] = (
            response.xpath(
                './/th[contains(text(), "Nuomos kaina")]/following-sibling::td/strong/text()'
            )
            .get()
            .split(" ")[0]
        )
        data["rooms"] = response.xpath(
            './/th[contains(text(), "Kambarių skaičius:")]/following-sibling::td/strong/text()'
        ).get()
        data["area"] = (
            response.xpath(
                './/th[contains(text(), "Buto plotas (kv. m):")]/following-sibling::td/strong/text()'
            )
            .get()
            .split(" ")[0]
        )
        data["floor"] = (
            response.xpath(
                './/th[contains(text(), "Aukštas:")]/following-sibling::td/strong/text()'
            )
            .get()
            .split(",")[0]
        )
        data["url"] = response.url

        yield data
