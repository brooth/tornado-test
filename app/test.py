
import asyncio
import threading
import time

async def call(d):
    print('call from %s' % threading.current_thread())
    await async_call(d)
    print('end call from %s' % threading.current_thread())


@asyncio.coroutine
def async_call(d):
    def delay():
        print('delay from %s' % threading.current_thread())
        time.sleep(d)
        print('end delay from %s' % threading.current_thread())

    loop = asyncio.get_event_loop()
    return (yield from loop.run_in_executor(None, delay))

loop = asyncio.get_event_loop()
tasks = [
    call(3),
    call(1),
    call(1.5),
    call(5)
]
loop.run_until_complete(asyncio.gather(*tasks))
loop.close()
