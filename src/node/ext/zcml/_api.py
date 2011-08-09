from lxml import etree
from plumber import plumber
from zope.interface import implements
from node.interfaces import IRoot
from node.parts import (
    Reference,
    Order,
)
from node.base import OrderedNode
from zope.component import getUtility
from node.ext.xml.interfaces import IXMLFactory
from node.ext.xml import XMLNode
from node.ext.zcml.interfaces import (
    IZCMLNode,
    IZCMLFile,
    ISimpleDirective,
    IComplexDirective,
)

class ZCMLAttrs(object):
    """XXX: move this to node.ext.xml. and rename to XMLAttributes.
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
        """XXX: Remove, no attribute access for attributes.
        """
        if name.find(':') != -1:
            name = self.model._fq_name(name)
        return self.model.model.attributes[name]
    
    def __setattr__(self, name, value):
        """XXX: Remove, no attribute access for attributes.
        """
        if name.find(':') != -1:
            name = self.model._fq_name(name)
        self.model.model.attributes[name] = value


class ZCMLNode(OrderedNode):
    __metaclass__  = plumber
    __plumbing__ = Reference, Order
    
    implements(IZCMLNode)
    
    def __init__(self, name=None, parent=None, nsmap=None, model=None):
        OrderedNode.__init__(self, name=name)
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
        OrderedNode.__setitem__(self, key, value)
    
    def __delitem__(self, key):
        todelete = self[key]
        self.model.element.remove(todelete.model.element)
        OrderedNode.__delitem__(self, key)
    
    @property
    def attrs(self):
        return ZCMLAttrs(self)
    
    def filter(self, interface=None, tag=None, attr=None, value=None):
        filtered = list()
        if interface is None \
          and tag is None \
          and attr is None \
          and value is None:
            return filtered
        if interface is not None:
            items = [item for item in self.filtereditems(interface)]
        else:
            items = self.values()
        if tag is not None:
            tag = self._fq_name(tag)
        for item in items:
            if tag is not None:
                if item.model.element.tag != tag:
                    continue
            if attr is not None:
                if item.attrs.get(attr) is None:
                    continue
            if value is not None:
                if item.attrs.get(attr) != value:
                    continue
            filtered.append(item)
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
        model = self.model.root
        with open(model.outpath, "wb") as file:
            file.write("<?xml version=\"1.0\" encoding=\"%s\"?>\n" % 'UTF-8')
            formatted = ZCMLFormatter().format(
                etree.tostring(model.element, pretty_print=True))
            file.write(formatted)


class SimpleDirective(ZCMLNode):
    implements(ISimpleDirective)
    
    def __setitem__(self, key, value):
        raise NotImplementedError(u"Cannot add children to SimpleDirective.")


class ComplexDirective(ZCMLNode):
    implements(IComplexDirective)


class ZCMLFormatter(object):
    
    def lineindent(self, line):
        indent = 0
        while True:
            if line[indent] != u' ':
                break
            indent += 1
        return indent
    
    def format(self, xml):
        """Format already prettyprinted XML output for better human readability
        """
        formatted_lines = list()
        lines = xml.split('\n')
        for line in lines:
            # continue if blank line
            if not line.strip():
                continue
            # replace each tab with 4 spaces
            line = line.rstrip().replace('\t', '    ')
            if line.find(' ') > -1:
                indent = self.lineindent(line)
                # if line exceeds 80 chars, split up line by attributes, and
                # align them below each other.
                if len(line) > 80:
                    sublines = line.strip().split(' ') # XXX
                    formatted_lines.append(indent * ' ' + sublines[0])
                    for subline in sublines[1:]:
                        formatted_lines.append((indent + 4) * ' ' + subline)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        ret_lines = list()
        # add new blank lines
        for line in formatted_lines:
            if line.strip().startswith('<'):
                ret_lines.append('')
            ret_lines.append(line)
        ret = '\n'.join(ret_lines)
        return ret.strip('\n')