from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name", ("custom", None)
)
async def test_database_created_on_startup(name):
    config = {}
    if name:
        config["database_name"] = name
    datasette = Datasette(memory=True, metadata={
        "plugins": {
            "datasette-ephemeral-tables": config
        }
    })
    await datasette.invoke_startup()
    expected = name or "ephemeral"
    assert expected in datasette.databases
