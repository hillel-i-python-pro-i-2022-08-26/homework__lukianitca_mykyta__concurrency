import asyncio


class MapQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self._elems = set()

    async def add_unique(self, new_elem):
        if new_elem.url not in self._elems:
            await self.queue.put(new_elem)
            self._elems.add(new_elem.url)

    async def add_to_set(self, links):
        self._elems.update(links)

    async def get_all_tasks(self):
        print("STEP IN QUEUE")
        return [await self.queue.get() for _ in range(self.queue.qsize())]

    def write_links(self):
        with open("links_storage/parsed_links.txt", mode="w+") as file:
            file.write("\n".join([link for link in self._elems if link]))
