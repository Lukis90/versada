from enum import StrEnum
from typing import Annotated, Any

from bson import ObjectId
from pydantic import PlainSerializer
from pydantic_core import core_schema


class OID(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)


FloatTwoDecimals = Annotated[
    float, PlainSerializer(lambda x: round(x, 2), return_type=float)
]

FloatFourDecimals = Annotated[
    float, PlainSerializer(lambda x: round(x, 4), return_type=float)
]


class CSVNames(StrEnum):
    DATE = "date"
    DESCRIPTION = "description"
    CURRENCY = "currency"
    AMOUNT = "amount"

    @classmethod
    def to_list(cls):
        return [c.value for c in cls]
