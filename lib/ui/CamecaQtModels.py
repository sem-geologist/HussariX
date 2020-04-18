from PyQt5 import QtCore
from ..parsers.cameca import CamecaWDS


class QtiSpectrometerSetupModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)


class DummyCamecaWDS(CamecaWDS):
    def __init__(self):
        self.file_basename = 'calculated'
        self.datasets = []
        self.check_state = 0

    def append_dataset(self, dataset):
        dataset.parent = self
        self.datasets.append(dataset)


class CamecaWDSTreeModel(QtCore.QAbstractItemModel):
    """This model is simple as it is intended only for two level
    containing data.That simplifies implementation of check state
    by checking parent node (filename) of imported Wds file(s).
    This model is not universal - it hooks directly with data,
    otherwise than examples of Qt it does not use brokering
    Classes as i.e. NodeTree and similar."""
    def __init__(self, cameca_wds, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.collection = cameca_wds
        # this flag is used for tristate check behaviour
        # to prevent loop:
        self.parent_selects_children_flag = False
        # That is for custom node with calculated WDS spectra
        self.last_item_is_custom = False

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

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return len(self.collection)
        else:
            return len(self.collection[parent.row()].datasets)

    def columnCount(self, parent):
        return 1

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and section == 0 and\
         role == QtCore.Qt.DisplayRole:
            return 'WDS files'

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

        if role == QtCore.Qt.ToolTipRole and parent.isValid():
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
        if role == QtCore.Qt.EditRole:
            return self.collection[parent.row()].datasets[row].comment

    def setData(self, index, value, role):
        row = index.row()
        parent = index.parent()

        if not index.isValid() or (role != QtCore.Qt.CheckStateRole
                                   and role != QtCore.Qt.EditRole):
            return False
        if role == QtCore.Qt.CheckStateRole:
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
                    # NOTE this depends on Qt Checked = 2; unchecked = 0
                    # partially_checked = 1
                    parent.internalPointer().check_state += (value - 1)
                    if parent.internalPointer().check_state in [
                                    0, 1, self.rowCount(parent) - 1,
                                    self.rowCount(parent)]:
                        self.setData(parent, QtCore.Qt.PartiallyChecked,
                                     role=QtCore.Qt.CheckStateRole)
        if role == QtCore.Qt.EditRole:
            self.collection[parent.row()].datasets[row].comment = value
        self.dataChanged.emit(index, index)
        return True

    def initialize_calculated_container(self):
        parent = QtCore.QModelIndex()
        self.beginInsertRows(parent, self.rowCount() + 1,
                             self.rowCount() + 1,)
        self.collection.append(DummyCamecaWDS())
        self.last_item_is_custom = True
        self.endInsertRows()

    def append_calculated_dataset(self, result):
        if not self.last_item_is_custom:
            self.initialize_calculated_container()
        parent = self.index(self.rowCount() - 1)
        self.beginInsertRows(parent, self.rowCount(parent) + 1,
                             self.rowCount(parent) + 1)
        self.collection[-1].append_dataset(result)
        self.endInsertRows()

    def append_wds_files(self, wds_files):
        lenght = len(wds_files)
        start_row = len(self.collection)
        if self.last_item_is_custom:
            start_row -= 1
        end_row = start_row + lenght - 1
        self.beginInsertRows(QtCore.QModelIndex(), start_row, end_row)
        for i in wds_files:
            self.collection.insert(start_row, i)
        self.endInsertRows()

    def set_all_children(self, index, value):
        self.parent_selects_children_flag = True
        for row in range(self.rowCount(index)):
            self.setData(self.index(row, 0, parent=index), value,
                         QtCore.Qt.CheckStateRole)
        self.parent_selects_children_flag = False

    def flags(self, index):
        parent = index.parent()
        flag_union = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
        if parent.isValid():
            flag_union |= QtCore.Qt.ItemIsSelectable
            if parent.data(QtCore.Qt.DisplayRole) == 'calculated':
                flag_union |= QtCore.Qt.ItemIsEditable
        return flag_union

    def registerGraphicalCanvas(self, canvas):
        pass

    def registerSpectralImageCanvas(self, canvas):
        pass
