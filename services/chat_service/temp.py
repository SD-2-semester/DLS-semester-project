# import uuid
# from typing import Generic, TypeVar, get_args, get_origin

# import sqlalchemy as sa
# from pydantic import BaseModel
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# from chat_service.db.meta import meta


# class Base(DeclarativeBase):
#     """Base model for all other models."""

#     metadata = meta

#     __tablename__: str

#     id: Mapped[uuid.UUID] = mapped_column(
#         sa.UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )


# class MModel(Base):
#     """."""

#     __tablename__ = "yo"


# T = TypeVar("T", bound=BaseModel)
# M = TypeVar("M", bound=Base)


# class TestDTOA(BaseModel):
#     """..."""

#     a: int


# class TestModelB(BaseModel):
#     """..."""

#     b: int


# class TestModelC(BaseModel):
#     """..."""

#     c: bytes


# class MainClass(Generic[M]):
#     model: M

#     def __init_subclass__(cls, **kwargs) -> None:
#         # print("subclass name")
#         # print(cls.__orig_bases__)  # type: ignore

#         print(kwargs)

#         # super().__init_subclass__()

#         for base in cls.__orig_bases__:  # type: ignore

#             model = get_args(base)
#             origin = get_origin(base)
#             if origin is None or not issubclass(origin, MainClass):
#                 continue

#             print(model[0])
#             print(origin)
#         # print(get_args(base)[0])
#         # print(get_origin(base))

#         print("###")

#         # cls.model = TestModel


# class ExtendedMainClass(MainClass, Generic[T]):
#     """..."""


# class SubClassA(MainClass[MModel]):

#     def test(self):
#         print(self.model)


# class ExtendedSubClassA(ExtendedMainClass[TestDTOA], MModel):
#     """..."""


# # class SubClassB(MainClass[TestModelB]):

# #     def test(self):
# #         print(self.model)


# # class SubClassC(MainClass[TestModelC]):

# #     def test(self):
# #         print(self.model)


# # m = MainClass()

# s = SubClassA()
# # s.test()
