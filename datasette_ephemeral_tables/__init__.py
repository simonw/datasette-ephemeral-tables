from datasette import hookimpl
from functools import wraps
import asyncio
import collections
import time

JAVASCRIPT = """
let ephemeralExpiresAt = new Date();
ephemeralExpiresAt.setSeconds(ephemeralExpiresAt.getSeconds() + %s);

function ephemeralFormatSecondsAsMinutesAndSeconds(seconds) {
    var minutes = Math.floor(seconds / 60);
    if (minutes >= 10) {
        return `${minutes}m`;
    }
    seconds = Math.ceil(seconds - minutes * 60);
    if (minutes) {
        return `${minutes}m ${seconds}s`;
    } else {
        return `${seconds}s`;
    }
}

window.addEventListener("load", function() {
    // Add div#ephemeral-timer
    let timeRemainingDiv = document.createElement('div');
    timeRemainingDiv.id = 'ephemeral-timer';
    timeRemainingDiv.style.padding = '0.5em';
    timeRemainingDiv.style.marginBottom = '0.75rem';
    timeRemainingDiv.style.backgroundColor = 'pink';
    timeRemainingDiv.style.color = 'black';
    document.querySelector('.page-header').insertAdjacentElement('afterend', timeRemainingDiv);

    // Every 1s, update the time remaining
    let interval = setInterval(() => {
        const now = new Date();
        const secondsRemaining = (ephemeralExpiresAt - now) / 1000;
        if (secondsRemaining <= 0) {
            clearInterval(interval);
            timeRemainingDiv.innerText = 'This table has expired';
        } else {
            const timeRemaining = ephemeralFormatSecondsAsMinutesAndSeconds(secondsRemaining);
            timeRemainingDiv.innerText = `This table expires in ${timeRemaining}`;
        }
    });
});
"""


Settings = collections.namedtuple("Settings", ("name", "table_ttl", "poll_interval"))


def _settings(datasette):
    plugin_config = datasette.plugin_config("datasette-ephemeral-tables") or {}
    return Settings(
        name=plugin_config.get("name", "ephemeral"),
        table_ttl=plugin_config.get("table_ttl", 5 * 60),
        poll_interval=plugin_config.get("poll_interval", 2),
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
    db = datasette.add_memory_database(_settings(datasette).name)
    db._known_tables = {}


@hookimpl
def asgi_wrapper(datasette):
    settings = _settings(datasette)

    def wrapper(app):
        @wraps(app)
        async def ensure_task_running(scope, receive, send):
            if not getattr(datasette, "_datasette_demo_database_loop", None):
                datasette._datasette_demo_database_loop = asyncio.create_task(
                    keep_checking(datasette, settings.name, settings.poll_interval)
                )
            return await app(scope, receive, send)

        return ensure_task_running

    return wrapper


async def keep_checking(datasette, name, interval):
    while True:
        await check_for_new_tables(datasette, name)
        await asyncio.sleep(interval)


@hookimpl
def extra_body_script(database, table, view_name, datasette):
    settings = _settings(datasette)
    if view_name != "table" or database != settings.name:
        return
    table_created_at = datasette.get_database(database)._known_tables.get(table)
    if table_created_at is None:
        return
    seconds_until_expires = settings.table_ttl - (time.monotonic() - table_created_at)
    return JAVASCRIPT % str(seconds_until_expires)
