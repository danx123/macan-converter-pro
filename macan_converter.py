import sys, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QTabWidget, QComboBox, QLineEdit, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer

class MacanConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Converter Pro 🧿")
        self.setGeometry(100, 100, 600, 400)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.pdf_tab(), "PDF → Image")
        self.tabs.addTab(self.html_tab(), "HTML → Image")
        self.tabs.addTab(self.ico_tab(), "PNG → ICO")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    # PDF → Image Tab
    def pdf_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.pdf_path = QLineEdit()
        browse_btn = QPushButton("Browse PDF")
        browse_btn.clicked.connect(self.load_pdf)

        self.pdf_format = QComboBox()
        self.pdf_format.addItems(["png", "jpg"])

        self.pdf_output = QLineEdit()
        out_btn = QPushButton("Output Folder")
        out_btn.clicked.connect(self.select_output_folder)

        convert_btn = QPushButton("Convert PDF")
        convert_btn.clicked.connect(self.convert_pdf)

        layout.addWidget(QLabel("PDF File:"))
        layout.addWidget(self.pdf_path)
        layout.addWidget(browse_btn)
        layout.addWidget(QLabel("Format:"))
        layout.addWidget(self.pdf_format)
        layout.addWidget(QLabel("Output Folder:"))
        layout.addWidget(self.pdf_output)
        layout.addWidget(out_btn)
        layout.addWidget(convert_btn)
        tab.setLayout(layout)
        return tab

    def load_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file:
            self.pdf_path.setText(file)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.pdf_output.setText(folder)

    def convert_pdf(self):
        doc = QPdfDocument()
        doc.load(self.pdf_path.text())
        fmt = self.pdf_format.currentText()
        out_dir = self.pdf_output.text()

        for page in range(doc.pageCount()):
            image = QImage(1200, 1600, QImage.Format.Format_ARGB32)
            image.fill(0xFFFFFFFF)
            painter = QPainter(image)
            doc.render(painter, page)
            painter.end()
            out_path = os.path.join(out_dir, f"page_{page+1}.{fmt}")
            image.save(out_path)

    # HTML → Image Tab
    def html_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.html_path = QLineEdit()
        browse_btn = QPushButton("Browse HTML")
        browse_btn.clicked.connect(self.load_html)

        self.html_format = QComboBox()
        self.html_format.addItems(["png", "jpg"])

        self.html_output = QLineEdit()
        out_btn = QPushButton("Output Path")
        out_btn.clicked.connect(self.select_html_output)

        convert_btn = QPushButton("Convert HTML")
        convert_btn.clicked.connect(self.convert_html)

        layout.addWidget(QLabel("HTML File:"))
        layout.addWidget(self.html_path)
        layout.addWidget(browse_btn)
        layout.addWidget(QLabel("Format:"))
        layout.addWidget(self.html_format)
        layout.addWidget(QLabel("Output Path:"))
        layout.addWidget(self.html_output)
        layout.addWidget(out_btn)
        layout.addWidget(convert_btn)
        tab.setLayout(layout)
        return tab

    def load_html(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select HTML", "", "HTML Files (*.html *.htm)")
        if file:
            self.html_path.setText(file)

    def select_html_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg)")
        if file:
            self.html_output.setText(file)

    def convert_html(self):
        view = QWebEngineView()
        html = open(self.html_path.text(), encoding="utf-8").read()
        view.setHtml(html)

        def capture():
            pixmap = view.grab()
            pixmap.save(self.html_output.text())
            QApplication.quit()

        QTimer.singleShot(2000, capture)
        view.show()
        QApplication.exec()

    # PNG → ICO Tab
    def ico_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.png_path = QLineEdit()
        browse_btn = QPushButton("Browse PNG")
        browse_btn.clicked.connect(self.load_png)

        self.ico_size = QComboBox()
        self.ico_size.addItems(["16", "32", "64", "128", "256"])

        self.ico_output = QLineEdit()
        out_btn = QPushButton("Save ICO")
        out_btn.clicked.connect(self.select_ico_output)

        convert_btn = QPushButton("Convert to ICO")
        convert_btn.clicked.connect(self.convert_ico)

        layout.addWidget(QLabel("PNG File:"))
        layout.addWidget(self.png_path)
        layout.addWidget(browse_btn)
        layout.addWidget(QLabel("ICO Size:"))
        layout.addWidget(self.ico_size)
        layout.addWidget(QLabel("Output Path:"))
        layout.addWidget(self.ico_output)
        layout.addWidget(out_btn)
        layout.addWidget(convert_btn)
        tab.setLayout(layout)
        return tab

    def load_png(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PNG", "", "PNG Files (*.png)")
        if file:
            self.png_path.setText(file)

    def select_ico_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save ICO", "", "ICO Files (*.ico)")
        if file:
            self.ico_output.setText(file)

    def convert_ico(self):
        pixmap = QPixmap(self.png_path.text())
        size = int(self.ico_size.currentText())
        icon = pixmap.scaled(size, size)
        icon.save(self.ico_output.text(), "ICO")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacanConverterApp()
    window.show()
    sys.exit(app.exec())