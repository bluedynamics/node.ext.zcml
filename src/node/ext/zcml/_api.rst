node.ext.zcml
=============

Import nodes::

    >>> from node.ext.zcml import ZCMLNode
    >>> from node.ext.zcml import ZCMLFile
    >>> from node.ext.zcml import SimpleDirective
    >>> from node.ext.zcml import ComplexDirective

Testdata directory::

    >>> datadir
    '.../node.ext.zcml/src/node/ext/zcml/testing/data'


Parse ZCML file
---------------

Read existing zcml file::

    >>> import os
    >>> existingpath = os.path.join(datadir, 'configure.zcml')
    >>> existingpath
    '.../node.ext.zcml/src/node/ext/zcml/testing/data/configure.zcml'

    >>> zcml = ZCMLFile(path=existingpath)

Check NSMAP::

    >>> sorted(zcml.nsmap.items())
    [(None, 'http://namespaces.zope.org/zope'), 
    ('browser', 'http://namespaces.zope.org/browser'), 
    ('cmf', 'http://namespaces.zope.org/cmf'), 
    ('five', 'http://namespaces.zope.org/five'), 
    ('zcml', 'http://namespaces.zope.org/zcml')]

Check parsed Tree::

    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: None
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.ComplexDirective'>: ...
        <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...


Query ZCML nodes
----------------

Check ``filter`` function::

    >>> zcml.filter()
    []

Filter by tag name::

    >>> zcml.filter(tag='browser:page')
    [<SimpleDirective object '...' at ...>]

    >>> zcml.filter(tag='include')
    [<SimpleDirective object '...' at ...>, 
    <SimpleDirective object '...' at ...>]

Filter by tag name and attribute name::

    >>> zcml.filter(tag='include', attr='file')
    [<SimpleDirective object '...' at ...>]

Filter by tagname, attribute name and attribute value::

    >>> zcml.filter(tag='include', attr='file', value='inexistent')
    []

    >>> zcml.filter(tag='include', attr='file', value='foo.zcml')
    [<SimpleDirective object '...' at ...>]

    >>> zcml.filter(tag='browser:page', attr='name', value='foo')
    [<SimpleDirective object '...' at ...>]

Filter function does not work recusrive::

    >>> zcml.filter(tag='class')
    [<ComplexDirective object '...' at ...>]

    >>> zcml.filter(tag='implements')
    []

    >>> zcml.filter(tag='class')[0].filter(tag='implements')
    [<SimpleDirective object '...' at ...>]

Filter adapter, check multivalued attribute::

    >>> adapter = zcml.filter(tag='adapter')[0]
    >>> adapter.attrs['for']
    ['.interfaces.IIface1', '.interfaces.IIface2', '.interfaces.IIface3']


Write ZCML file
---------------

Change outpath of already parsed ZCML and dump. Outpath defaults to given
path at __init__ time::

    >>> zcml.__name__ = os.path.join(datadir, 'dumped.configure.zcml')
    >>> zcml()
    >>> with open(zcml.name, 'r') as file:
    ...     lines = file.readlines()
    >>> lines
    ['<?xml version="1.0" encoding="UTF-8"?>\n', 
    '<configure\n', 
    '    xmlns="http://namespaces.zope.org/zope"\n', 
    '    xmlns:zcml="http://namespaces.zope.org/zcml"\n', 
    '    xmlns:browser="http://namespaces.zope.org/browser"\n', 
    '    xmlns:five="http://namespaces.zope.org/five"\n', 
    '    xmlns:cmf="http://namespaces.zope.org/cmf"\n', 
    '    i18n_domain="agx.example">\n', 
    '\n', 
    '    <include package="foo.bar"/>\n', 
    '\n', 
    '    <include file="foo.zcml"/>\n', 
    '\n', 
    '    <utility factory=".foo.Bar"/>\n', 
    '\n', 
    '    <browser:page\n', 
    '        for="*"\n', 
    '        name="foo"\n', 
    '        class=".foo.Baz"\n', 
    '        template="foo.pt"\n', 
    '        permission="zope.Public"/>\n', 
    '\n', 
    '    <class class=".foo.Baz">\n', 
    '\n', 
    '        <implements interface=".interfaces.IBaz"/>\n', 
    '\n', 
    '    </class>\n', 
    '\n', 
    '    <adapter\n', 
    '        for=".interfaces.IIface1 .interfaces.IIface2 .interfaces.IIface3"\n', 
    '        factory=".a.B"\n', 
    '        provides=".interfaces.IFace4"/>\n', 
    '\n', 
    '</configure>']


Create ZCML file
----------------

Path for our new file::

    >>> outpath = os.path.join(datadir, 'new.zcml')

Delete outfile if present due to prior test run::

    >>> try:
    ...     os.remove(outpath)
    ... except OSError, e:
    ...     pass

NSMAP to use. Note that you can only define namspaces due to File creation::

    >>> nsmap = {
    ...     None: 'http://namespaces.zope.org/zope',
    ...     'browser': 'http://namespaces.zope.org/browser',
    ... }

Create new ZCML::

    >>> zcml = ZCMLFile(name=outpath, path=outpath, nsmap=nsmap)
    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: /...

Only accepts IZCMLNode implementations::

    >>> zcml['foo'] = object()
    Traceback (most recent call last):
      ...
    ValueError: Invalid value <object object at ...>

Add simple directives::

    >>> simple = SimpleDirective(name='utility', parent=zcml)
    >>> simple.attrs['factory'] = 'foo.Bar'

    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: /...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...

    >>> zcml()
    >>> with open(zcml.name, 'r') as file:
    ...     lines = file.readlines()
    >>> lines
    ['<?xml version="1.0" encoding="UTF-8"?>\n', 
    '<configure\n', 
    '    xmlns:browser="http://namespaces.zope.org/browser"\n', 
    '    xmlns="http://namespaces.zope.org/zope">\n', 
    '\n', 
    '  <utility factory="foo.Bar"/>\n', 
    '\n', 
    '</configure>']

    >>> simple = SimpleDirective(name='browser:page', parent=zcml)
    >>> simple.attrs['for'] = ['.Iface1', '.Iface2']
    >>> simple.attrs['name'] = 'somename'
    >>> simple.attrs['template'] = 'somename.pt'
    >>> simple.attrs['permission'] = 'zope.Public'

    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: /...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...

Add complex directive::

    >>> complex = ComplexDirective(name='class', parent=zcml)
    >>> complex.attrs['class'] = '.foo.Bar'
    >>> sub = SimpleDirective(name='implements', parent=complex)
    >>> sub.attrs['interface'] = '.interfaces.IBar'

Simple directives cannot contain children::

    >>> sub['foo'] = SimpleDirective(name='fail', parent=sub)
    Traceback (most recent call last):
      ...
    NotImplementedError: Cannot add children to SimpleDirective.

Write ZCML file and check contents::

    >>> zcml()
    >>> with open(outpath, 'r') as file:
    ...     lines = file.readlines()
    >>> lines
    ['<?xml version="1.0" encoding="UTF-8"?>\n', 
    '<configure\n', 
    '    xmlns:browser="http://namespaces.zope.org/browser"\n', 
    '    xmlns="http://namespaces.zope.org/zope">\n', 
    '\n', 
    '  <utility factory="foo.Bar"/>\n', 
    '\n', 
    '  <browser:page\n', 
    '      for=".Iface1 .Iface2"\n', 
    '      name="somename"\n', 
    '      template="somename.pt"\n', 
    '      permission="zope.Public"/>\n', 
    '\n', 
    '  <class class=".foo.Bar">\n', 
    '\n', 
    '    <implements interface=".interfaces.IBar"/>\n', 
    '\n', 
    '  </class>\n', 
    '\n', 
    '</configure>']


Modify ZCML file
----------------

Use already created ZCML file to modify.

Add another ZCML node::

    >>> simple = SimpleDirective(name='adapter', parent=zcml)
    >>> simple.attrs['for'] = 'interfaces.IBar'
    >>> simple.attrs['name'] = 'myadapter'
    >>> simple.attrs['factory'] = '.foobar.FooBarAdapter'

    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: /...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.ComplexDirective'>: ...
        <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...

    >>> toremove = zcml.filter(tag='utility')[0]
    >>> toremove.uuid in zcml.keys()
    True

    >>> del zcml[toremove.uuid]

    >>> zcml.__name__ = os.path.join(datadir, 'modified.zcml')
    >>> zcml()

    >>> os.path.exists(zcml.name)
    True

    >>> with open(zcml.name, 'r') as file:
    ...     lines = file.readlines()
    >>> lines
    ['<?xml version="1.0" encoding="UTF-8"?>\n', 
    '<configure\n', 
    '    xmlns:browser="http://namespaces.zope.org/browser"\n', 
    '    xmlns="http://namespaces.zope.org/zope">\n', 
    '\n', 
    '  <browser:page\n', 
    '      for=".Iface1 .Iface2"\n', 
    '      name="somename"\n', 
    '      template="somename.pt"\n', 
    '      permission="zope.Public"/>\n', 
    '\n', 
    '  <class class=".foo.Bar">\n', 
    '\n', 
    '    <implements interface=".interfaces.IBar"/>\n', 
    '\n', 
    '  </class>\n', 
    '\n', 
    '  <adapter\n', 
    '      for="interfaces.IBar"\n', 
    '      name="myadapter"\n', 
    '      factory=".foobar.FooBarAdapter"/>\n', 
    '\n', 
    '</configure>']


Test helper function::

    >>> from node.ext.zcml._api import split_line_by_attributes
    >>> line = '<tagname foo="a b c d e" bar="baz" />'
    >>> split_line_by_attributes(line)
    ['<tagname', 'foo="a b c d e"', 'bar="baz"/>']
