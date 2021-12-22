# -*- coding: utf8 -*-

import json
from PyQt5 import QtCore
from ..misc import xray_util as xu

dos_greek = {'a': 'α', 'b': 'β', 'g': 'γ'}


def utfize(text):
    """replace the a,b,g ascii letters used by retards traped in the ms-dos age
    to the proper utf8 greek α, β, γ
    """
    return ''.join(dos_greek[s] if s in dos_greek else s for s in text)


class SimpleDictNode(object):
    """Helper class to construct model from
    and save models data back to pythons dict form.
    To construct the Node Tree use 'node_builder' static method
    """
    
    def __init__(self, name=None, parent=None, state=None):
        
        self._children = []
        self._parent = parent
        self.name = name       # str
        self.state = state     # bool
        
        if parent is not None:
            parent.addChild(self)


    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None
        return True

# this is not java, no need for not needed encapsulation....
#    def name(self):
#        return self._name
#    
#    def state(self):
#        return self._state
#    
#    def setState(self, state):
#        self.state = state
#        self.set_all_children(state)
#               
    #def checkState(self):
    #    if self.childCount() > 0:
    #        states = [i.checkState() for i in self._children]
    #        if ('partially' in states) or (any(states) and not all(states)):
    #            self.state = 'partially'
    #            return 'partially' 
    #        elif all(states):
    #            self.state = True
    #            return True
    #        else:
    #            self.state = False
    #            return False
    #    else:
    #        return self.state
        
    #def set_all_children(self, state):             # IT was design mistake
    #    if self.childCount() > 0:
    #        for i in self._children:
    #            i.state = state
    #            i.set_all_children(state)

    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)
    
    def parent(self):
        return self._parent
    
    def get_tree_path(self):
        if self._parent is None:
            return self.name
        return ' '.join([self._parent.get_tree_path(),
                         self.name])
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=True)
    
    def to_dict(self):
        def _dict(node):
            if node.childCount() == 0:  # the line node
                return {node.name: node.state}
            else:                # the line family and element
                output = {node.name: {} }
                for n in node._children:
                    output[node.name].update(_dict(n))
                return output
        return _dict(self)
    
    @staticmethod
    def node_builder(dictionary, name='root'):
        root = SimpleDictNode(name)
        def _builder(dict2, parent=None):
            for key in dict2:
                if type(dict2[key]) == dict:
                    leaf = SimpleDictNode(key, parent)
                    _builder(dict2[key], parent=leaf)
                else:
                    SimpleDictNode(key, parent, dict2[key])
        _builder(dictionary, root)
        #root.checkState()
        return root
    

class ElementLineTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super().__init__(parent)
        self._rootNode = root
        self.edx = None
    
    def coupleToEDX(self, eds):
        self.edx = eds
        
    def decouple(self):
        self.edx = None
    
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        return 3
    
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if index.column() == 0:
            if role == QtCore.Qt.DisplayRole:
                return utfize(node.name)
        
            if role == QtCore.Qt.CheckStateRole:
                if node.state == True:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        elif (index.column() == 1) and (role == QtCore.Qt.DisplayRole):
            if node.childCount() == 0:
                return xu.xray_energy(node._parent._parent.name, node.name)
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        elif (index.column() == 0) and (role == QtCore.Qt.CheckStateRole):
            node = index.internalPointer()
            if value == QtCore.Qt.Checked:
                 node.state = True
            else:
                 node.state = False
            self.dataChanged.emit(index, index)
            return True

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Element lines"
            elif section == 1:
                return "energy [kV]"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

