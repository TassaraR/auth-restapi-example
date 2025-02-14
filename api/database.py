from sqlmodel import SQLModel


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)
