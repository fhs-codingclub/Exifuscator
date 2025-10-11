import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QScrollArea, QSplitter, QFrame, QToolBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5 import QtGui
from PIL import Image
from PIL.ExifTags import TAGS
from Metadata_window import MetadataEditorDialog

class ExifMetadataViewer(QMainWindow):
    """
    A simple GUI application for viewing EXIF metadata of images.
    Built with PyQt5 and Pillow for easy customization and extension.
    """
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self._last_exif_data = None
        self.logo_pixmap_original = None  # Cache original logo to avoid reloading
        self.dark_mode = True  # Start in dark mode
        
        # Cache theme icon pixmaps
        self.moon_icon = QPixmap("img/dark mode mod.png")
        self.sun_icon = QPixmap("img/sun light.png")
        self.logo_dark = QPixmap("img/exifuscator_dark.png")
        self.logo_white = QPixmap("img/exifuscator_white.png")
        
        self.init_ui()
        
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("EXIFuscator")
        self.setWindowIcon(QIcon('img/favicon.png'))
        self.setGeometry(100, 100, 1000, 700)

        # Create menu bar first
        self.create_menu_bar()
        
        # Create toolbar with logo and Load Image button
        self.create_toolbar()

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
        
        # Status bar
        self.statusBar().showMessage("Ready - Click 'Load Image' to begin")
    
    def setup_image_panel(self, parent):
        """Setup the left panel for image display."""
        image_frame = QFrame()
        image_frame.setFrameStyle(QFrame.StyledPanel)
        image_layout = QVBoxLayout(image_frame)

        # Image display area with scroll
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #000000; border: 2px dashed #ccc;")
        self.image_label.setMinimumSize(400, 300)

        self.image_scroll.setWidget(self.image_label)
        image_layout.addWidget(self.image_scroll)

        parent.addWidget(image_frame)

    def setup_metadata_panel(self, parent):
        """Setup the right panel for metadata display."""
        metadata_frame = QFrame()
        metadata_frame.setFrameStyle(QFrame.StyledPanel)
        metadata_layout = QVBoxLayout(metadata_frame)
        # Top row with Load Image button aligned to the right
        top_row = QHBoxLayout()
        self.load_button_meta = QPushButton("Load Image")
        self.load_button_meta.clicked.connect(self.load_image)
        top_row.addWidget(self.load_button_meta)
        top_row.setAlignment(Qt.AlignCenter)
        metadata_layout.addLayout(top_row)
        
        # Metadata display area
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setPlainText("Load an image to view its EXIF metadata")
        metadata_layout.addWidget(self.metadata_text)
        
        # Clear metadata button
        self.clear_button = QPushButton("Clear Image")
        self.clear_button.clicked.connect(self.clear_metadata)
        self.clear_button.setEnabled(False)
        metadata_layout.addWidget(self.clear_button)

        # Edit metadata button
        self.edit_button = QPushButton("Edit Metadata")
        self.edit_button.clicked.connect(self.write_metadata)
        self.edit_button.setEnabled(False)
        metadata_layout.addWidget(self.edit_button)
        parent.addWidget(metadata_frame)
    
    def create_toolbar(self):
        """Create toolbar with theme toggles, centered logo, and Load Image button."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        # keep a reference to the toolbar so other methods can query its size
        self.toolbar = toolbar

        # Create a container widget with horizontal layout for centering
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Left spacer
        layout.addStretch(1)

        # Moon icon button (left of logo) - toggles to dark mode
        self.moon_button = QLabel()
        self.moon_button.setPixmap(self.moon_icon.scaledToHeight(70, Qt.SmoothTransformation))
        self.moon_button.setCursor(Qt.PointingHandCursor)
        self.moon_button.setToolTip("Switch to Dark Mode")
        self.moon_button.mousePressEvent = lambda event: self.toggle_theme(True)
        layout.addWidget(self.moon_button)

        # Logo label - load and cache the original pixmap once
        self.logo_label = QLabel()
        # Start with white logo (for dark mode)
        self.logo_pixmap_original = self.logo_white
        
        if not self.logo_pixmap_original.isNull():
            # Initial scaling - will be adjusted on resize
            self.update_logo_size()
        else:
            self.logo_label.setText("EXIFfuscator")
            self.logo_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Sun icon button (right of logo) - toggles to light mode
        self.sun_button = QLabel()
        self.sun_button.setPixmap(self.sun_icon.scaledToHeight(70, Qt.SmoothTransformation))
        self.sun_button.setCursor(Qt.PointingHandCursor)
        self.sun_button.setToolTip("Switch to Light Mode")
        self.sun_button.mousePressEvent = lambda event: self.toggle_theme(False)
        layout.addWidget(self.sun_button)

        # Right spacer
        layout.addStretch(1)

        toolbar.addWidget(container)

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
    
    def toggle_theme(self, to_dark_mode):
        """
        Toggle between light and dark mode.
        
        Args:
            to_dark_mode (bool): True to switch to dark mode, False for light mode
        """
        # Only toggle if we're changing modes
        if self.dark_mode == to_dark_mode:
            return
        
        self.dark_mode = to_dark_mode
        
        # Get the application instance
        app = QApplication.instance()
        
        if self.dark_mode:
            # Apply dark theme
            try:
                import qdarkstyle
                app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            except ImportError:
                # Fallback to a simple dark style if qdarkstyle not available
                app.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                    QTextEdit, QScrollArea {
                        background-color: #1e1e1e;
                        color: #ffffff;
                    }
                """)
            # Use white logo for dark mode
            self.logo_pixmap_original = self.logo_white
        else:
            # Apply light theme (default Qt style)
            app.setStyleSheet("")
            # Use dark logo for light mode
            self.logo_pixmap_original = self.logo_dark
        
        # Update logo display
        self.update_logo_size()
        
        # Update status message
        mode_name = "Dark Mode" if self.dark_mode else "Light Mode"
        self.statusBar().showMessage(f"Switched to {mode_name}")
    
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
            self.edit_button.setEnabled(True)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(file_path)}")
    
    def display_image(self, file_path):
        """Display the selected image in the image panel."""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale image to fit while maintaining aspect ratio
                available = self.image_scroll.viewport().size()
                scaled_pixmap = pixmap.scaled(
                    available,
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
                    self._last_exif_data = dict(exif_data)
                    self.update_metadata_display()
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

       # self.load_button = QPushButton("Load Image")
        #self.load_button.clicked.connect(self.load_image)
        #self.load_button.setMinimumHeight(30)
        #toolbar.addWidget(self.load_button)

    def update_metadata_display(self):
        if self._last_exif_data:
            divider = "=" * int(self.width() * 0.045)
            text = "EXIF Metadata:\n" + divider + "\n\n"
            for tag_id, value in self._last_exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                text += f"{tag_name}: {value}\n"
            print(text)
            self.metadata_text.setPlainText(text)
    

    def write_metadata(self, _=None):
        if not self.current_image_path:
            return
        dlg = MetadataEditorDialog(self, self.current_image_path)
        if dlg.exec_() == dlg.Accepted:
            try:
                with Image.open(self.current_image_path) as image:
                    exif = image.getexif()
                self._last_exif_data = dict(exif) if exif is not None else None
                self.update_metadata_display()
                self.statusBar().showMessage("Metadata saved")
            except Exception:
                pass

    def clear_metadata(self):
        """Clear the metadata display and image."""
        self.metadata_text.setPlainText("Load an image to view its EXIF metadata")
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #ccc;")
        self.current_image_path = None
        self.clear_button.setEnabled(False)
        self.statusBar().showMessage("Ready - Click 'Load Image' to begin")
        self._last_exif_data = None

    def resizeEvent(self, event):
        """Handle window resize events safely."""
        super().resizeEvent(event)
        
        # Update logo size dynamically (safe with cached pixmap)
        self.update_logo_size()
        
        # Update metadata divider if we have data
        if self._last_exif_data:
            self.update_metadata_display()
    
    def update_logo_size(self):
        """
        Update logo size based on toolbar height.
        Adjust MAX_LOGO_HEIGHT and MIN_LOGO_HEIGHT to change logo size.
        """
        # Configuration - easy to edit
        MAX_LOGO_HEIGHT = 200 / 3  # Maximum logo height in pixels
        MIN_LOGO_HEIGHT = 100  # Minimum logo height in pixels
        TOOLBAR_PADDING = 8   # Padding from toolbar edges
        
        # Safety checks
        if not hasattr(self, 'logo_label'):
            return
        if not hasattr(self, 'toolbar'):
            return
        if self.logo_pixmap_original is None or self.logo_pixmap_original.isNull():
            return
        
        try:
            # Calculate logo height based on toolbar size
            toolbar_height = self.toolbar.height()
            logo_height = max(MIN_LOGO_HEIGHT, min(MAX_LOGO_HEIGHT, toolbar_height - TOOLBAR_PADDING))
            
            # Scale the cached pixmap
            scaled = self.logo_pixmap_original.scaledToHeight(logo_height, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        except Exception as e:
            # Silently handle any errors to prevent crashes
            print(f"Logo resize error (non-critical): {e}")
    
    def show_about(self):
        """Show about dialog."""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About EXIFuscator",
            "EXIFbuscator 1.0\n\n"
            "A python GUI program to manage EXIF metadata in images and obfuscate values such as location coordinates and time.\n\n"
            "Made by Angel Juarez, Erik Shaver, and Daniel\n\n"
            "Logo made by @gabrielmaroni on github"
        )


def create_application():
    """Factory function to create and return the application instance."""
    app = QApplication(sys.argv)
    app.setApplicationName("EXIF Metadata Viewer")
    app.setOrganizationName("CipherHacks")
    # Apply dark style if available without making it a hard dependency
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    except Exception:
        pass
    
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