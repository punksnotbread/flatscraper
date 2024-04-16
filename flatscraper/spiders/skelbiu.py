import scrapy

MAX_PRICE = 1000


class SkelbiuSpider(scrapy.Spider):
    name = "skelbiu"
    allowed_domains = ["skelbiu.lt"]
    meta = {"impersonate": "chrome"}

    def start_requests(self):
        urls = [
            f"https://www.skelbiu.lt/skelbimai/?autocompleted=1&keywords=&cost_min=&cost_max=1000&type=0&district=1&quarter=12%2C16&streets=0&ignorestreets=0&ignore_district=0&space_min=40&space_max=&rooms_min=&rooms_max=&year_min=&year_max=&floor_min=&floor_max=&price_per_unit_min=&price_per_unit_max=&searchAddress=&cities=465&distance=0&mainCity=1&search=1&category_id=322&user_type=0&ad_since_min=0&ad_since_max=0&visited_page=1&orderBy=-1&detailsSearch=1",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_search, meta=self.meta)

    def parse_search(self, response):
        for listing in response.xpath('.//a[contains(@class, "standard-list-item")]'):
            product_url = listing.xpath(".//@href").extract_first()
            yield scrapy.Request(
                response.urljoin(product_url),
                callback=self.parse_product,
                meta=self.meta,
            )

        next_page_url = response.xpath(
            './/a[@class="pagination_link" and @rel="next"]//@href'
        ).extract()
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
            response.xpath('.//p[@class="price"]/text()').get().split(" ")[0]
        )
        data["rooms"] = response.xpath(
            './/div[contains(text(), "Kamb. sk")]/following-sibling::div/text()'
        ).get()
        data["area"] = (
            response.xpath(
                './/div[contains(text(), "Plotas, m")]/following-sibling::div/text()'
            )
            .get()
            .split(" ")[0]
        )
        data["floor"] = response.xpath(
            './/div[contains(text(), "Aukštas")]/following-sibling::div/text()'
        ).get()
        data["url"] = response.url

        yield data
