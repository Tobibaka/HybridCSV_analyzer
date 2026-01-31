"""
Chemical Equipment Parameter Visualizer - Desktop Application
Built with PyQt5 and Matplotlib
"""

import sys
import os
import requests
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QTabWidget, QGroupBox, QMessageBox, QLineEdit, QFormLayout,
    QSplitter, QListWidget, QListWidgetItem, QHeaderView, QFrame,
    QStatusBar, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


# API Configuration
API_BASE_URL = "http://localhost:8000/api"


class APIClient:
    """Client for communicating with the Django backend API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = API_BASE_URL
    
    def health_check(self):
        """Check if API is available."""
        try:
            response = self.session.get(f"{self.base_url}/health/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def login(self, username, password):
        """Login user."""
        response = self.session.post(
            f"{self.base_url}/auth/login/",
            json={"username": username, "password": password}
        )
        return response
    
    def register(self, username, email, password):
        """Register new user."""
        response = self.session.post(
            f"{self.base_url}/auth/register/",
            json={"username": username, "email": email, "password": password}
        )
        return response
    
    def logout(self):
        """Logout user."""
        response = self.session.post(f"{self.base_url}/auth/logout/")
        return response
    
    def get_current_user(self):
        """Get current authenticated user."""
        response = self.session.get(f"{self.base_url}/auth/user/")
        return response
    
    def get_datasets(self):
        """Get list of datasets."""
        response = self.session.get(f"{self.base_url}/datasets/")
        return response
    
    def get_dataset_summary(self, dataset_id):
        """Get dataset summary."""
        response = self.session.get(f"{self.base_url}/datasets/{dataset_id}/summary/")
        return response
    
    def get_dataset_records(self, dataset_id):
        """Get dataset records."""
        response = self.session.get(f"{self.base_url}/datasets/{dataset_id}/records/")
        return response
    
    def upload_csv(self, file_path, name=None):
        """Upload CSV file."""
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            data = {'name': name} if name else {}
            response = self.session.post(
                f"{self.base_url}/upload/",
                files=files,
                data=data
            )
        return response
    
    def delete_dataset(self, dataset_id):
        """Delete a dataset."""
        response = self.session.delete(f"{self.base_url}/datasets/{dataset_id}/")
        return response
    
    def get_report_url(self, dataset_id):
        """Get PDF report download URL."""
        return f"{self.base_url}/datasets/{dataset_id}/report/"


class UploadThread(QThread):
    """Thread for uploading CSV files."""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, api_client, file_path):
        super().__init__()
        self.api_client = api_client
        self.file_path = file_path
    
    def run(self):
        try:
            response = self.api_client.upload_csv(self.file_path)
            if response.status_code == 201:
                self.finished.emit(response.json())
            else:
                self.error.emit(response.json().get('error', 'Upload failed'))
        except Exception as e:
            self.error.emit(str(e))


class ChartCanvas(FigureCanvas):
    """Matplotlib canvas widget for embedding charts in PyQt."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.set_facecolor('#f5f5f5')


class LoginDialog(QDialog):
    """Login/Register dialog."""
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Login / Register")
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout(self)
        
        # Tab widget for login/register
        self.tabs = QTabWidget()
        
        # Login tab
        login_widget = QWidget()
        login_layout = QFormLayout(login_widget)
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        login_layout.addRow("Username:", self.login_username)
        login_layout.addRow("Password:", self.login_password)
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.do_login)
        login_layout.addRow(login_btn)
        self.tabs.addTab(login_widget, "Login")
        
        # Register tab
        register_widget = QWidget()
        register_layout = QFormLayout(register_widget)
        self.register_username = QLineEdit()
        self.register_email = QLineEdit()
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        register_layout.addRow("Username:", self.register_username)
        register_layout.addRow("Email:", self.register_email)
        register_layout.addRow("Password:", self.register_password)
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.do_register)
        register_layout.addRow(register_btn)
        self.tabs.addTab(register_widget, "Register")
        
        layout.addWidget(self.tabs)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
    
    def do_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        try:
            response = self.api_client.login(username, password)
            if response.status_code == 200:
                self.user = response.json().get('user')
                self.accept()
            else:
                QMessageBox.warning(self, "Error", response.json().get('error', 'Login failed'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def do_register(self):
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        try:
            response = self.api_client.register(username, email, password)
            if response.status_code == 201:
                # Auto-login after registration
                login_response = self.api_client.login(username, password)
                if login_response.status_code == 200:
                    self.user = login_response.json().get('user')
                    self.accept()
            else:
                error_msg = response.json()
                if isinstance(error_msg, dict):
                    error_msg = str(list(error_msg.values())[0])
                QMessageBox.warning(self, "Error", str(error_msg))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.api_client = APIClient()
        self.current_user = None
        self.current_dataset = None
        self.summary = None
        self.records = []
        
        self.setup_ui()
        self.check_api_connection()
        self.load_datasets()
    
    def setup_ui(self):
        """Setup the main UI."""
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Upload and History
        left_panel = QWidget()
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        
        # User info and auth buttons
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout(auth_group)
        self.user_label = QLabel("Not logged in")
        auth_layout.addWidget(self.user_label)
        
        auth_buttons = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.show_login_dialog)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.do_logout)
        self.logout_btn.setVisible(False)
        auth_buttons.addWidget(self.login_btn)
        auth_buttons.addWidget(self.logout_btn)
        auth_layout.addLayout(auth_buttons)
        left_layout.addWidget(auth_group)
        
        # Upload section
        upload_group = QGroupBox("Upload CSV")
        upload_layout = QVBoxLayout(upload_group)
        
        self.upload_btn = QPushButton("📁 Select CSV File")
        self.upload_btn.setMinimumHeight(60)
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn)
        
        self.upload_status = QLabel("")
        upload_layout.addWidget(self.upload_status)
        left_layout.addWidget(upload_group)
        
        # History section
        history_group = QGroupBox("Recent Datasets (Last 5)")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_dataset_selected)
        history_layout.addWidget(self.history_list)
        
        history_buttons = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_datasets)
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_selected_dataset)
        history_buttons.addWidget(self.refresh_btn)
        history_buttons.addWidget(self.delete_btn)
        history_layout.addLayout(history_buttons)
        
        self.download_btn = QPushButton("📥 Download PDF Report")
        self.download_btn.clicked.connect(self.download_report)
        history_layout.addWidget(self.download_btn)
        
        left_layout.addWidget(history_group)
        left_layout.addStretch()
        
        main_layout.addWidget(left_panel)
        
        # Right panel - Data display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Summary cards
        summary_group = QGroupBox("Summary Statistics")
        summary_layout = QHBoxLayout(summary_group)
        
        self.total_label = self.create_summary_card("Total Equipment", "0", "#1976d2")
        self.flowrate_label = self.create_summary_card("Avg. Flowrate", "0", "#4caf50")
        self.pressure_label = self.create_summary_card("Avg. Pressure", "0", "#ff9800")
        self.temp_label = self.create_summary_card("Avg. Temperature", "0", "#9c27b0")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.flowrate_label)
        summary_layout.addWidget(self.pressure_label)
        summary_layout.addWidget(self.temp_label)
        right_layout.addWidget(summary_group)
        
        # Tabs for charts and table
        self.tabs = QTabWidget()
        
        # Charts tab
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)
        
        # Pie chart
        self.pie_canvas = ChartCanvas(width=5, height=4)
        charts_layout.addWidget(self.pie_canvas)
        
        # Bar chart
        self.bar_canvas = ChartCanvas(width=6, height=4)
        charts_layout.addWidget(self.bar_canvas)
        
        self.tabs.addTab(charts_widget, "📊 Charts")
        
        # Line chart tab
        line_widget = QWidget()
        line_layout = QVBoxLayout(line_widget)
        self.line_canvas = ChartCanvas(width=10, height=5)
        line_layout.addWidget(self.line_canvas)
        self.tabs.addTab(line_widget, "📈 Parameter Comparison")
        
        # Data table tab
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.data_table)
        
        self.tabs.addTab(table_widget, "📋 Data Table")
        
        right_layout.addWidget(self.tabs)
        main_layout.addWidget(right_panel)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Apply styles
        self.apply_styles()
    
    def create_summary_card(self, title, value, color):
        """Create a summary card widget."""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("value")
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return card
    
    def apply_styles(self):
        """Apply application styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #1976d2;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #eee;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1976d2;
                color: white;
            }
        """)
    
    def check_api_connection(self):
        """Check if API is available."""
        if self.api_client.health_check():
            self.statusBar.showMessage("Connected to API server")
        else:
            self.statusBar.showMessage("⚠️ API server not available - Please start the backend")
            QMessageBox.warning(
                self, 
                "Connection Error",
                "Cannot connect to the backend API.\n\n"
                "Please ensure the Django server is running:\n"
                "cd backend && python manage.py runserver"
            )
    
    def show_login_dialog(self):
        """Show login dialog."""
        dialog = LoginDialog(self.api_client, self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_user = dialog.user
            self.update_user_display()
    
    def do_logout(self):
        """Logout current user."""
        try:
            self.api_client.logout()
            self.current_user = None
            self.update_user_display()
            self.statusBar.showMessage("Logged out successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Logout failed: {str(e)}")
    
    def update_user_display(self):
        """Update user display."""
        if self.current_user:
            self.user_label.setText(f"Welcome, {self.current_user['username']}")
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(True)
        else:
            self.user_label.setText("Not logged in")
            self.login_btn.setVisible(True)
            self.logout_btn.setVisible(False)
    
    def upload_file(self):
        """Handle file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.upload_status.setText("Uploading...")
            self.upload_btn.setEnabled(False)
            
            self.upload_thread = UploadThread(self.api_client, file_path)
            self.upload_thread.finished.connect(self.on_upload_success)
            self.upload_thread.error.connect(self.on_upload_error)
            self.upload_thread.start()
    
    def on_upload_success(self, data):
        """Handle successful upload."""
        self.upload_status.setText("✅ Upload successful!")
        self.upload_btn.setEnabled(True)
        self.statusBar.showMessage("File uploaded successfully")
        
        # Reload datasets and display the new one
        self.load_datasets()
        self.display_dataset(data)
    
    def on_upload_error(self, error):
        """Handle upload error."""
        self.upload_status.setText(f"❌ Error: {error}")
        self.upload_btn.setEnabled(True)
        self.statusBar.showMessage("Upload failed")
    
    def load_datasets(self):
        """Load datasets from API."""
        try:
            response = self.api_client.get_datasets()
            if response.status_code == 200:
                datasets = response.json()
                self.history_list.clear()
                
                for dataset in datasets:
                    item = QListWidgetItem()
                    item.setData(Qt.UserRole, dataset['id'])
                    
                    # Format date
                    date = datetime.fromisoformat(dataset['uploaded_at'].replace('Z', '+00:00'))
                    date_str = date.strftime('%Y-%m-%d %H:%M')
                    
                    item.setText(
                        f"{dataset['name']}\n"
                        f"📅 {date_str}\n"
                        f"📊 {dataset['total_records']} records"
                    )
                    self.history_list.addItem(item)
                
                if datasets:
                    self.history_list.setCurrentRow(0)
        except Exception as e:
            self.statusBar.showMessage(f"Failed to load datasets: {str(e)}")
    
    def on_dataset_selected(self, item):
        """Handle dataset selection."""
        dataset_id = item.data(Qt.UserRole)
        self.load_dataset_details(dataset_id)
    
    def load_dataset_details(self, dataset_id):
        """Load and display dataset details."""
        try:
            summary_response = self.api_client.get_dataset_summary(dataset_id)
            records_response = self.api_client.get_dataset_records(dataset_id)
            
            if summary_response.status_code == 200 and records_response.status_code == 200:
                self.current_dataset = dataset_id
                self.summary = summary_response.json()
                self.records = records_response.json()
                self.update_display()
        except Exception as e:
            self.statusBar.showMessage(f"Failed to load dataset: {str(e)}")
    
    def display_dataset(self, data):
        """Display dataset from upload response."""
        self.current_dataset = data['id']
        self.summary = data['summary']
        self.records = data['records']
        self.update_display()
    
    def update_display(self):
        """Update all display elements with current data."""
        if not self.summary:
            return
        
        # Update summary cards
        self.update_summary_card(self.total_label, str(self.summary.get('total_count', 0)))
        self.update_summary_card(self.flowrate_label, str(self.summary.get('averages', {}).get('flowrate', 0)))
        self.update_summary_card(self.pressure_label, str(self.summary.get('averages', {}).get('pressure', 0)))
        self.update_summary_card(self.temp_label, str(self.summary.get('averages', {}).get('temperature', 0)))
        
        # Update charts
        self.update_pie_chart()
        self.update_bar_chart()
        self.update_line_chart()
        
        # Update table
        self.update_table()
        
        self.statusBar.showMessage(f"Displaying dataset with {len(self.records)} records")
    
    def update_summary_card(self, card, value):
        """Update summary card value."""
        value_label = card.findChild(QLabel, "value")
        if value_label:
            value_label.setText(value)
    
    def update_pie_chart(self):
        """Update pie chart with type distribution."""
        self.pie_canvas.fig.clear()
        ax = self.pie_canvas.fig.add_subplot(111)
        
        type_dist = self.summary.get('type_distribution', {})
        if type_dist:
            colors = ['#1976d2', '#4caf50', '#ff9800', '#9c27b0', '#f44336', '#00bcd4', '#ffc107', '#607d8b']
            ax.pie(
                type_dist.values(),
                labels=type_dist.keys(),
                colors=colors[:len(type_dist)],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.set_title('Equipment Type Distribution', fontweight='bold')
        
        self.pie_canvas.fig.tight_layout()
        self.pie_canvas.draw()
    
    def update_bar_chart(self):
        """Update bar chart with averages by type."""
        self.bar_canvas.fig.clear()
        ax = self.bar_canvas.fig.add_subplot(111)
        
        type_averages = self.summary.get('type_averages', {})
        if type_averages:
            types = list(type_averages.keys())
            x = np.arange(len(types))
            width = 0.25
            
            flowrates = [type_averages[t]['avg_flowrate'] for t in types]
            pressures = [type_averages[t]['avg_pressure'] for t in types]
            temps = [type_averages[t]['avg_temperature'] for t in types]
            
            ax.bar(x - width, flowrates, width, label='Flowrate', color='#1976d2')
            ax.bar(x, pressures, width, label='Pressure', color='#4caf50')
            ax.bar(x + width, temps, width, label='Temperature', color='#ff9800')
            
            ax.set_xlabel('Equipment Type')
            ax.set_ylabel('Average Values')
            ax.set_title('Average Parameters by Type', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(types, rotation=45, ha='right')
            ax.legend()
        
        self.bar_canvas.fig.tight_layout()
        self.bar_canvas.draw()
    
    def update_line_chart(self):
        """Update line chart with parameter comparison."""
        self.line_canvas.fig.clear()
        ax = self.line_canvas.fig.add_subplot(111)
        
        if self.records:
            # Show first 15 records
            display_records = self.records[:15]
            names = [r['equipment_name'].split('-')[0] for r in display_records]
            
            flowrates = [r['flowrate'] for r in display_records]
            pressures = [r['pressure'] for r in display_records]
            temps = [r['temperature'] for r in display_records]
            
            x = range(len(names))
            
            ax.plot(x, flowrates, 'o-', label='Flowrate', color='#1976d2', linewidth=2)
            ax.plot(x, pressures, 's-', label='Pressure', color='#4caf50', linewidth=2)
            ax.plot(x, temps, '^-', label='Temperature', color='#ff9800', linewidth=2)
            
            ax.set_xlabel('Equipment')
            ax.set_ylabel('Parameter Values')
            ax.set_title('Parameter Comparison (First 15 Equipment)', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        self.line_canvas.fig.tight_layout()
        self.line_canvas.draw()
    
    def update_table(self):
        """Update data table."""
        self.data_table.setRowCount(len(self.records))
        
        for row, record in enumerate(self.records):
            self.data_table.setItem(row, 0, QTableWidgetItem(record['equipment_name']))
            self.data_table.setItem(row, 1, QTableWidgetItem(record['equipment_type']))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(record['flowrate'])))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(record['pressure'])))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(record['temperature'])))
    
    def delete_selected_dataset(self):
        """Delete selected dataset."""
        current_item = self.history_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a dataset to delete")
            return
        
        dataset_id = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this dataset?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = self.api_client.delete_dataset(dataset_id)
                if response.status_code == 204:
                    self.statusBar.showMessage("Dataset deleted successfully")
                    self.load_datasets()
                    
                    # Clear display if deleted current dataset
                    if self.current_dataset == dataset_id:
                        self.current_dataset = None
                        self.summary = None
                        self.records = []
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete dataset")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}")
    
    def download_report(self):
        """Download PDF report for current dataset."""
        if not self.current_dataset:
            QMessageBox.warning(self, "Warning", "Please select a dataset first")
            return
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"equipment_report_{self.current_dataset}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                response = requests.get(
                    self.api_client.get_report_url(self.current_dataset),
                    stream=True
                )
                
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.statusBar.showMessage(f"Report saved to {file_path}")
                    QMessageBox.information(
                        self,
                        "Success",
                        f"PDF report saved successfully!\n\n{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "Error", "Failed to generate report")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Chemical Equipment Parameter Visualizer")
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
