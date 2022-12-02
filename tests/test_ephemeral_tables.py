from curses import meta
from datasette.app import Datasette
import asyncio
import pytest
import sqlite3


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ("custom", None))
async def test_database_created_on_startup(name):
    config = {}
    if name:
        config["name"] = name
    datasette = Datasette(
        memory=True, metadata={"plugins": {"datasette-ephemeral-tables": config}}
    )
    await datasette.invoke_startup()
    expected = name or "ephemeral"
    assert expected in datasette.databases


@pytest.mark.asyncio
@pytest.mark.parametrize("table", ("normal", "has_underscore-and-hyphen"))
async def test_table_dropped_after_ttl_seconds(table):
    datasette = Datasette(
        memory=True,
        metadata={
            "plugins": {
                "datasette-ephemeral-tables": {
                    "table_ttl": 0.3,
                    "poll_interval": 0.1,
                }
            }
        },
    )
    await datasette.invoke_startup()
    # Need to do at least one hit to start the mechanisms running
    await datasette.client.get("/ephemeral.json")
    # Now create a table
    db = datasette.get_database("ephemeral")
    await db.execute_write("CREATE TABLE [{}] (id integer primary key)".format(table))
    tables = await db.table_names()
    assert table in tables
    await asyncio.sleep(0.2)
    # Should be registered by now
    assert table in db._known_tables
    await asyncio.sleep(0.4)
    # Should have been dropped
    assert table not in db._known_tables
    tables = await db.table_names()
    assert tables == []


@pytest.mark.asyncio
async def test_timer_on_table_pages(tmpdir):
    db_path = str(tmpdir / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE foo (id integer primary key)")
    datasette = Datasette(
        [db_path],
        metadata={
            "plugins": {
                "datasette-ephemeral-tables": {
                    "poll_interval": 0.1,
                }
            }
        },
    )
    await datasette.invoke_startup()
    response = await datasette.client.get("/test/foo")
    assert "This table expires in" not in response.text
    db = datasette.get_database("ephemeral")
    await db.execute_write("CREATE TABLE foo (id integer primary key)")
    await asyncio.sleep(0.2)
    response = await datasette.client.get("/ephemeral/foo")
    assert "This table expires in" in response.text
