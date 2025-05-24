from typing import Any, TypeAlias, Union

import requests
from datetime import datetime, timedelta
from lxml import html
# from pathlib import Path

Params: TypeAlias = dict[str, Any]
ArticleItem: TypeAlias = dict[str, Any]
ArticleContent: TypeAlias = dict[str, Any]


class NewsCrawler():
    _index_url = None
    _date_key = 'date'
    _page_key = 'page'

    def __init__(
            self,
            start_date: datetime,
            end_date: datetime | None = None,
            *,
            start_page: int = 1,
            end_page: int | None = None
            ):
        self._start_date = start_date
        self._end_date = end_date
        self._current_date = self._start_date

        self._start_page = start_page
        self._end_page = end_page
        self._current_page = self._start_page

    @property
    def params(self) -> Params:
        return {
            self._date_key: self._current_date,
            self._page_key: self._current_page
        }

    def run(
            self,
            raise_error: bool = True
            # dump_dir: Path | None = None
            ) -> dict[str, Union[list[ArticleItem], list[ArticleContent]]]:
        # if dump_dir is not None and dump_dir.is_file():
        #     raise ValueError()

        if self._end_date is not None:
            end_date = self._end_date
        else:
            end_date = self._start_date

        article_items = []
        article_contents = []
        self._current_date = self._start_date
        while self._current_date <= end_date:
            end_page = self._end_page if self._end_page is not None else 100

            # if dump_dir is not None:
            #     dump_index_dir = dump_dir / 'index'
            #     dump_article_dir = dump_dir / 'articles'
            # else:
            #     dump_index_dir = None
            #     dump_article_dir = None

            self._current_page = self._start_page
            while self._current_page <= end_page:
                index_page = self.get_index(
                    self.params,
                    # dump_dir=dump_index_dir
                )
                if self._end_page is None:
                    self._end_page = self.extract_end_page(index_page)
                    end_page = self._end_page

                article_items_ = self.extract_article_items(index_page)
                article_contents_ = []
                for article_item in article_items_:
                    try:
                        article_page = self.get_article_content(
                            article_item,
                            # dump_dir=dump_article_dir
                        )
                        article_content = self.extract_article_content(
                            article_page,
                            article_item['url']
                        )
                        article_contents_.append(article_content)
                    except Exception as exc:
                        if raise_error:
                            raise
                        else:
                            # print(exc)
                            pass

                article_items.extend(article_items_)
                article_contents.extend(article_contents_)

                self._current_page += 1
            self._current_date += timedelta(days=1)

        return {
            'article_items': article_items,
            'article_contents': article_contents
        }

    def get_index(
            self,
            params: Params | None = None,
            # dump_dir: Path | None = None
            ) -> html.HtmlElement:
        # print('Get index page:', params)
        if self._index_url is None:
            raise ValueError()

        if params is None:
            params = self.params

        response = requests.get(self._index_url, params=params)
        index_page = html.fromstring(response.text)

        # if dump_dir is not None:
        #     if dump_dir.is_file(dump_dir):
        #         raise ValueError()

        #     dump_dir.mkdir(parents=True, exist_ok=True)

        #     formatted_date = (
        #         params[self._date_key]
        #         .replace('/', '')
        #         .replace('-', '')
        #     )
        #     formatted_page = f"{params[self._page_key]:03d}"
        #     dump_file = dump_dir / f"{formatted_date}_{formatted_page}.html"
        #     with open(dump_file, 'wb') as f:
        #         f.write(response.content)

        return index_page

    def get_article_content(
            self,
            article_item: ArticleItem,
            # params: Params,
            # dump_dir: Path | None = None
            ) -> html.HtmlElement:
        # print('Get article:', article_item['url'])
        response = requests.get(article_item['url'])
        article_page = html.fromstring(response.text)

        # if dump_dir is not None:
        #     if dump_dir.is_file():
        #         raise ValueError()

        #     dump_dir.mkdir(parents=True, exist_ok=True)

        #     formatted_date = (
        #         params[self._date_key]
        #         .replace('/', '')
        #         .replace('-', '')
        #     )
        #     formatted_page = f"{params[self._page_key]:03d}"
        #     formatted_url = article_item['url'].split('/')[-1]
        #     dump_file = (
        #         dump_dir
        #         / f"{formatted_date}_{formatted_page}_{formatted_url}.html"
        #     )
        #     with open(dump_file, 'wb') as f:
        #         f.write(response.content)

        return article_page

    @staticmethod
    def extract_end_page(index_page: html.HtmlElement) -> int:
        raise NotImplementedError()

    @staticmethod
    def extract_article_items(
            index_page: html.HtmlElement
            ) -> list[ArticleItem]:
        raise NotImplementedError()

    @staticmethod
    def extract_article_content(
            article_page: html.HtmlElement,
            article_url: str
            ) -> ArticleContent:
        raise NotImplementedError()
