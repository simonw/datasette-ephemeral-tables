from datasette import hookimpl
from functools import wraps
import asyncio
import collections
import time

TABLE_TTL = 30

Settings = collections.namedtuple("Settings", ("table_ttl", "database_name"))


def _settings(datasette):
    plugin_config = datasette.plugin_config("datasette-ephemeral-tables") or {}
    return Settings(
        table_ttl=plugin_config.get("table_ttl", 5 * 60),
        database_name=plugin_config.get("database_name", "ephemeral"),
    )


async def check_for_new_tables(datasette, name):
    # This will be called every X seconds
    table_ttl = _settings(datasette).table_ttl
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
        # Drop any tables that are older than table_ttl seconds
        expired_tables = [
            name
            for name, created in db._known_tables.items()
            if time.monotonic() - created > table_ttl
        ]
        for table in expired_tables:
            await db.execute_write("DROP TABLE {}".format(table))
            del db._known_tables[table]
    except Exception as e:
        print("Error in check_for_new_tables:", e)


@hookimpl
def startup(datasette):
    db = datasette.add_memory_database(_settings(datasette).database_name)
    db._known_tables = {}


@hookimpl
def asgi_wrapper(datasette):
    settings = _settings(datasette)

    def wrapper(app):
        @wraps(app)
        async def ensure_task_running(scope, receive, send):
            if not getattr(datasette, "_datasette_demo_database_loop", None):
                datasette._datasette_demo_database_loop = asyncio.create_task(
                    keep_checking(datasette, settings.database_name)
                )
            return await app(scope, receive, send)

        return ensure_task_running

    return wrapper


async def keep_checking(datasette, name):
    while True:
        await check_for_new_tables(datasette, name)
        await asyncio.sleep(2)
