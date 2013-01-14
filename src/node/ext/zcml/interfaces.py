from zope.interface import (
    Interface,
    Attribute,
)
from node.interfaces import (
    INode,
    ICallable,
    ILeaf,
    IRoot,
)
from node.ext.directory.interfaces import IFile


class IZCMLNode(INode):
    """Interface for ZCML nodes.
    """
    nsmap = Attribute(u"Namespace map")

    def filter(interface=None, attr=None, value=None):
        """Return directives by filter.

        interface
            Interface to be searched
        attr
            Attribute name to be searched
        value
            Attribute value to be searched
        """


class IZCMLFile(IZCMLNode, ICallable, IRoot, IFile):
    """Interface for a ZCML file.
    """
    outpath = Attribute(u"Path for dumping ZCML File")


class ISimpleDirective(IZCMLNode, ILeaf):
    """Interface for simple directive.
    """


class IComplexDirective(IZCMLNode):
    """Interface for complex directive.
    """
