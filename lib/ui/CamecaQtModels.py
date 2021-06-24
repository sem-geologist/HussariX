from PyQt5.QtCore import (QAbstractItemModel,
                          QAbstractListModel,
                          QModelIndex,
                          Qt)
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QWidgetAction, QMenu, QLabel
from colorcet import glasbey_light, glasbey_dark
from .spectral_curve import SpectralCurveItem
from ..parsers.cameca import CamecaWDS, Cameca, CamecaBase

# note: in some cameca software versions it is user customisable
cam_def_colors = {'PC0': QColor(182, 255, 182),
                  'PC1': QColor(255, 255, 192),
                  'PC2': QColor(255, 224, 192),
                  'PC3': QColor(255, 192, 192),
                  'PET': QColor(192, 192, 255),
                  'TAP': QColor(175, 255, 255),
                  'LIF': QColor(255, 192, 255),
                  'QTZ': QColor(128, 255, 255),
                  'etc': QColor(255, 255, 255)}


# font to use to write onto above colors (to stay dark in dark mode):
k_text_col = QColor(0, 0, 0)

glasbey_l_qcolors = [QColor(i) for i in glasbey_light * 4]
glasbey_d_qcolors = [QColor(i) for i in glasbey_dark * 4]
# make it 4 x 254, so that there would be enought of colors


def menu_linestyle_entry_generator(pen_style=Qt.SolidLine, width=2,
                                   parent=None):
    wa = QWidgetAction(parent)
    label = QLabel(parent)
    pix = QPixmap(74, 24)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    pen = QPen(QColor(255, 178, 75), width,
               pen_style)
    painter.setPen(pen)
    painter.drawLine(0, 12, 74, 12)
    painter.end()
    label.setPixmap(pix)
    wa.setDefaultWidget(label)
    wa.pen = pen  # this attribute will hold the style
    return wa


# Construct the line style menu, which will be reused.


line_pattern_menu = QMenu("line pattern")
for i in [Qt.SolidLine, Qt.DotLine, Qt.DashLine, Qt.DashDotLine,
          Qt.DashDotDotLine]:
    line_pattern_menu.addAction(
        menu_linestyle_entry_generator(pen_style=i, parent=line_pattern_menu))
    line_pattern_menu.addSeparator()
line_width_menu = QMenu("line width")
for j in [1, 2, 3, 4, 5]:
    line_width_menu.addAction(
        menu_linestyle_entry_generator(width=j, parent=line_width_menu))
    line_width_menu.addSeparator()

line_style_menu = QMenu()
line_style_menu.addMenu(line_pattern_menu)
line_style_menu.addMenu(line_width_menu)


class WDSPlotItem(SpectralCurveItem):
    def __init__(self, dataset_item, canvas_widget=None):
        SpectralCurveItem.__init__(self)
        self.canvas_widget = canvas_widget
        self.signal = dataset_item.signal
        self.signal_header = dataset_item.signal_header
        self.dataset = dataset_item._parent
        dts = self.dataset
        if not hasattr(dts, 'q_custom_color'):
            dts.q_custom_color = glasbey_l_qcolors[dts.q_row] \
              if canvas_widget.dark_mode else glasbey_d_qcolors[dts.q_row]
        self.setPen(self.dataset.q_custom_color)
        self.setVisible(self.dataset.q_checked_state)
        if not hasattr(self.dataset, 'plot_items'):  # need to inject ref.
            self.dataset.plot_items = []             # for highlighting and
        self.dataset.plot_items.append(self)         # visib. change signaling
        self.set_spectral_data()

    def set_spectral_data(self, x_mode=None, y_mode=None):
        if x_mode is None:
            x_mode = self.canvas_widget.x_axis_mode
        if x_mode == 'cameca':
            x = self.signal.x_100k_sin_theta
        elif x_mode == 'energy':
            x = self.signal.x_keV
        elif x_mode == 'wavelenth':
            x = self.signal.x_nm
        if y_mode is None:
            y_mode = self.canvas_widget.y_axis_mode
        if y_mode == 'cps':
            y = self.signal.y_cps
        elif y_mode == 'cts':
            y = self.signal.y_cts
        elif y_mode == 'cpsna':
            y = self.signal.y_cps_per_nA
        self.setData(x=x, y=y)


# class QtiSpectrometerSetupModel(QAbstractTableModel):
#    def __init__(self, parent=None):
#        super().__init__(parent)


class DummyCamecaWDS(CamecaWDS):
    def __init__(self):
        self.file_basename = 'calculated'
        self.q_children = []
        self.q_check_state = 0

    def append_dataset(self, dataset):
        dataset.q_parent = self
        self.q_children.append(dataset)


class SpecXTALCombiModel(QAbstractListModel):
    
    SpectXtalCombinationRole = Qt.UserRole
    LineStyleRole = Qt.UserRole + 1
    LineWidthRole = Qt.UserRole + 2
    
    def __init__(self, model, parent=None):
        QAbstractListModel.__init__(self, parent=parent)
        self.spectra_model = model
        self.combinations = []
        self.selected_xtal_family = None
        self.ignore_family_constrain = False
        if len(self.spectra_model.collection) > 0:
            self.combinations = sorted(
                set.union(*[i.spect_xtal_unique_combinations
                            for i in self.spectra_model.collection]),
                key=lambda x: x.combi_string)
        self.spectra_model.rowsInserted.connect(self.scan_and_add_entries)

    def data(self, index, role):
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return self.combinations[index.row()].combi_string
        node = self.combinations[index.row()]
        if role == Qt.DecorationRole:
            if not hasattr(node, 'q_pen_style'):
                node.q_pen_style = Qt.SolidLine
                node.q_pen_width = 1
            qpix = QPixmap(48, 4)
            qpix.fill(Qt.transparent)
            painter = QPainter(qpix)
            pen = QPen(cam_def_colors[node.xtal.family_name], 4,
                       node.q_pen_style)
            painter.setPen(pen)
            painter.drawLine(0, 1, 48, 1)
            painter.end()
            return qpix
        if role == Qt.CheckStateRole:
            if not hasattr(node, 'q_checked'):
                node.q_checked = Qt.Unchecked
            return node.q_checked
        if role == self.SpectXtalCombinationRole:
            return node
        if role == self.LineStyleRole:
            if not hasattr(node, 'q_pen_style'):
                node.q_pen_style = Qt.SolidLine
            return node.q_pen_style
        if role == self.LineWidthRole:
            if not hasattr(node, 'q_pen_width'):
                node.q_pen_width = 1
            return node.q_pen_width

    def setData(self, index, value, role):
        if not index.isValid():
            return
        node = self.combinations[index.row()]
        if role == Qt.CheckStateRole:
            node.q_checked = value
            if value == 0:
                if not any([i.q_checked for i in self.combinations]):
                    self.layoutAboutToBeChanged.emit()
                    self.selected_xtal_family = None
                    self.layoutChanged.emit()
            elif not self.ignore_family_constrain:
                if self.selected_xtal_family is None:
                    self.layoutAboutToBeChanged.emit()
                    self.selected_xtal_family = \
                        self.combinations[index.row()].xtal.family_name
                    self.layoutChanged.emit()
        if role == self.LineStyleRole:
            self.layoutAboutToBeChanged.emit()
            node.q_pen_style = value
            self.layoutChanged.emit()
        if role == self.LineWidthRole:
            node.q_pen_width = value
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self.combinations)

    def scan_and_add_entries(self, *args):
        new_combinations = set.union(*[i.spect_xtal_unique_combinations
                                       for i in self.spectra_model.collection])
        diff_comb = new_combinations.difference(self.combinations)
        if len(diff_comb) > 0:
            lenght = len(diff_comb)
            start_row = len(self.combinations)
            end_row = start_row + lenght - 1
            self.beginInsertRows(QModelIndex(), start_row, end_row)
            for i in diff_comb:
                self.combinations.insert(start_row, i)
            self.endInsertRows()

    def setIgnoreFamilyConstrain(self, state):
        self.layoutAboutToBeChanged.emit()
        self.ignore_family_constrain = state
        self.layoutChanged.emit()
        if state:
            self.selected_xtal_family = None
        if not state:
            self.leave_only_single_family_selected()

    def leave_only_single_family_selected(self):
        for i, spect_header in enumerate(self.combinations):
            if spect_header.q_checked and self.selected_xtal_family is None:
                self.selected_xtal_family = spect_header.xtal.family_name
            elif spect_header.q_checked:
                if self.selected_xtal_family != spect_header.xtal.family_name:
                    self.setData(self.index(i), 0, Qt.CheckStateRole)

    def flags(self, index):
        if self.ignore_family_constrain or self.selected_xtal_family is None:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        if self.combinations[index.row()].xtal.family_name == \
                self.selected_xtal_family:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return ~Qt.ItemIsEnabled


class CamecaWDSTreeModel(QAbstractItemModel):
    """This model is simple as it is intended only for two level
    containing data.That simplifies implementation of check state
    by checking parent node (filename) of imported Wds file(s).
    This model is not universal - it hooks directly with data,
    otherwise than examples of Qt it does not use brokering
    Classes as i.e. NodeTree and similar."""
    def __init__(self, cameca_files, dark_mode=True, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self.collection = cameca_files
        self.dark_mode = dark_mode
        # this flag is used for tristate check behaviour
        # to prevent children<->parent loops:
        self.parent_selects_children_flag = False
        # That is for custom node with calculated WDS spectra
        self.last_item_is_custom = False
        self.spec_xtal_selection_model = None

    def index(self, row, column=0, parent=None):
        """reimplemented"""
        if parent is None or not parent.isValid():
            return self.createIndex(row, column, self.collection[row])

        return self.createIndex(row, column,
                                parent.internalPointer().q_children[row])

    def parent(self, index):
        """reimplemented"""
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if isinstance(node, CamecaBase):
            return QModelIndex()
        if isinstance(node, Cameca.Dataset):
            row = self.collection.index(node.q_parent)
            return self.createIndex(row, 0, node.q_parent)
        if isinstance(node, Cameca.DatasetItem):
            row = node.q_parent.q_row
            return self.createIndex(row, 0, node.q_parent)
        return QModelIndex()

    def hasChildren(self, index):
        if index == QModelIndex():
            return True
        node = index.internalPointer()
        if node is not None and node.q_row_count > 0:
            return True
        return False

    def rowCount(self, index):
        if index.isValid():
            node = index.internalPointer()
            return node.q_row_count
        return len(self.collection)

    def columnCount(self, parent):
        return 1

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and section == 0 and\
         role == Qt.DisplayRole:
            return 'WDS files / Datasets'

    def data(self, index, role):
        row = index.row()
        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if isinstance(node, CamecaBase):
                return node.file_basename
            if isinstance(node, Cameca.Dataset):
                return '{}: {}'.format(row + 1, node.comment.text)

        if role == Qt.ToolTipRole:
            if isinstance(node, Cameca.Dataset):
                return 'dt\'set {} contains:\n  '.format(row + 1) + \
                    '\n  '.join([str(i.signal_header) for i in node.items])

        if role == Qt.CheckStateRole:
            if isinstance(node, CamecaBase):
                if node.q_checked_state == 0:
                    return Qt.Unchecked
                if node.q_checked_state == node.q_row_count:
                    return Qt.Checked
                return Qt.PartiallyChecked
            if isinstance(node, Cameca.Dataset):  # , Cameca.DatasetItem)):
                return node.q_checked_state

        if role == Qt.DecorationRole:
            if isinstance(node, Cameca.Dataset):
                if not hasattr(node, 'q_custom_color'):
                    node.q_custom_color = glasbey_l_qcolors[row] \
                        if self.dark_mode else glasbey_d_qcolors[row]
                return node.q_custom_color

        if role == Qt.EditRole:
            if isinstance(node, CamecaWDS.Dataset):
                return node.comment.text

    def setData(self, index, value, role):
        row = index.row()
        parent = index.parent()

        if not index.isValid() and role in (Qt.CheckStateRole,
                                            Qt.EditRole):
            return False
        if role == Qt.CheckStateRole:
            node = index.internalPointer()
            if isinstance(node, CamecaBase):
                if value == Qt.Checked:
                    node.q_checked_state = node.q_row_count
                elif value == Qt.Unchecked:
                    node.q_checked_state = 0
                if value != Qt.PartiallyChecked:
                    self.set_all_children(index, value)
            elif isinstance(node, Cameca.Dataset):
                node.q_checked_state = value
                if not hasattr(node, 'plot_items'):
                    node.plot_items = []
                for plot_item in node.plot_items:
                    plot_item.setVisible(value)
                self.update_parent_check_state(index, value)
        if role == Qt.EditRole:
            self.collection[parent.row()].q_children[row].comment.text = value
        self.dataChanged.emit(index, index)
        return True

    def update_parent_check_state(self, index, value):
        parent = index.parent()
        if not self.parent_selects_children_flag:
            # NOTE this depends on Qt Checked = 2; unchecked = 0
            # partially_checked = 1
            parent.internalPointer().q_checked_state += (value - 1)
            if parent.internalPointer().q_checked_state in [
                    0, 1,
                    self.rowCount(parent) - 1, self.rowCount(parent)]:
                self.setData(parent, Qt.PartiallyChecked,
                             role=Qt.CheckStateRole)

    def initialize_calculated_container(self):
        parent = QModelIndex()
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
        self.beginInsertRows(QModelIndex(), start_row, end_row)
        for i in wds_files:
            self.collection.insert(start_row, i)
        self.endInsertRows()

    def set_all_children(self, index, value):
        self.parent_selects_children_flag = True
        for row in range(self.rowCount(index)):
            self.setData(self.index(row, 0, parent=index), value,
                         Qt.CheckStateRole)
        self.parent_selects_children_flag = False

    def flags(self, index):
        parent = index.parent()
        flag_union = Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        if parent.isValid():
            flag_union |= Qt.ItemIsSelectable
            if parent.data(Qt.DisplayRole) == 'calculated':
                flag_union |= Qt.ItemIsEditable
        return flag_union
