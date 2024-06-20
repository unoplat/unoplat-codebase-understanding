from typing import List, Optional

from pydantic import BaseModel, Field
from data_models.chapi_unoplat_annotation import Annotation
from data_models.chapi_unoplat_class_fieldmodel import ClassFieldModel, FieldModel
from data_models.chapi_unoplat_function import Function
from data_models.chapi_unoplat_import import Import
from data_models.chapi_unoplat_node import Node
from data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset


class DspyUnoplatNodeSubset(BaseModel):
    node_name: Optional[str] = Field(default=None, alias="NodeName",description="This is name of the class.")
    multiple_extend: Optional[bool] = Field(default=None, alias="MultipleExtend",description="this includes if class is inheriting multiple classes")
    fields: List[ClassFieldModel] = Field(default_factory=list, alias="Fields",description="This includes class fields")
    extend: Optional[str] = Field(default=None, alias="Extend",description="This includes class inheritance")
    imports: List[Import] = Field(default_factory=list, alias="Imports",description="This includes class imports which can be used to infer types of fields")
    annotations: List[DspyUnoplatAnnotationSubset] = Field(default_factory=list, alias="Annotations")