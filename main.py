from logic import *

def main():
    """Starts and launches the GUI application"""
    application = QApplication([])
    window = Logic()
    window.show()
    application.exec()

if __name__ == '__main__':
    main()