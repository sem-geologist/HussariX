
from PyQt5.Qt import QImage, QIcon, QPixmap
from PyQt5.QtCore import QRectF
from pyqtgraph import ImageItem

class Image:
    """requires that parser would
    initialize self.image_array"""
    
    def gen_icon(self):
        qimage = QImage(self.image_array,
                  self.image_array.shape[1],
                  self.image_array.shape[0],
                  QImage.Format_Grayscale8)
        self.icon = QIcon(QPixmap(qimage))
        
    def gen_image_item(self, height, width):
        self.pg_image_item = ImageItem(self.image_array)
        self.pg_image_item.setRect(QRectF(0, height, width, -height))
