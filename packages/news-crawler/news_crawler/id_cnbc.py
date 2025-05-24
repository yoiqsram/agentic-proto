from lxml import etree, html

from news_crawler._base import (
    NewsCrawler,
    Params,
    ArticleItem,
    ArticleContent
)


class CNBCNewsCrawler(NewsCrawler):
    _index_url = 'https://www.cnbcindonesia.com/indeks'

    @property
    def params(self) -> Params:
        params = super().params
        params[self._date_key] = params[self._date_key].strftime('%Y/%m/%d')
        return params

    @staticmethod
    def extract_end_page(index_page: html.HtmlElement) -> int:
        return int(
            index_page.findall(".//a[@dtr-evt='halaman']")[-2].text
        )

    @staticmethod
    def extract_article_items(
            index_page: html.HtmlElement
            ) -> list[ArticleItem]:
        article_item_elements = index_page.findall(".//article/a")
        article_items = []
        for article_item_element in article_item_elements:
            article_url = article_item_element.get('href')
            article_metadata = article_item_element.find('.//h2').getparent()
            article_title = article_metadata.find('.//h2').text.strip()
            article_category = article_metadata.find('span').text.strip()
            article_image_url = article_item_element.find('.//img').get('src')

            article_item = {
                'url': article_url,
                'title': article_title,
                'category': article_category,
                'image_url': article_image_url
            }
            article_items.append(article_item)
        
        return article_items

    @staticmethod
    def extract_article_content(
            article_page: html.HtmlElement,
            article_url: str
            ) -> ArticleContent:
        article_title = article_page.find('.//h1').text.strip()
        article_categories = [
            el.text.strip()
            for el in article_page.find(".//nav[@aria-label='Breadcrumb']")
                .findall('a')
        ][1:]

        article_datetime = (
            article_page.findall(".//div[@id='detailHead']/div")[-1]
            .text.strip()
        )
        article_authors = (
            article_page.find(".//div[@id='detailHead']/div/span")
            .getparent()
            .text.strip().strip(',')
        )
        article_cover_url = article_page.find('.//figure/img').get('src')
        article_cover_caption = (
            article_page.find('.//figure/figcaption')
            .text.strip()
        )

        article_content = [
            el.text_content().strip()
            for el in article_page.find(".//div[@class='detail-text']/p")
                .getparent().iterchildren()
            if not isinstance(el, etree._Comment)
                and el.tag not in ('a', 'div', 'table')
        ]
        article_content = '\n'.join(
            filter(lambda text: len(text) > 0, article_content)
        )

        return {
            'url': article_url,
            'title': article_title,
            'datetime': article_datetime,
            'authors': article_authors,
            'categories': article_categories,
            'cover_url': article_cover_url,
            'cover_caption': article_cover_caption,
            'content': article_content
        }
