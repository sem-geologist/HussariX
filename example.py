import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from qbhm_viewer.eds import spectrum_widget_Qt5 as swidget




if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    pet = swidget.EDSSpectraGUI(None, icon_size=24, pet_opacity=0.8)
    pet.show()
    
    sys.exit(app.exec_())
