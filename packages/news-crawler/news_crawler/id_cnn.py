from lxml import etree, html

from news_crawler._base import (
    NewsCrawler,
    Params,
    ArticleItem,
    ArticleContent
)


class CNNNewsCrawler(NewsCrawler):
    _index_url = 'https://www.cnnindonesia.com/indeks/'

    @property
    def params(self) -> Params:
        params = super().params
        params[self._date_key] = params[self._date_key].strftime('%Y/%m/%d')
        return params

    @staticmethod
    def extract_end_page(index_page: html.HtmlElement) -> int:
        return int(
            list(index_page.findall(".//a[@dtr-evt='halaman']"))[-2].text
        )

    @staticmethod
    def extract_article_items(
            index_page: html.HtmlElement
            ) -> list[ArticleItem]:
        article_item_elements = list(filter(
            lambda el: el.get('href') != '#',
            index_page.findall(".//article/a[@aria-label='link description']")
        ))
        article_items = []
        for article_item_element in article_item_elements:
            article_url = article_item_element.get('href')
            article_title = article_item_element.find('.//h2').text
            article_category = article_item_element.find('.//span/span/span').text
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
            for el in article_page.find_class('breadcrumb')[0].findall('.//a')
        ]


        article_datetime = (
            article_page.find('.//h1')
            .getparent()
            .findall('div')[3]
            .text.strip()
        )
        article_authors = []
        article_cover_url = article_page.find('.//figure/img').get('src')
        article_cover_caption = (
            article_page.find('.//figure/figcaption')
            .text.strip()
        )

        article_content = [
            el
            for el in article_page.find_class('detail-text')[0]
                .iterchildren()
            if not isinstance(el, etree._Comment)
                and el.tag not in ('div', 'table', 'style', 'script')
                and el.text is not None
        ]
        if article_content[0].tag == 'strong':
            strong = article_content[0].text.strip()
            article_content = [
                el.text.replace('\xa0', ' ').strip()
                for el in article_content[1:]
            ]
            article_content[0] = strong + ' - ' + article_content[0]

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
