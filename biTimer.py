import sys
import time
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction,
                             QDialog, QTextEdit, QPushButton, QHBoxLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon


class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 获取当前文件的目录
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置图标和待办事项文件路径
        icon_path = os.path.join(current_dir, "icon.png")
        self.todo_file_path = os.path.join(current_dir, "todo.txt")

        self.initUI()
        self.tray_icon = QSystemTrayIcon(self)
        icon = QIcon(icon_path)

        if not icon.isNull():
            self.tray_icon.setIcon(icon)
            self.tray_icon.setVisible(True)
            print("Tray icon set successfully.")
        else:
            print("Error: Tray icon is null.")

        self.create_tray_menu()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 设置窗口始终在顶部并透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 更新窗口位置
        self.update_position()

    def initUI(self):
        self.setWindowTitle("biTimer")

        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white; font-size: 48px;")

        self.todo_label = QLabel(self)
        self.todo_label.setAlignment(Qt.AlignCenter)
        self.todo_label.setStyleSheet("color: white; font-size: 48px;")

        layout = QVBoxLayout()
        layout.addWidget(self.time_label)
        layout.addWidget(self.todo_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_time()
        self.load_todo()

    def update_time(self):
        current_time = time.strftime('%Y-%m-%d\n%H:%M:%S', time.localtime())
        self.time_label.setText(current_time)

    def create_tray_menu(self):
        menu = QMenu()

        edit_action = QAction("编辑待办事项", self)
        edit_action.triggered.connect(self.edit_todo)
        menu.addAction(edit_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def edit_todo(self):
        dialog = CustomInputDialog(self)
        dialog.exec_()
        self.load_todo()

    def load_todo(self):
        try:
            with open(self.todo_file_path, 'r') as file:
                todo = file.read()
            self.todo_label.setText(todo)
        except FileNotFoundError:
            self.todo_label.setText("没有待办事项")

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.update_position()

    def update_position(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.frameSize().width()
        window_height = self.frameSize().height()

        # 将窗口移动到右上角偏下一点的位置
        self.move(screen_width - window_width -50, 200)  # 偏移量200

    def resizeEvent(self, event):
        self.update_position()
        super().resizeEvent(event)

    def exit_app(self):
        self.tray_icon.hide()
        QApplication.instance().quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "biTimer",
            "应用程序已最小化到系统托盘。要退出，请使用系统托盘中的退出选项。",
            QSystemTrayIcon.Information,
            2000
        )


class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("编辑待办事项")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        self.input = QTextEdit(self)
        self.input.setPlaceholderText("输入你的待办事项")

        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.accept)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.input)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        if os.path.exists(parent.todo_file_path):
            with open(parent.todo_file_path, 'r') as file:
                self.input.setText(file.read())

    def accept(self):
        with open(self.parent().todo_file_path, 'w') as file:
            file.write(self.input.toPlainText())
        super().accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainWin = ToDoApp()
    mainWin.show()
    sys.exit(app.exec_())
