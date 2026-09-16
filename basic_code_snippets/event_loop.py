import asyncio, time


async def sample():
    print("Hello")
    await asyncio.sleep(2) #This does not mean stop python for 2 seconds, It approximately means "I can't make progress right now. Give control back to the event loop."
    print("World")

asyncio.run(sample())

async def task_A():
    print("A: Start")
    await asyncio.sleep(2)
    print("A: End")

async def task_B():
    print("B: Start")
    await asyncio.sleep(1)
    print("B: End")

async def task_C():
    await asyncio.gather(task_A(),task_B())


asyncio.run(task_C())


'''
Write two coroutines:
download_file() and query_database(). Make them take 3 seconds and 2 seconds respectively using sleep.
Run them concurrently.

Question: approximately how long should the entire program take?
'''

async def downlaod_file():
    print("Inside download file")
    await asyncio.sleep(3)
    print("File downloaded successfully")

async def query_database():
    print("Started to query database")
    await asyncio.sleep(2)
    print("DB Query is done")

async def run_tasks():
    await asyncio.gather(downlaod_file(),query_database())

asyncio.run(run_tasks())

'''
Co-routines:
'''
async def fetch_data():
    await asyncio.sleep(1)
    return "Data Fetched"

async def wrapper_coroutine():
    print(await fetch_data())
    print("Wrapper executed")

print(asyncio.run(fetch_data()))


async def greet(name):
    await asyncio.sleep(1)
    return f"Hello {name}!"

async def greeting_wrapper(name):
    response = await greet(name)
    output = response + "  Hope you are doing good"
    print("Response of greeting wrapper: ", output)

asyncio.run(greeting_wrapper("Naveen"))


async def start_coroutine():
    print("Starting....")
    await asyncio.sleep(2)
    print("Stopping....")

asyncio.run(start_coroutine())



async def work(name, secs):
    print(f"start {name}")
    await asyncio.sleep(secs)
    print(f"end   {name}")
    return name.upper()

async def sequential():
    t0 = time.perf_counter()
    await work("A", 2)          # runs fully
    await work("B", 2)          # then this
    await work("C", 2)          # then this
    print(f"sequential: {time.perf_counter()-t0:.1f}s")

async def concurrent():
    t0 = time.perf_counter()
    tasks = [
        asyncio.create_task(work("A", 2)),
        asyncio.create_task(work("B", 2)),
        asyncio.create_task(work("C", 2)),
    ]
    results = [await t for t in tasks]
    print(results)
    print(f"concurrent: {time.perf_counter()-t0:.1f}s")

asyncio.run(sequential())   # ~6.0s
asyncio.run(concurrent())   # ~2.0s