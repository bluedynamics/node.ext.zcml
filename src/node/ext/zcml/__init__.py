from node.ext import directory
from _api import (
    ZCMLNode,
    ZCMLFile,
    SimpleDirective,
    ComplexDirective,
)

directory.file_factories['.zcml'] = ZCMLFile