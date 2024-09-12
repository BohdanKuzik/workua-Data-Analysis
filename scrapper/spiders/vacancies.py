import scrapy
from scrapy.http import Response
from .items import JobItem


class WorkUaJobsSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["work.ua"]
    start_urls = ["https://www.work.ua/en/jobs-python/"]

    def parse(self, response: Response, **kwargs):
        vacancies = response.xpath("//div[contains(@class, 'job-link')]")

        for vacancy in vacancies:
            link = vacancy.xpath(".//h2/a/@href").get()
            if link:
                link = response.urljoin(link)
                yield response.follow(link, self.parse_job_details, meta={"link": link})

        next_page = response.xpath("//a[@class='link-icon' and contains(@href, 'page')]/@href").get()
        if next_page:
            next_page = response.urljoin(next_page)
            self.logger.info(f"Navigating to next page: {next_page}")
            yield response.follow(next_page, self.parse)

    def parse_job_details(self, response: Response):
        item = JobItem(
            title=self.parse_title(response),
            skills=self.parse_skills(response),
            salary=self.parse_salary(response),
            company=self.parse_company(response),
            description=self.parse_description(response),
            link=response.meta["link"]
        )
        yield item

    def parse_title(self, response: Response) -> str:
        return response.xpath("//h1/text()").get(default="").strip()

    def parse_skills(self, response: Response) -> str:
        return ", ".join(response.xpath("//span[@class='ellipsis']/text()").getall())

    def parse_salary(self, response: Response) -> str:
        return (
            response.xpath(
                "//span[@title='Salary']/following-sibling::span[@class='strong-500']/text()"
            )
            .get(default="")
            .replace("\u2009", "")
            .replace("\u202f", "")
            .strip()
        )

    def parse_company(self, response: Response) -> str:
        return (
            response.xpath(
                "//span[@title='Company Information']/following-sibling::a/span[@class='strong-500']/text()"
            )
            .get(default="")
            .strip()
        )

    def parse_description(self, response: Response) -> str:
        job_description = response.xpath(
            "//div[@id='job-description']//text()"
        ).getall()
        return " ".join(job_description).replace("\r\n", "").strip()
