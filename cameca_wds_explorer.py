from lib.ui import SpectrumWidgets as swidget
from lib.ui import WDSWidget
from lib.ui import CamecaQtModels
from lib.parsers import cameca
from PyQt5 import QtWidgets, QtCore
import sys


class DummyCamecaWDS(cameca.CamecaWDS):
    def __init__(self):
        self.file_basename = 'calculated'
        self.datasets = []

    def append_sum_of_selected(self, datasets):
        new_dataset = sum(datasets)
        new_dataset.parent = self
        self.datasets.append(new_dataset)


class WDSScanViewer(WDSWidget.Ui_WDSScanWidget,
                    QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('WDS Scan Viewer')
        self.bkg_groupBox.hide()
        self.spect_layout = QtWidgets.QHBoxLayout(self.spect_widget_container)
        # Probably my OS theme is ugly and that is unnecessary:
        self.spect_layout.setContentsMargins(1, 1, 1, 1)
        self.spec_widget = swidget.EDSSpectraGUI(
            initial_mode='wds',
            pet_opacity=0.91)
        self.spect_layout.addWidget(self.spec_widget)
        self.openButton.clicked.connect(self.open_wds_files)
        self.selection_model = self.spectraTreeView.selectionModel()

    def open_wds_files(self):
        dialog = QtWidgets.QFileDialog()
        agg_checkbox = QtWidgets.QCheckBox(
            'Sum the items with duplicate comment')
        dl = dialog.layout()
        dl.addWidget(agg_checkbox)
        dialog.setNameFilter("Cameca Wds Data (*.wdsDat);;All Files (*)")
        dialog.setWindowTitle("select WdsDat file(s)")
        dialog.setFileMode(dialog.ExistingFiles)
        dialog.exec()
        files = dialog.selectedFiles()
        if 'wdsDat' in files[0]:
            agg = agg_checkbox.checkState()
            self.wds_files = [cameca.CamecaWDS(i) for i in files]
            if agg:
                for i in self.wds_files:
                    i.aggregate()
            self.wds_file_model = CamecaQtModels.CamecaWDSTreeModel(
                                                        self.wds_files)
            self.spectraTreeView.setModel(self.wds_file_model)
            combinations = []
            for i in self.wds_files:
                combinations.extend(i.get_set_of_xtal_spect_combinations())
            self.combinations = sorted(set(combinations))
            comb_text = ['{}: {}'.format(*i) for i in self.combinations]
            self.comb_model = QtCore.QStringListModel(comb_text)
            self.spectComboBox.setModel(self.comb_model)

    def add_sum_of_items(self):
        [i.internalPointer() for i in self.selection_model().selected()]


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = WDSScanViewer()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
