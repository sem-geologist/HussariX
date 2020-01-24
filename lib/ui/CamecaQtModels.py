from PyQt5 import QtCore


class QtiSpectrometerSetupModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)


class CamecaWDSTreeModel(QtCore.QAbstractItemModel):
    """This model is simple as it is intended only for two level
    containing data, in which way check all is implemented
    by checking parent node (filename) of imported Wds file(s).
    This model is not universal - it hooks directly with data,
    otherwise than examples it does not use brokering Classes as
    NodeTree and similar."""
    def __init__(self, cameca_wds, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.collection = cameca_wds
        self.parent_selects_children_flag = False

    def index(self, row, column=0, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            _index = self.createIndex(row, 0, self.collection[row])
        else:
            _index = self.createIndex(
                row, 0, self.collection[parent.row()].datasets[row])
        return _index

    def parent(self, _index):
        node = _index.internalPointer()
        if 'datasets' in node.__dict__:
            return QtCore.QModelIndex()
        elif 'parent' in node.__dict__:
            row = self.collection.index(node.parent)
            return self.index(row, 0)

    def hasChildren(self, _index):
        if _index == QtCore.QModelIndex():
            return True
        node = _index.internalPointer()
        if 'datasets' in node.__dict__:
            return True
        elif 'parent' in node.__dict__:
            return False

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.collection)
        else:
            return len(self.collection[parent.row()].datasets)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        row = index.row()
        parent = index.parent()

        if role == QtCore.Qt.DisplayRole:
            if not parent.isValid():
                return self.collection[row].file_basename
            else:
                par_row = parent.row()
                return '{}: {}'.format(
                    row + 1,
                    self.collection[par_row].datasets[row].comment)

        if role == QtCore.Qt.CheckStateRole:
            if not parent.isValid():
                if self.collection[row].check_state == 0:
                    return QtCore.Qt.Unchecked
                elif self.collection[row].check_state == self.rowCount(index):
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.PartiallyChecked
                return self.collection[row].check_state
            else:
                par_row = parent.row()
                return self.collection[par_row].datasets[index.row()].enabled

    def setData(self, index, value, role):
        row = index.row()
        parent = index.parent()

        if not index.isValid() or role != QtCore.Qt.CheckStateRole:
            return False
        if not parent.isValid():
            if value == QtCore.Qt.Checked:
                self.collection[row].check_state = self.rowCount(index)
            elif value == QtCore.Qt.Unchecked:
                self.collection[row].check_state = 0
            if value != QtCore.Qt.PartiallyChecked:
                self.set_all_children(index, value)
        else:
            self.collection[parent.row()].datasets[row].enabled = value
            if not self.parent_selects_children_flag:
                # NOTE this depends on Checked = 2 uncchecked = 0
                parent.internalPointer().check_state += (value - 1)
                if parent.internalPointer().check_state in [
                                    0, 1, self.rowCount(parent) - 1,
                                    self.rowCount(parent)]:
                    self.setData(parent, QtCore.Qt.PartiallyChecked,
                                 role=QtCore.Qt.CheckStateRole)
        self.dataChanged.emit(index, index)
        return True

    def set_all_children(self, index, value):
        self.parent_selects_children_flag = True
        for row in range(self.rowCount(index)):
            self.setData(self.index(row, 0, parent=index), value,
                         QtCore.Qt.CheckStateRole)
        self.parent_selects_children_flag = False

    def flags(self, index):
        parent = index.parent()
        if not parent.isValid():
            # not sure if autotristate is needed here
            # as there is custom implementation
            return QtCore.Qt.ItemIsEnabled | \
                   QtCore.Qt.ItemIsAutoTristate | \
                   QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | \
                   QtCore.Qt.ItemIsUserCheckable | \
                   QtCore.Qt.ItemIsSelectable
