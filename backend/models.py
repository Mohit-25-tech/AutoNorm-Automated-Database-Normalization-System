from pydantic import BaseModel
from typing import List

class FunctionalDependency(BaseModel):
    lhs: List[str]
    rhs: List[str]

class NormalizationRequest(BaseModel):
    attributes: List[str]
    functional_dependencies: List[FunctionalDependency]

class ViolationItem(BaseModel):
    type: str
    fd: str
    reason: str

class TableSchema(BaseModel):
    name: str
    attributes: List[str]
    primary_key: List[str]

class NormalizationResponse(BaseModel):
    candidate_keys: List[List[str]]
    prime_attributes: List[str]
    violations_2nf: List[ViolationItem]
    violations_3nf: List[ViolationItem]
    violations_bcnf: List[ViolationItem]
    tables_2nf: List[TableSchema]
    tables_3nf: List[TableSchema]
    tables_bcnf: List[TableSchema]
    is_2nf: bool
    is_3nf: bool
    is_bcnf: bool