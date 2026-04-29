import sys
import json
import time
import os
from pathlib import Path
import pyotp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QMessageBox, QSplitter)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette


class TwoFactorAuthenticator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2FA 验证器")
        self.setGeometry(100, 100, 500, 600)
        
        self.data_file = Path.home() / ".2fa_secrets.json"
        self.secrets = {}
        self.load_secrets()
        
        self.init_ui()
        self.start_timer()
        
    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QWidget { background-color: #ffffff; }
            QLabel { color: #333333; }
            QLineEdit { 
                border: 2px solid #e0e0e0; 
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton#deleteBtn { background-color: #f44336; }
            QPushButton#deleteBtn:hover { background-color: #d32f2f; }
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("2FA 验证器")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        code_display_layout = QVBoxLayout()
        code_display_layout.setSpacing(5)
        
        self.code_label = QLabel("------")
        self.code_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.code_label.setAlignment(Qt.AlignCenter)
        self.code_label.setStyleSheet("color: #2196F3; letter-spacing: 8px;")
        code_display_layout.addWidget(self.code_label)
        
        self.timer_label = QLabel("剩余时间: --s")
        self.timer_label.setFont(QFont("Arial", 12))
        self.timer_label.setAlignment(Qt.AlignCenter)
        code_display_layout.addWidget(self.timer_label)
        
        self.current_secret_label = QLabel("")
        self.current_secret_label.setFont(QFont("Arial", 10))
        self.current_secret_label.setAlignment(Qt.AlignCenter)
        self.current_secret_label.setStyleSheet("color: #666666;")
        code_display_layout.addWidget(self.current_secret_label)
        
        main_layout.addLayout(code_display_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e0e0e0; }")
        
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setSpacing(10)
        
        input_layout.addWidget(QLabel("添加新密钥:"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("密钥名称 (例如: GitHub)")
        input_layout.addWidget(self.name_input)
        
        self.secret_input = QLineEdit()
        self.secret_input.setPlaceholderText("2FA Secret (Base32格式)")
        input_layout.addWidget(self.secret_input)
        
        add_btn = QPushButton("添加密钥")
        add_btn.clicked.connect(self.add_secret)
        input_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("删除选中密钥")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self.delete_secret)
        input_layout.addWidget(delete_btn)
        
        input_layout.addStretch()
        splitter.addWidget(input_widget)
        
        self.secret_list = QListWidget()
        self.secret_list.itemClicked.connect(self.on_secret_selected)
        self.refresh_secret_list()
        splitter.addWidget(self.secret_list)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        if self.secrets:
            first_key = next(iter(self.secrets.keys()))
            self.current_secret = first_key
            self.current_secret_label.setText(f"当前: {first_key}")
        else:
            self.current_secret = None
        
    def load_secrets(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.secrets = json.load(f)
            except:
                self.secrets = {}
        else:
            self.secrets = {}
            
    def save_secrets(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.secrets, f, ensure_ascii=False, indent=2)
            
    def refresh_secret_list(self):
        self.secret_list.clear()
        for name in sorted(self.secrets.keys()):
            item = QListWidgetItem(name)
            self.secret_list.addItem(item)
            
    def add_secret(self):
        name = self.name_input.text().strip()
        secret = self.secret_input.text().strip()
        
        if not name or not secret:
            QMessageBox.warning(self, "错误", "请填写密钥名称和Secret！")
            return
            
        try:
            pyotp.TOTP(secret).now()
        except:
            QMessageBox.warning(self, "错误", "无效的Secret格式！请确保是Base32格式。")
            return
            
        self.secrets[name] = secret
        self.save_secrets()
        self.refresh_secret_list()
        
        self.name_input.clear()
        self.secret_input.clear()
        
        if not self.current_secret:
            self.current_secret = name
            self.current_secret_label.setText(f"当前: {name}")
            
        QMessageBox.information(self, "成功", f"密钥 '{name}' 添加成功！")
        
    def delete_secret(self):
        current_item = self.secret_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "错误", "请先选择要删除的密钥！")
            return
            
        name = current_item.text()
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除密钥 '{name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.secrets[name]
            self.save_secrets()
            self.refresh_secret_list()
            
            if self.current_secret == name:
                if self.secrets:
                    self.current_secret = next(iter(self.secrets.keys()))
                    self.current_secret_label.setText(f"当前: {self.current_secret}")
                else:
                    self.current_secret = None
                    self.current_secret_label.setText("")
                    self.code_label.setText("------")
                    
    def on_secret_selected(self, item):
        name = item.text()
        self.current_secret = name
        self.current_secret_label.setText(f"当前: {name}")
        
    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_code)
        self.timer.start(100)
        self.update_code()
        
    def update_code(self):
        if not self.current_secret or self.current_secret not in self.secrets:
            return
            
        secret = self.secrets[self.current_secret]
        totp = pyotp.TOTP(secret)
        code = totp.now()
        remaining = 30 - (int(time.time()) % 30)
        
        self.code_label.setText(code)
        self.timer_label.setText(f"剩余时间: {remaining:02d}s")
        
        if remaining <= 5:
            self.timer_label.setStyleSheet("color: #f44336;")
        else:
            self.timer_label.setStyleSheet("color: #666666;")


def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = TwoFactorAuthenticator()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
