node.ext.zcml
=============

Import nodes.::

    >>> from node.ext.zcml import ZCMLNode
    >>> from node.ext.zcml import ZCMLFile
    >>> from node.ext.zcml import SimpleDirective
    >>> from node.ext.zcml import ComplexDirective

Testdata directory.::

    >>> datadir
    '.../node.ext.zcml/src/node/ext/zcml/tests/data'


Parse ZCML file
---------------

Read existing zcml file.::

    >>> import os
    >>> existingpath = os.path.join(datadir, 'configure.zcml')
    >>> existingpath
    '.../node.ext.zcml/src/node/ext/zcml/tests/data/configure.zcml'
    
    >>> zcml = ZCMLFile(existingpath)

Check NSMAP.::

    >>> zcml.nsmap
    {None: 'http://namespaces.zope.org/zope', 
    'cmf': 'http://namespaces.zope.org/cmf', 
    'five': 'http://namespaces.zope.org/five', 
    'zcml': 'http://namespaces.zope.org/zcml', 
    'browser': 'http://namespaces.zope.org/browser'}

Check parsed Tree.::

    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: None
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.ComplexDirective'>: ...
        <class 'node.ext.zcml._api.SimpleDirective'>: ...


Query ZCML nodes
----------------

Check ``filter`` function.::

    >>> zcml.filter()
    []

Filter by tag name.::

    >>> zcml.filter(tag='browser:page')
    [<SimpleDirective object '...' at ...>]
    
    >>> zcml.filter(tag='include')
    [<SimpleDirective object '...' at ...>, 
    <SimpleDirective object '...' at ...>]

Filter by tag name and attribute name.::

    >>> zcml.filter(tag='include', attr='file')
    [<SimpleDirective object '...' at ...>]

Filter by tagname, attribute name and attribute value.::

    >>> zcml.filter(tag='include', attr='file', value='inexistent')
    []
    
    >>> zcml.filter(tag='include', attr='file', value='foo.zcml')
    [<SimpleDirective object '...' at ...>]
    
    >>> zcml.filter(tag='browser:page', attr='name', value='foo')
    [<SimpleDirective object '...' at ...>]

Filter function does not work recusrive.::

    >>> zcml.filter(tag='class')
    [<ComplexDirective object '...' at ...>]
    
    >>> zcml.filter(tag='implements')
    []
    
    >>> zcml.filter(tag='class')[0].filter(tag='implements')
    [<SimpleDirective object '...' at ...>]


Write ZCML file
---------------

Change outpath of already parsed ZCML and dump. Outpath defaults to given
path at __init__ time.::

    >>> zcml.outpath = os.path.join(datadir, 'dumped.configure.zcml')
    >>> zcml()
    >>> file = open(zcml.outpath)
    >>> lines = file.readlines()
    >>> file.close()
    
    >> lines
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
    '        <implements interface=".interfaces.IBaz"/>\n', 
    '    </class>\n', 
    '\n', 
    '</configure>']


Create ZCML file
----------------

Path for our new file.::

    >>> outpath = os.path.join(datadir, 'new.zcml')

Delete outfile if present due to prior test run.::

    >>> try:
    ...     os.remove(outpath)
    ... except OSError, e:
    ...     pass

NSMAP to use. Note that you can only define namspaces due to File creation.::

    >>> nsmap = {
    ...     None: 'http://namespaces.zope.org/zope',
    ...     'browser': 'http://namespaces.zope.org/browser',
    ... }

Create new ZCML.::

    >>> zcml = ZCMLFile(outpath, nsmap=nsmap)
    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: None

Only accepts IZCMLNode implementations.::

    >>> zcml['foo'] = object()
    Traceback (most recent call last):
      ...
    ValueError: Invalid value <object object at ...>

Add simple directives.::

    >>> simple = SimpleDirective(name='utility', parent=zcml)
    >>> simple.attrs['factory'] = 'foo.Bar'
    
    >>> simple = SimpleDirective(name='browser:page', parent=zcml)
    >>> simple.attrs['for'] = '*'
    >>> simple.attrs['name'] = 'somename'
    >>> simple.attrs['template'] = 'somename.pt'
    >>> simple.attrs['permission'] = 'zope.Public'
    
    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: None
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...

Add complex directive.::
    
    >>> complex = ComplexDirective(name='class', parent=zcml)
    >>> complex.attrs['class'] = '.foo.Bar'
    >>> sub = SimpleDirective(name='implements', parent=complex)
    >>> sub.attrs['interface'] = '.interfaces.IBar'

Simple directives cannot contain children.::

    >>> sub['foo'] = SimpleDirective(name='fail', parent=sub)
    Traceback (most recent call last):
      ...
    NotImplementedError: Cannot add children to SimpleDirective.

Write ZCML file and check contents.::

    >>> zcml()
    >>> file = open(outpath, 'r')
    >>> lines = file.readlines()
    >>> file.close()
    
    >> lines
    ['<?xml version="1.0" encoding="UTF-8"?>\n', 
    '<configure\n', 
    '    xmlns:browser="http://namespaces.zope.org/browser"\n', 
    '    xmlns="http://namespaces.zope.org/zope">\n', 
    '  <utility factory="foo.Bar"/>\n', 
    '  <browser:page\n', 
    '      for="*"\n', 
    '      name="somename"\n', 
    '      template="somename.pt"\n', 
    '      permission="zope.Public"/>\n', 
    '  <class class=".foo.Bar">\n', 
    '    <implements interface=".interfaces.IBar"/>\n', 
    '  </class>\n', 
    '</configure>']


Modify ZCML file
----------------

Use already created ZCML file to modify.

Add another ZCML node.::

    >>> simple = SimpleDirective(name='adapter', parent=zcml)
    >>> simple.attrs['for'] = 'interfaces.IBar'
    >>> simple.attrs['name'] = 'myadapter'
    >>> simple.attrs['factory'] = '.foobar.FooBarAdapter'
    
    >>> zcml.printtree()
    <class 'node.ext.zcml._api.ZCMLFile'>: None
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.ComplexDirective'>: ...
        <class 'node.ext.zcml._api.SimpleDirective'>: ...
      <class 'node.ext.zcml._api.SimpleDirective'>: ...
    
    >>> toremove = zcml.filter(tag='utility')[0]
    >>> del zcml[toremove.uuid]
    
    >>> zcml.outpath = os.path.join(datadir, 'modified.zcml')
    >>> zcml()