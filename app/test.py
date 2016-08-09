
import asyncio
import threading
import time

async def call(d):
    print('1')
    await async_call(d)
    print('2')


@asyncio.coroutine
def async_call(d):
    def delay(d, future):
        print('begin')
        time.sleep(d)
        print('middle')
        loop.call_soon_threadsafe(future.done)
        print('end')

    future = loop.create_future()
    thread = threading.Thread(target=delay, args=(d, future))
    thread.start()
    return (yield from future)

loop = asyncio.get_event_loop()
tasks = [
    call(3),
    call(1),
    call(1.5)
]
loop.run_until_complete(asyncio.gather(*tasks))
loop.close()
