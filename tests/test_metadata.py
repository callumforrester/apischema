from dataclasses import dataclass, field
from typing import Generic, TypeVar

from apischema import deserialize
from apischema.metadata import flattened

T = TypeVar("T")


@dataclass
class A(Generic[T]):
    pass


@dataclass
class B(Generic[T]):
    a1: A = field(metadata=flattened)
    a2: A[T] = field(metadata=flattened)
    a3: A[int] = field(metadata=flattened)


def test_flattened_generic_dataclass():
    deserialize(B, {})  # it works
