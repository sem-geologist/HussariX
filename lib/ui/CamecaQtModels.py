from datetime import datetime
from PyQt5.QtCore import (QAbstractItemModel,
                          QAbstractListModel,
                          QModelIndex,
                          Qt)
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen
from PyQt5.QtCore import pyqtSignal as Signal
# from colorcet import glasbey_light, glasbey_dark
from .spectrum_curve import SpectrumCurveItem
from ..parsers.cameca import CamecaWDS, Cameca, CamecaBase
from ..misc.glasbey_colors import glasbey_light, glasbey_dark

# note: in some cameca software versions it is user customisable
cam_def_colors = {'PC0': QColor(182, 255, 182),
                  'PC1': QColor(255, 255, 192),
                  'PC2': QColor(255, 224, 192),
                  'PC3': QColor(255, 192, 192),
                  'PET': QColor(192, 192, 255),
                  'TAP': QColor(175, 255, 255),
                  'LIF': QColor(255, 192, 255),
                  'QTZ': QColor(128, 255, 255),
                  'EDX': QColor(255, 255, 255),
                  'etc': QColor(255, 255, 255)}


# font to use to write onto above colors (to stay dark in dark mode):
k_text_col = QColor(0, 0, 0)

glasbey_l_qcolors = glasbey_light * 4
glasbey_d_qcolors = glasbey_dark * 4
# make it 4 x 254, so that there would be enought of colors


class WDSPlotItem(SpectrumCurveItem):
    def __init__(self, dataset_item, canvas_widget=None,
                 pen_style=1, pen_width=1, alpha=200):
        SpectrumCurveItem.__init__(self)
        self.canvas_widget = canvas_widget
        self.signal = dataset_item.signal
        self.signal_header = dataset_item.signal_header
        self.dataset = dataset_item._parent
        dts = self.dataset
        if not hasattr(dts, 'q_custom_color'):
            dts.q_custom_color = glasbey_l_qcolors[dts.q_row] \
              if canvas_widget.dark_mode else glasbey_d_qcolors[dts.q_row]
        color = QColor(self.dataset.q_custom_color)
        color.setAlpha(alpha)
        self.setPen(color, style=pen_style,
                    width=pen_width)
        self.setVisible(self.dataset.q_checked_state)
        if not hasattr(self.dataset, 'plot_items'):  # need to inject ref.
            self.dataset.plot_items = []             # for highlighting and
        self.dataset.plot_items.append(self)         # visib. change signaling
        if self.canvas_widget is not None:
            self.set_spectrum_data()
            self.canvas_widget.addItem(self)

    def set_spectrum_data(self, x_mode=None, y_mode=None):
        if x_mode is None:
            x_mode = self.canvas_widget.x_axis_mode
        if x_mode == 'cameca':
            x = self.signal.x_100k_sin_theta
        elif x_mode == 'energy':
            x = self.signal.x_keV
        elif x_mode == 'wavelength':
            x = self.signal.x_nm
        if y_mode is None:
            y_mode = self.canvas_widget.y_axis_mode
        if y_mode == 'cps':
            y = self.signal.y_cps
        elif y_mode == 'cts':
            y = self.signal.y_cts
        elif y_mode == 'cpsna':
            y = self.signal.y_cps_per_nA
        if x.shape[0] > y.shape[0]:  # a hack to plot corrupted content
            x = x[:y.shape[0]]
        self.setData(x=x, y=y)
        self.x_ref = x
        self.y_ref = y

    def remove_from_model(self):
        """actually remove from data container which is checked by model,
        but model does not need to be informed as the content of .plot_items
        are checked only during check_box state changes"""
        self.dataset.plot_items.remove(self)


class DummyCamecaWDS(CamecaWDS):
    def __init__(self):
        self.file_basename = 'calculated'
        self.q_children = []
        self.q_check_state = 0

    def append_dataset(self, dataset):
        dataset.q_parent = self
        self.q_children.append(dataset)


class SpecXTALCombiModel(QAbstractListModel):
    # Custom signals:
    combinationCheckedStateChanged = Signal(object, bool)
    xtalFamilyChanged = Signal(str, float, float, str)

    # Qt Custom/User Roles:
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
        for stuff in self.combinations:
            stuff.q_checked_state = Qt.Unchecked

    def get_checked_combinations(self):
        return [i for i in self.combinations
                if i.q_checked_state == Qt.Checked]

    def uncheck_all_combinations(self):
        combinations = self.get_checked_combinations()
        rows = [self.combinations.index(i)
                for i in combinations]
        for r in rows:
            self.setData(self.index(r), Qt.Unchecked, Qt.CheckStateRole)

    def check_on_combination(self, combination):
        if combination in self.combinations:
            row = self.combinations.index(combination)
            self.uncheck_all_combinations()
            self.setData(self.index(row), Qt.Checked, Qt.CheckStateRole)

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
            pen = QPen(cam_def_colors[node.family_name], 4,
                       node.q_pen_style)
            painter.setPen(pen)
            painter.drawLine(0, 1, 48, 1)
            painter.end()
            return qpix
        if role == Qt.CheckStateRole:
            if not hasattr(node, 'q_checked_state'):
                node.q_checked_state = Qt.Unchecked
            return node.q_checked_state
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
            node.q_checked_state = value
            if value == Qt.Unchecked:
                if not any([i.q_checked_state for i in self.combinations]):
                    self.layoutAboutToBeChanged.emit()
                    self.selected_xtal_family = None
                    self.layoutChanged.emit()
                self.combinationCheckedStateChanged.emit(node, False)
            elif not self.ignore_family_constrain:
                if self.selected_xtal_family is None:
                    self.layoutAboutToBeChanged.emit()
                    self.set_xtal_family(
                        self.combinations[index.row()])
                    self.layoutChanged.emit()
            if value == Qt.Checked:
                self.combinationCheckedStateChanged.emit(node, True)
        if role == self.LineStyleRole:
            self.layoutAboutToBeChanged.emit()
            node.q_pen_style = value
            self.layoutChanged.emit()
        if role == self.LineWidthRole:
            node.q_pen_width = value
        self.dataChanged.emit(index, index, [role])
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
                i.q_checked_state = 0
                self.combinations.insert(start_row, i)
            self.endInsertRows()

    def change_xtal_exclusivness(self, mode):
        if mode == 'cameca':
            self.setIgnoreFamilyConstrain(False)
        else:
            self.setIgnoreFamilyConstrain(True)

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
            if (spect_header.q_checked_state and
                    self.selected_xtal_family is None):
                self.set_xtal_family(spect_header)
            elif spect_header.q_checked_state:
                if self.selected_xtal_family != spect_header.family_name:
                    self.setData(self.index(i), 0, Qt.CheckStateRole)

    def set_xtal_family(self, header):
        self.selected_xtal_family = header.family_name
        html_family_str = """<div style="background-color:{};color:#000000;">
                             &nbsp;{}&nbsp;</div>""".format(
                cam_def_colors[header.family_name].name(),
                header.family_name)
        self.xtalFamilyChanged.emit(header.family_name,
                                    header.two_d,
                                    header.k,
                                    html_family_str)

    def flags(self, index):
        if self.ignore_family_constrain or self.selected_xtal_family is None:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        if self.combinations[index.row()].family_name == \
                self.selected_xtal_family:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.NoItemFlags


class CamecaWDSTreeModel(QAbstractItemModel):
    """This model is simple as it is intended only for two level
    containing data.That simplifies implementation of check state
    by checking parent node (filename) of imported Wds file(s).
    This model is not universal - it hooks directly with data,
    otherwise than examples of Qt it does not use brokering
    Classes as i.e. NodeTree and similar."""
    SpectrumCurvesRole = Qt.UserRole
    wds_files_appended = Signal(object)

    def __init__(self, cameca_files, dark_mode=True, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self.collection = cameca_files
        self.dark_mode = dark_mode
        # alpha/transparency for curves when not highlighted
        self.global_alpha = 200
        # this flag is used for tristate check behaviour
        # to prevent children<->parent loops:
        self.parent_selects_children_flag = False
        # That is for custom node with calculated WDS spectra
        self.last_item_is_custom = False
        self.spec_xtal_selection_model = None

    def change_global_alpha(self, value):
        """change transparency of all curves in the model,
        that is ignored for highlighted curves in their function
        which is called from this function"""
        if (value > 255) or (value < 0):
            raise ValueError(
                "alpha should be between 0 to 255,"
                " but value applied is {}".format(value))
        self.global_alpha = value
        for wds_file in self.collection:
            for dataset in wds_file.content.datasets:
                for curve in dataset.plot_items:
                    curve.set_curve_alpha(value)

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
        """reimplemented"""
        if index == QModelIndex():
            return True
        node = index.internalPointer()
        if node is not None and node.q_row_count > 0:
            return True
        return False

    def rowCount(self, index):
        """reimplemented"""
        if index.isValid():
            node = index.internalPointer()
            return node.q_row_count
        return len(self.collection)

    def columnCount(self, parent):
        """reimplemented"""
        return 1

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """reimplemented"""
        if orientation == Qt.Horizontal and section == 0 and\
                role == Qt.DisplayRole:
            return 'WDS files / Datasets'

    def highlight_spectra(self, selected, deselected=None):
        for s_idx in selected.indexes():
            node = s_idx.internalPointer()
            for plot_item in node.plot_items:
                plot_item.highlight()
        if deselected is None:
            return
        for d_idx in deselected.indexes():
            node = d_idx.internalPointer()
            for plot_item in node.plot_items:
                plot_item.dehighlight(alpha=self.global_alpha)

    def data(self, index, role):
        row = index.row()
        node = index.internalPointer()

        if (role == self.SpectrumCurvesRole) and\
                isinstance(node, Cameca.Dataset):
            return node.plot_items

        if role == Qt.DisplayRole:
            if isinstance(node, CamecaBase):
                return node.file_basename
            if isinstance(node, Cameca.Dataset):
                return '{}: {}'.format(row + 1, node.comment.text)

        if role == Qt.ToolTipRole:
            if isinstance(node, Cameca.Dataset):
                ts = node.extras.datetime_and_pos[0].datetime.unix_timestamp
                return "".join(
                    [f"dataset {row + 1} contains:\n  ",
                     '\n  '.join([
                         ('CORRUPTED! ' if i.signal.corrupted else '')
                         + str(i.signal_header)
                         + f" {i.signal_header.beam_current:.1f} nA with dt {i.signal.dwell_time:.4g} s/chan"
                         for i in node.items]),
                     datetime.fromtimestamp(ts).strftime("\n %Y-%m-%d %H:%M")])

        if (role == Qt.ForegroundRole and
                isinstance(node, Cameca.Dataset) and
                any([i.signal.corrupted for i in node.items])):
            return QColor(Qt.red)

        if role == Qt.CheckStateRole:
            if isinstance(node, CamecaBase):
                if node.q_checked_state == 0:
                    return Qt.Unchecked
                if node.q_checked_state == node.q_row_count:
                    return Qt.Checked
                return Qt.PartiallyChecked
            if isinstance(node, Cameca.Dataset):
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
        if not index.isValid() and role in (Qt.CheckStateRole,
                                            Qt.EditRole,
                                            Qt.DecorationRole):
            return False

        node = index.internalPointer()
        if role == Qt.CheckStateRole:
            if isinstance(node, CamecaBase):
                if value == Qt.Checked:
                    node.q_checked_state = node.q_row_count
                elif value == Qt.Unchecked:
                    node.q_checked_state = 0
                if value != Qt.PartiallyChecked:
                    self.set_all_children(index, value)
            elif isinstance(node, Cameca.Dataset):
                node.q_checked_state = value
                # It could look that using dataChanged and connecting plot
                # items with that would be more clean way, but this
                # way is much faster, as there needs to be done no iteration
                # over an over datasets; Single dataset checked - means
                # only plots which are in the list change visibility
                for plot_item in node.plot_items:
                    plot_item.setVisible(value)
                self.update_parent_check_state(index, value)
        if role == Qt.EditRole:
            node.text = value
        if role == Qt.DecorationRole:
            node.q_custom_color = value
            for j in node.plot_items:
                j.set_curve_color(value)
        self.dataChanged.emit(index, index, [role])
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

    #def initialize_calculated_container(self):
    #    parent = QModelIndex()
    #    self.beginInsertRows(parent, self.rowCount() + 1,
    #                         self.rowCount() + 1,)
    #    self.collection.append(DummyCamecaWDS())
    #    self.last_item_is_custom = True
    #    self.endInsertRows()

    #def append_calculated_dataset(self, result):
    #    if not self.last_item_is_custom:
    #        self.initialize_calculated_container()
    #    parent = self.index(self.rowCount() - 1)
    #    self.beginInsertRows(parent, self.rowCount(parent) + 1,
    #                         self.rowCount(parent) + 1)
    #    self.collection[-1].append_dataset(result)
    #    self.endInsertRows()

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
        self.wds_files_appended.emit(wds_files)

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
