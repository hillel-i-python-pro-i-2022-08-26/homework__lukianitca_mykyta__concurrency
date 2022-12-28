import asyncio
import aiohttp

from services import MapQueue, TaskRequest, Config, init_logger


async def main():
    links = [
        "https://nz.ua/",
        "https://github.com/",
        "https://www.tiktok.com/",
        "https://www.linkedin.com/",
        "https://exame.com/invest/mercados/jovens-periferia-sao-paulo-estrelas-programacao-eua/",
    ]
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
    }
    queue_obj = MapQueue()
    config = Config(max_depth=2)
    semaphore = asyncio.Semaphore(20)
    logger = init_logger()
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(headers=header, timeout=timeout) as session:
        await asyncio.gather(
            *[
                TaskRequest(url, session, queue_obj, logger, config=config, semaphore=semaphore).parse()
                for url in links
            ],
        )
        while not queue_obj.queue.empty():
            new_tasks = await queue_obj.get_all_tasks()
            await asyncio.gather(*[task.parse() for task in new_tasks])
    queue_obj.write_links()


if __name__ == "__main__":
    asyncio.run(main())
