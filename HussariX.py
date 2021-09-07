import sys
import os

from datetime import datetime

from PyQt5.QtCore import Qt, QSettings, QDir
from PyQt5 import QtGui, QtWidgets
from pyqtgraph.dockarea import Dock, DockArea
from lib.ui.CamecaQtModels import CamecaWDSTreeModel
from lib.ui import SpectrumWidgets as sw
from lib.parsers import cameca
from lib.icons.icons import IconProvider

setting = QSettings('setting.ini', QSettings.IniFormat)
# check if there is peaksight installed
CAMSOFT_IS_PRESENT = False
if os.name == 'nt':
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"SOFTWARE\Cameca\SX\Configuration") as cam_con:
            cam_data_path = winreg.QueryValueEx(cam_con, "DataPath")[0]
            CAMSOFT_IS_PRESENT = True
    except EnvironmentError:
        pass


class DockMenu(QtWidgets.QMenu):
    def __init__(self, dock_widget, parent=None):
        self.dock_widget = dock_widget
        name = dock_widget.title()
        QtWidgets.QMenu.__init__(self, name, parent=parent)
        self.rename_action = QtWidgets.QAction('rename')
        self.rename_action.setIcon(
            QtGui.QIcon(self.parent().icon_provider.get_icon_path(
                'rename.svg'
            )))
        self.del_action = QtWidgets.QAction('discard plot')
        self.del_action.setIcon(
            QtGui.QIcon(self.parent().icon_provider.get_icon_path(
                'plot-window-close.svg'
            )))
        self.addAction(self.rename_action)
        self.addAction(self.del_action)
        self.rename_action.triggered.connect(self.rename_dock)
        self.del_action.triggered.connect(self.remove_dock)

    def rename_dock(self):
        dlg = QtWidgets.QInputDialog()
        dlg.setTextValue(self.dock_widget.title())
        dlg.setLabelText("Give a new name for Plot Widget")
        renamed = dlg.exec()
        if renamed:
            new_text = dlg.textValue()
            self.dock_widget.setTitle(new_text)
            self.dock_widget.widgets[0].name = new_text
            self.setTitle(new_text)

    def remove_dock(self):
        main_window = self.parent()
        main_window.destroy_wds_plotWidget(self.dock_widget)


class HussariX(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        self.setGeometry(20, 20, 800, 600)
        placeholder_text = QtWidgets.QLabel(
            "Content will appear here after opening file")
        placeholder_text.setWhatsThis(
            """<p>After opening file this is transformed into Docking Area,
            where any newly opened window can be dragged and placed
            or stacked independently, or even poped-out to separate
            independent window (useful in multi-monitor setup)</p>
            """)
        placeholder_text.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(placeholder_text)
        self.docking_area = DockArea()
        self.icon_provider = IconProvider(self)
        self.plot_n = 0
        menu = self.menuBar()
        file_m = menu.addMenu("File")
        self.plotting_m = menu.addMenu("Plotting")
        self.help_m = menu.addMenu("Help")
        self.plotting_m_entries = []
        self.setWindowTitle("HussariX")
        icon = QtGui.QIcon()
        for i in [16, 22, 32, 48, 64]:
            icon.addFile(
                self.icon_provider.get_icon_path(
                    'hussarix_{}_icon.svg'.format(i),
                    neutral=True))
        self.setWindowIcon(icon)
        self.action_whats_this = QtWidgets.QWhatsThis.createAction(self)
        self.help_m.addAction(self.action_whats_this)
        self.help_m.addAction("About Qt", QtWidgets.qApp.aboutQt)
        self.action_open_wdsDat = QtWidgets.QAction('Open wdsDat')
        self.action_open_wdsDat.setIcon(
            QtGui.QIcon(self.icon_provider.get_icon_path(
                'wdsDat_open.svg')))
        self.action_open_qtiDat = QtWidgets.QAction('Open qtiDat')
        self.action_open_qtiDat.setIcon(
            QtGui.QIcon(self.icon_provider.get_icon_path(
                'qtiDat_open.svg')))
        self.action_open_impDat = QtWidgets.QAction('Open impDat')
        self.action_open_impDat.setIcon(
            QtGui.QIcon(self.icon_provider.get_icon_path(
                'impDat_open.svg')))
        self.action_open_qtiDat.setDisabled(True)
        self.action_open_impDat.setDisabled(True)
        self.action_open_spx = QtWidgets.QAction('Open spx')
        self.action_open_spx.setIcon(
            QtGui.QIcon(self.icon_provider.get_icon_path('spx_open.svg')))
        self.action_open_spx.setToolTip('Bruker Esprit spectra .spx')
        self.action_open_rtx = QtWidgets.QAction('Open rtx')
        self.action_open_rtx.setIcon(
            QtGui.QIcon(self.icon_provider.get_icon_path('rtx_open.svg')))
        self.action_open_rtx.setToolTip('Bruker Esprit project .rtx')
        self.action_open_rtx.setDisabled(True)
        file_m.addSection('Cameca Peaksight files')
        file_m.addAction(self.action_open_wdsDat)
        file_m.addAction(self.action_open_qtiDat)
        file_m.addAction(self.action_open_impDat)
        file_m.addSection('Bruker Esprit files')
        file_m.addAction(self.action_open_spx)
        file_m.addAction(self.action_open_rtx)
        self.any_file_opened = False
        self.any_wds_opened = False
        file_m.addSeparator()
        self.plotting_m.addSeparator()
        self.action_quit = QtWidgets.QAction('Quit')
        self.action_quit.setShortcut('Ctrl+Q')
        self.action_quit.triggered.connect(QtWidgets.qApp.quit)
        file_m.addAction(self.action_quit)
        self.action_mkPlotItem = QtWidgets.QAction('New Plotting Widget')
        self.action_mkPlotItem.setIcon(
            QtGui.QIcon(self.icon_provider.get_icon_path(
                'plot-window-new.svg')))
        self.plotting_m.addAction(self.action_mkPlotItem)
        self.action_mkPlotItem.setEnabled(False)
        self.plot_widgets = []
        self.action_open_wdsDat.triggered.connect(self.open_wds_files)

    def open_wds_files(self):
        dialog = QtWidgets.QFileDialog()
        # agg_checkbox = QtWidgets.QCheckBox(
        #    'Sum the items with duplicate comment')
        # dl = dialog.layout()
        # dl.addWidget(agg_checkbox)
        dialog.setNameFilter("Cameca Wds Data (*.wdsDat);;All Files (*)")
        dialog.setWindowTitle("select WdsDat file(s)")
        dialog.setFileMode(dialog.ExistingFiles)
        if CAMSOFT_IS_PRESENT:
            with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"SOFTWARE\Cameca\SX\Configuration") as conf:
                current_project = winreg.QueryValueEx(conf,
                                                      "CurrentProject")[0]
                current_sample = winreg.QueryValueEx(conf,
                                                     "CurrentSample")[0]
            wds_data_path = os.path.join(cam_data_path, current_project,
                                         current_sample, "WDS Spectra")
            dialog.setDirectory(wds_data_path)
        else:
            last_dir = setting.value('last_dir')
            if last_dir is not None and QDir(last_dir).exists():
                dialog.setDirectory(last_dir)
        dialog.exec()
        files = dialog.selectedFiles()
        if len(files) > 0 and 'wdsDat' in files[0]:
            setting.setValue('last_dir', dialog.directory().absolutePath())
            if not self.any_file_opened:
                self.setCentralWidget(self.docking_area)
                self.any_file_opened = True
                self.docking_widgets = []
            if not self.any_wds_opened:
                self.wds_files_model = CamecaWDSTreeModel([])
                self.wds_tree_view = QtWidgets.QTreeView()
                self.wds_tree_view.setWhatsThis(
                    """<h4> WDS dataset/file tree View</h4>
                    <p> This is where visibility of given dataset can
                    be controlled by checking/unchecking the dataset;
                    When cheking/unchecking filename it will check/uncheck
                    all datasets under that filename in the tree;
                    Visibility is changed for generated curves in all opened
                    Plotting Widgets simultaniously.</p>
                    <p>Datasets have capability of multi selection
                    (with a help of "Shift" or/and "Ctrl" key modifiers);
                    Selected datasets will result in highlighting
                    the coresponding curves in the Plotting Widgets
                    (if dataset is checked in the tree, and checked Xtal/spect
                    combinations is present in the dataset)</p>
                    <p>Current item (the last item clicked or navigated with
                    keyboard) will change background model in Plotting Widgets
                    for simple Peak-Bakground markers</p>"""
                )
                self.wds_tree_view.setModel(self.wds_files_model)
                self.wds_tree_view.setStyleSheet(
                    'show-decoration-selected: 0')
                self.wds_files_selection_model = self.wds_tree_view.selectionModel()
                self.wds_files_selection_model.selectionChanged.connect(
                    self.wds_files_model.highlight_spectra)
                self.wds_tree_view.setHeaderHidden(True)
                self.wds_tree_view.setSelectionMode(
                    QtWidgets.QTreeView.ExtendedSelection)
                self.wds_items_dw = Dock('WDS Files/Datasets',
                                         widget=self.wds_tree_view,
                                         autoOrientation=False,
                                         size=(100, 100))
                self.wds_items_dw.setStretch(x=1, y=2)
                alpha_container = QtWidgets.QWidget()
                qgb_layout = QtWidgets.QVBoxLayout(alpha_container)
                alpha_container.setLayout(qgb_layout)
                self.alpha_spin_box = QtWidgets.QSpinBox()
                alpha_container.setWhatsThis(
                    """<h4>Global alpha/transparency of plotted curves</h4>
                    <p>with many WDS spectra opened the Plotting Canvas/-es
                    get/-s easily cluttered. For better clarity curve alpha
                    (transparency) comes to help. Alpha can be changed from
                    0 (Fully transparent) to 255 (Fully opaque). This value
                    is forced for all plotted curves globaly, unless curve is
                    from slected dataset (is highlighted)</p>"""
                )
                self.alpha_spin_box.setMinimum(0)
                self.alpha_spin_box.setMaximum(255)
                self.alpha_spin_box.setValue(200)
                qgb_layout.addWidget(QtWidgets.QLabel('alpha of curves:'))
                qgb_layout.addWidget(self.alpha_spin_box)
                self.wds_items_dw.addWidget(alpha_container)
                self.docking_area.addDock(self.wds_items_dw, position="left")
                self.wds_selection_model = self.wds_tree_view.selectionModel()
                self.any_wds_opened = True
                self.action_mkPlotItem.setEnabled(True)
                self.action_mkPlotItem.trigger()
                self.alpha_spin_box.valueChanged.connect(
                    self.wds_files_model.change_global_alpha)
                self.action_mkPlotItem.triggered.connect(
                    self.make_wds_plotWidget)
                self.action_mkPlotItem.trigger()  # make at least one
            wds_files = [cameca.CamecaWDS(i) for i in files]
            self.wds_files_model.append_wds_files(wds_files)

    def make_wds_plotWidget(self):
        self.plot_n += 1
        widget = sw.WDSSpectraGUI(self.wds_files_model,
                                  self.wds_files_selection_model)
        plotting_dw = Dock('WDS Plot {}'.format(self.plot_n), widget=widget,
                           autoOrientation=False)
        widget.attachedToParentWidget.connect(plotting_dw.setVisible)
        widget.name = plotting_dw.title()
        self.plot_widgets.append(widget)
        self.docking_widgets.append(plotting_dw)
        plotting_dw.setStretch(x=5, y=1)
        if len(self.docking_widgets) == 1:
            self.docking_area.addDock(plotting_dw, position="right",
                                      size=(100, 100))
        else:
            self.docking_area.addDock(plotting_dw, "bottom",
                                      self.docking_widgets[-2],
                                      size=(100, 100))
        plotting_dw.menu_entry = DockMenu(plotting_dw,
                                          parent=self)
        plotting_dw.menu_action = self.plotting_m.addMenu(
            plotting_dw.menu_entry)
        self.plotting_m.update()

    def destroy_wds_plotWidget(self, dock_widget):
        dock_widget.widgets[0].prepare_to_destroy()
        self.plot_widgets.remove(dock_widget.widgets[0])
        self.docking_widgets.remove(dock_widget)
        self.plotting_m.removeAction(dock_widget.menu_action)
        dock_widget.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = HussariX()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
