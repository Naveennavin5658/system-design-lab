import asyncio, asyncpg


async def main():
    connection = await asyncpg.connect("postgresql://postgres:naveen@localhost:5432/gm-tracker")
    val = await connection.fetchval("SELECT 1")
    print(val)
    await connection.close()

asyncio.run(main())