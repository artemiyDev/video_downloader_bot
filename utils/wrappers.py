import asyncio
import concurrent.futures
from functools import wraps, partial


def async_wrap(func):
    @wraps(func)
    async def run(*args, executor=None):
        loop = asyncio.get_running_loop()
        pfunc = partial(func, *args)
        return await loop.run_in_executor(executor, pfunc)

    return run


async def run_blocking_io(func, *args):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, func, *args
        )
    return result