from dataclasses import dataclass
from typing import Optional

from graphql import print_schema

from apischema import type_name
from apischema.graphql import graphql_schema


@type_name("Foo")
@dataclass
class FooFoo:
    bar: int


def foo() -> Optional[FooFoo]:
    ...


schema = graphql_schema(query=[foo])
schema_str = """\
type Query {
  foo: Foo
}

type Foo {
  bar: Int!
}
"""
assert print_schema(schema) == schema_str
