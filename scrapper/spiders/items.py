import scrapy


class JobItem(scrapy.Item):
    title = scrapy.Field()
    skills = scrapy.Field()
    salary = scrapy.Field()
    company = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
