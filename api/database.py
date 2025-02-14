import importlib.resources as pkg_resources

from sqlmodel import SQLModel, create_engine

with pkg_resources.path("api", "../data/duck.db") as db_path:
    DATABASE_URL = f"duckdb:///{db_path}"
engine = create_engine(DATABASE_URL, echo=False)


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)
