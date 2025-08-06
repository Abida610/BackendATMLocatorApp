from typing import Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
T = TypeVar('T', bound=BaseModel)

# convert SQLAlchemy objects to Pydantic models.
def to_pydantic(db_object: DeclarativeBase, pydantic_model: Type[T]) -> T:
    return pydantic_model(**db_object.__dict__)