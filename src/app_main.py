from utils.loggs.logger import init_logger
from window.AppWindow import AppWindow

if __name__ == '__main__':
    logger = init_logger("app")
    app = AppWindow()
    app.mainloop()
