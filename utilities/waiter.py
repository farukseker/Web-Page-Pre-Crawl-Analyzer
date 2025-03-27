import time
import asyncio


def wait_for_page_load(wait_for_page_load_time: int = 1):
    for _ in range(wait_for_page_load_time, 0, -1):
        time.sleep(1)
        print(f'{_}.second left')


async def async_wait_for_page_load(wait_for_page_load_time: int = 1):
    for _ in range(wait_for_page_load_time, 0, -1):
        await asyncio.sleep(1)
        print(f'{_}.second left')
