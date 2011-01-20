# Copyright BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2

from zope.interface import implements
from zodict import Node
from zope.component import getUtility
from agx.io.xml.interfaces import IXMLFactory
from agx.io.xml import XMLNode
from agx.io.zcml.interfaces import (
    IZCMLNode,
    IZCMLFile,
    ISimpleDirective,
    IComplexDirective,
)

class ZCMLAttrs(object):
    """XXX: move this to agx.io.xml. and rename to XMLAttributes.
    """
    
    def __init__(self, model):
        object.__setattr__(self, '_model', model)
    
    @property
    def model(self):
        return object.__getattribute__(self, '_model')

    def __getitem__(self, key):
        if key.find(':') != -1:
            key = self.model._fq_name(key)
        return self.model.model.attributes[key]
    
    def __setitem__(self, name, value):
        if name.find(':') != -1:
            name = self.model._fq_name(name)
        self.model.model.attributes[name] = value
    
    def get(self, key, default=None):
        if key.find(':') != -1:
            key = self.model._fq_name(key)
        return self.model.model.attributes.get(key, default)
    
    def __contains__(self, key):
        if key.find(':') != -1:
            key = self.model._fq_name(key)
        return key in self.model.model.attributes
    
    def __getattr__(self, name):
        if name.find(':') != -1:
            name = self.model._fq_name(name)
        return self.model.model.attributes[name]
    
    def __setattr__(self, name, value):
        if name.find(':') != -1:
            name = self.model._fq_name(name)
        self.model.model.attributes[name] = value

class ZCMLNode(Node):
    implements(IZCMLNode)
    
    def __init__(self, name=None, parent=None, nsmap=None, model=None):
        Node.__init__(self, name=name)
        self.model = model
        if self.model is not None:
            self.model.format = 1
            if nsmap is None:
                self.nsmap = self.model.element.nsmap
        elif parent is not None:
            self.nsmap = parent.model.element.nsmap
            parent[self.uuid] = self
        elif nsmap is not None:
            self.nsmap = nsmap
        else:
            self.nsmap = {
                None: 'http://namespaces.zope.org/zope',
            }
    
    def __setitem__(self, key, value):
        if not IZCMLNode.providedBy(value):
            raise ValueError(u"Invalid value %s" % value)
        if value.nsmap is None:
            value.nsmap = self.nsmap
        if value.model is None:
            if value.__name__ is None:
                raise ValueError(u"Cannot create model. no name given" % value)
            ns = None
            if value.__name__.find(':') != -1:
                ns, name = value.__name__.split(':')
            else:
                name = value.__name__
            value.model = XMLNode(name, ns=value.nsmap[ns], nsmap=value.nsmap)
            #value.model.element.nsmap = self.nsmap
            self.model[value.uuid] = value.model
        Node.__setitem__(self, key, value)
    
    def __delitem__(self, key):
        todelete = self[key]
        self.model.element.remove(todelete.model.element)
        Node.__delitem__(self, key)
    
    @property
    def attrs(self):
        return ZCMLAttrs(self)
    
    def filter(self, interface=None, tag=None, attr=None, value=None):
        if interface is not None:
            items = [item for item in self.filtereditems(interface)]
        else:
            items = self.values()
        filtered = list()
        if tag is not None:
            tag = self._fq_name(tag)
            for item in items:
                if item.model.element.tag == tag:
                    filtered.append(item)
        if attr is not None:
            for item in items:
                if item.attrs.get(attr) is not None:
                    filtered.remove(item)
        if value is not None:
            for item in items:
                if item.attrs.get(attr) is not None:
                    if not item.attrs.get(attr) == value:
                        filtered.remove(item)
        return filtered
    
    def _buildchildren(self, node):
        for child in node.model.values():
            if child.values():
                complex = ComplexDirective(model=child)
                node[complex.uuid] = complex
                node._buildchildren(complex)
            else:
                simple = SimpleDirective(model=child)
                node[simple.uuid] = simple
    
    def _fq_name(self, name):
        if name.find(':') != -1:
            ns, attr = name.split(':')
            return '{%s}%s' % (self.nsmap[ns], attr)
        return '{%s}%s' % (self.nsmap[None], name)

class ZCMLFile(ZCMLNode):
    implements(IZCMLFile)
    
    def __init__(self, path, nsmap=None):
        ZCMLNode.__init__(self, nsmap=nsmap)
        self.outpath = path
        try:
            factory = getUtility(IXMLFactory)
            model = factory(path)
            self.model = model.values()[0]
            self.nsmap = self.model.element.nsmap
            self._buildchildren(self)
        except IOError, e:
            self.model = XMLNode('configure', path=path,
                                 ns=self.nsmap[None], nsmap=self.nsmap)
    
    def __call__(self):
        self.model.root.outpath = self.outpath
        self.model.root.format = 1
        self.model.root()

class SimpleDirective(ZCMLNode):
    implements(ISimpleDirective)
    
    def __setitem__(self, key, value):
        raise NotImplementedError(u"Cannot add children to SimpleDirective.")

class ComplexDirective(ZCMLNode):
    implements(IComplexDirective)