import asyncio
from asyncio.exceptions import TimeoutError

import logging

import aiohttp
from aiohttp.client_exceptions import InvalidURL, ClientConnectorError, ServerDisconnectedError, ClientOSError
from bs4 import BeautifulSoup
from urllib import parse

from .datastructures import MapQueue
from .exceptions import RequestError


class Config:
    def __init__(self, max_depth: int | None = None):
        self.max_depth = max_depth


class TaskRequest:
    def __init__(
        self,
        url: str,
        session: aiohttp.ClientSession,
        tasks_queue: MapQueue,
        logger: logging.Logger,
        semaphore: asyncio.Semaphore,
        current_depth: int = 0,
        base_url: str | None = None,
        config: Config = Config(),
    ):
        self.url = url
        self.session = session
        self.tasks_queue = tasks_queue
        self.semaphore = semaphore
        self.base_url = self._set_base_link(base_url)
        self.current_depth = current_depth
        self.config = config
        self.logger = logger

    def _set_base_link(self, new_link):
        if not new_link:
            parsed_new_link = parse.urlparse(self.url)
            return parse.urljoin(parsed_new_link.scheme, parsed_new_link.netloc)
        return new_link

    async def parse(self):
        self.logger.info(f"[ START ] {self.url}")
        parsed_link_text = parse.urlparse(self.url)
        if not parsed_link_text.netloc:
            try:
                self.url = await self._normalize_url()
            except ValueError as exc:
                self.logger.info(exc)
                return
        else:
            self.base_url = f"{parsed_link_text.scheme}://{parsed_link_text.netloc}"
        try:
            new_links = await self._links_extractor__wrapper()
        except RequestError as exc:
            print(exc)
            return
        self.logger.info(f"Links extracted: {len(new_links)} for url: {self.url}")
        if await self._validate_depth():
            base_task_args = {
                "url": None,
                "session": self.session,
                "tasks_queue": self.tasks_queue,
                "logger": self.logger,
                "semaphore": self.semaphore,
                "config": self.config,
                "current_depth": self.current_depth + 1,
                "base_url": self.base_url,
            }
            for link in new_links:
                if link:
                    base_task_args["url"] = link
                    await self.tasks_queue.add_unique(TaskRequest(**base_task_args))
            self.logger.info(f"[ END ] Tasks added for link {self.url}")
            return
        self.logger.info("Final stage")
        await self.tasks_queue.add_to_set(new_links)

    async def _links_extractor__wrapper(self):
        try:
            return await self._extract_links()
        except (
            InvalidURL,
            ClientConnectorError,
            ClientOSError,
            UnicodeDecodeError,
            AssertionError,
            ServerDisconnectedError,
            TimeoutError,
        ) as exc:
            raise RequestError(exc) from exc

    async def _normalize_url(self):
        self.logger.info(f"Normalizing url for {self.url}")
        if not self.base_url:
            raise ValueError("Can't find base link for normalizing")
        return parse.urljoin(self.base_url, self.url)

    async def _validate_depth(self):
        self.logger.info(f"Validating depth for {self.url}")
        if self.config.max_depth:
            return self.current_depth != self.config.max_depth
        return True

    async def _extract_links(self):
        html = await self._get_html_page()
        self.logger.info(f"Extracting links for url: {self.url}")
        soup = BeautifulSoup(html, features="lxml")
        return set(map(lambda anchor: anchor.get("href"), soup.findAll("a")))

    async def _get_html_page(self):
        async with self.semaphore:
            async with self.session.get(self.url) as response:
                self.logger.info(f"Making request for url: {self.url}")
                return await response.text()
