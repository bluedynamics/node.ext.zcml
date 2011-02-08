from zope.interface import (
    Interface,
    Attribute,
)
from node.interfaces import (
    INode,
    ICallableNode,
    ILeaf,
    IRoot,
)

class IZCMLNode(INode):
    
    nsmap = Attribute(u"Namespace map")
    
    def filter(interface=None, attr=None, value=None):
        """Return directives by filter
        """

class IZCMLFile(IZCMLNode, ICallableNode, IRoot):
    """Interface for a ZCML file.
    """
    
    outpath = Attribute(u"Path for dumping ZCML File")

class ISimpleDirective(IZCMLNode, ILeaf):
    """Interface for simple directive.
    """

class IComplexDirective(IZCMLNode):
    """Interface for complex directive.
    """