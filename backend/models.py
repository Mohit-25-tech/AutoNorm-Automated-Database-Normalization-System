from pydantic import BaseModel
from typing import List, Optional

class FunctionalDependency(BaseModel):
    lhs: List[str]
    rhs: List[str]

class NormalizationRequest(BaseModel):
    attributes: List[str]
    functional_dependencies: List[FunctionalDependency]
    multivalued_attributes: Optional[List[str]] = []
    has_repeating_groups: Optional[bool] = False

class ViolationItem(BaseModel):
    type: str
    fd: str
    reason: str

class OneNFViolationItem(BaseModel):
    type: str
    attribute: str
    reason: str

class TableSchema(BaseModel):
    name: str
    attributes: List[str]
    primary_key: List[str]

class NormStep(BaseModel):
    title: str
    detail: str

class NormalizationResponse(BaseModel):
    candidate_keys: List[List[str]]
    prime_attributes: List[str]
    violations_1nf: List[OneNFViolationItem]
    violations_2nf: List[ViolationItem]
    violations_3nf: List[ViolationItem]
    violations_bcnf: List[ViolationItem]
    tables_2nf: List[TableSchema]
    tables_3nf: List[TableSchema]
    tables_bcnf: List[TableSchema]
    is_1nf: bool
    is_2nf: bool
    is_3nf: bool
    is_bcnf: bool
    steps_1nf: List[NormStep]
    steps_keys: List[NormStep]
    steps_2nf: List[NormStep]
    steps_3nf: List[NormStep]
    steps_bcnf: List[NormStep]
