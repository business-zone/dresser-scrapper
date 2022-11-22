import scrapy


class DressersSpider(scrapy.Spider):
    name = "dressers"

    def start_requests(self):
        MAIN_URL = "https://www.agatameble.pl/meble/przechowywanie/komody"
        yield scrapy.Request(url=MAIN_URL, callback=self.parse)

    def parse(self, response):
        style_filter = response.css("div.m-filters_singleWrapper.is-TEXT.is-filterList_1").css('#js-filters_list3-1')
        for style in style_filter.css('span.m-filters_txt.is-customCheckbox_inp.js-checkSubmit::text'):
            style_name = style.get().lower().replace(" ", "").replace("ł", "l")
            style_url = f"https://www.agatameble.pl/meble/przechowywanie/komody/styl:{style_name}"
            yield scrapy.Request(url=style_url, callback=self.parse_style)

    def parse_style(self, response):
        pages_number = response.css("span.m-pagination_count::text").get().replace("z ", "")
        for page in range(1, int(pages_number) + 1):
            page_url = response.request.url + f"?page={str(page)}"
            yield scrapy.Request(url=page_url, callback=self.parse_urls)

    def parse_urls(self, response):
        for dresser in response.css("div.m-offerBox_name"):
            dresser_url = f"https://www.agatameble.pl{dresser.css('a').attrib['href']}"
            yield scrapy.Request(url=dresser_url, callback=self.parse_dresser)

    def parse_dresser(self, response):
        name = response.css("h1.m-typo.m-typo_primary.is-full::text").get()
        if not name:
            name = response.css("h1.m-typo.m-typo_primary::text").get()
        yield {
            "name": name,
            "price": response.css("div.m-priceBox_price.m-priceBox_promo::text").get().replace(",-", "")
        }
