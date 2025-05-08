import sys
import PyQt5.QtWidgets as widget
import PyQt5.QtGui as Gui
from Views.mainView import MainWindow
from PyQt5.QtWidgets import QMessageBox

if __name__ == "__main__":
    try:
        app = widget.QApplication(sys.argv)
        app.setWindowIcon(Gui.QIcon("src/assets/motocarIcon.ico"))
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox .critical(None, "Error", f"Ocurrió un error: {str(e)}")