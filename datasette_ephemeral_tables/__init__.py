from datasette import hookimpl
from functools import wraps
import asyncio
import time

TABLE_TTL = 30


async def check_for_new_tables(datasette, name):
    # This will be called every X seconds
    try:
        db = datasette.get_database(name)
        tables_names = await db.table_names()
        for table_name in tables_names:
            if table_name not in db._known_tables:
                db._known_tables[table_name] = time.monotonic()
        # Clean up any that are now missing
        to_remove = [name for name in db._known_tables if name not in tables_names]
        for name in to_remove:
            del db._known_tables[name]
        # Drop any tables that are older than TABLE_TTL seconds
        expired_tables = [
            name
            for name, created in db._known_tables.items()
            if time.monotonic() - created > TABLE_TTL
        ]
        for table in expired_tables:
            await db.execute_write("DROP TABLE {}".format(table))
            del db._known_tables[table]
    except Exception as e:
        print("Error in check_for_new_tables:", e)


@hookimpl
def startup(datasette):
    # config = datasette.plugin_config("my-plugin") or {}
    db = datasette.add_memory_database("demo")
    db._known_tables = {}


@hookimpl
def asgi_wrapper(datasette):
    def wrapper(app):
        @wraps(app)
        async def ensure_task_running(scope, receive, send):
            if not getattr(datasette, "_datasette_demo_database_loop", None):
                datasette._datasette_demo_database_loop = asyncio.create_task(
                    keep_checking(datasette, "demo")
                )
            return await app(scope, receive, send)

        return ensure_task_running

    return wrapper


async def keep_checking(datasette, name):
    while True:
        await check_for_new_tables(datasette, name)
        await asyncio.sleep(2)
