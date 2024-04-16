import scrapy

MAX_PRICE = 1000


class AruodasSpider(scrapy.Spider):
    name = "aruodas"
    allowed_domains = ["aruodas.lt"]
    meta = {"impersonate": "chrome"}

    def start_requests(self):
        urls = [
            f"https://www.aruodas.lt/butu-nuoma/vilniuje/?FQuartal=12%2C16&FPriceMax={MAX_PRICE}",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_search, meta=self.meta)

    def parse_search(self, response):
        for listing in response.xpath(
            './/div[@class="advert-flex" and child::div[@class="list-remember-v2"]]'
        ):
            product_url = listing.xpath(
                './/div[@class="list-adress-v2 "]//@href'
            ).extract_first()
            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta=self.meta,
            )

        next_page_url = response.xpath('.//div[@class="pagination"]//@href').extract()
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
        summary = response.xpath('.//div[@class="obj-summary"]//text()')[-1].get()
        price, rooms, area, floor = summary.replace("\n", "").strip().split(" / ")
        data["price"] = price.split(" ")[0]
        data["rooms"] = rooms.split(" ")[0]
        data["area"] = area.split(" ")[0]
        data["floor"] = floor.split(" ")[0]
        data["url"] = response.xpath(
            '//dt[text()="Nuoroda"]/following-sibling::dd/text()'
        )[0].get()

        yield data
