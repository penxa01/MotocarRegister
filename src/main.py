import sys
import PyQt5.QtWidgets as widget
import PyQt5.QtGui as Gui
from Views.mainView import MainWindow

if __name__ == "__main__":
    app = widget.QApplication(sys.argv)
    app.setWindowIcon(Gui.QIcon("src/assets/motocarIcon.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())