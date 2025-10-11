import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QScrollArea, QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PIL import Image
from PIL.ExifTags import TAGS


class ExifMetadataViewer(QMainWindow):
    """
    A simple GUI application for viewing EXIF metadata of images.
    Built with PyQt5 and Pillow for easy customization and extension.
    """
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("EXIF Metadata Viewer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        central_widget.setLayout(QHBoxLayout())
        central_widget.layout().addWidget(main_splitter)
        
        # Left panel for image display
        self.setup_image_panel(main_splitter)
        
        # Right panel for metadata display
        self.setup_metadata_panel(main_splitter)
        
        # Set splitter proportions (60% image, 40% metadata)
        main_splitter.setSizes([600, 400])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Ready - Click 'Load Image' to begin")
    
    def setup_image_panel(self, parent):
        """Setup the left panel for image display."""
        image_frame = QFrame()
        image_frame.setFrameStyle(QFrame.StyledPanel)
        image_layout = QVBoxLayout(image_frame)
        
        # Load image button
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMinimumHeight(40)
        image_layout.addWidget(self.load_button)
        
        # Image display area with scroll
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #ccc;")
        self.image_label.setMinimumSize(400, 300)
        
        self.image_scroll.setWidget(self.image_label)
        image_layout.addWidget(self.image_scroll)
        
        parent.addWidget(image_frame)
    
    def setup_metadata_panel(self, parent):
        """Setup the right panel for metadata display."""
        metadata_frame = QFrame()
        metadata_frame.setFrameStyle(QFrame.StyledPanel)
        metadata_layout = QVBoxLayout(metadata_frame)
        
        # Metadata title
        metadata_title = QLabel("EXIF Metadata")
        metadata_title.setFont(QFont("Arial", 12, QFont.Bold))
        metadata_title.setAlignment(Qt.AlignCenter)
        metadata_layout.addWidget(metadata_title)
        
        # Metadata display area
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setPlainText("Load an image to view its EXIF metadata")
        metadata_layout.addWidget(self.metadata_text)
        
        # Clear metadata button
        self.clear_button = QPushButton("Clear Metadata")
        self.clear_button.clicked.connect(self.clear_metadata)
        self.clear_button.setEnabled(False)
        metadata_layout.addWidget(self.clear_button)
        
        parent.addWidget(metadata_frame)
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Load action
        load_action = file_menu.addAction('Load Image')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_image)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction('Exit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
    
    def load_image(self):
        """Load and display an image, then extract its EXIF metadata."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.extract_and_display_metadata(file_path)
            self.clear_button.setEnabled(True)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(file_path)}")
    
    def display_image(self, file_path):
        """Display the selected image in the image panel."""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale image to fit while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.image_scroll.size() - self.image_scroll.frameSize(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet("")  # Remove placeholder styling
            else:
                self.image_label.setText("Failed to load image")
                self.statusBar().showMessage("Error: Failed to load image")
        except Exception as e:
            self.image_label.setText(f"Error loading image: {str(e)}")
            self.statusBar().showMessage("Error loading image")
    
    def extract_and_display_metadata(self, file_path):
        """Extract and display EXIF metadata from the image."""
        try:
            # Open image with Pillow
            with Image.open(file_path) as image:
                exif_data = image.getexif()
                
                print(exif_data)  # Debug: print raw EXIF data to console

                if exif_data is not None:
                    metadata_text = "EXIF Metadata:\n" + "="*50 + "\n\n"


                    # Convert EXIF data to readable format
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        metadata_text += f"{tag_name}: {value}\n"
                    
                    self.metadata_text.setPlainText(metadata_text)
                else:
                    self.metadata_text.setPlainText("No EXIF metadata found in this image.")
                    
        except Exception as e:
            error_message = f"Error reading EXIF data: {str(e)}\n\n"
            error_message += "This could be due to:\n"
            error_message += "- Unsupported image format\n"
            error_message += "- Corrupted image file\n"
            error_message += "- Image has no EXIF data"
            self.metadata_text.setPlainText(error_message)
            self.statusBar().showMessage("Error reading EXIF data")
    
    def clear_metadata(self):
        """Clear the metadata display and image."""
        self.metadata_text.setPlainText("Load an image to view its EXIF metadata")
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #ccc;")
        self.current_image_path = None
        self.clear_button.setEnabled(False)
        self.statusBar().showMessage("Ready - Click 'Load Image' to begin")
    
    def show_about(self):
        """Show about dialog."""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About EXIF Metadata Viewer",
            "EXIF Metadata Viewer v1.0\n\n"
            "A simple application for viewing image EXIF metadata.\n"
            "Built with PyQt5 and Pillow.\n\n"
            "Load an image to view its embedded metadata."
        )


def create_application():
    """Factory function to create and return the application instance."""
    app = QApplication(sys.argv)
    app.setApplicationName("EXIF Metadata Viewer")
    app.setOrganizationName("CipherHacks")
    
    viewer = ExifMetadataViewer()
    return app, viewer


def main():
    """Main entry point for the application."""
    app, viewer = create_application()
    viewer.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()