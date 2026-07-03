from pathlib import Path

import duckdb
import pytest

from askdata.load_data import build


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("data") / "test.duckdb"
    # force the synthetic sample so tests stay deterministic even when the
    # full Olist CSVs are present in data/olist/
    build(path, olist_dir=Path("/nonexistent"))
    return path


@pytest.fixture(scope="session")
def con(db_path):
    c = duckdb.connect(str(db_path), read_only=True)
    yield c
    c.close()
