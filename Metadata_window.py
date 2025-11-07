from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
    QScrollArea,
    QWidget,
)
from PIL import Image
from PIL.ExifTags import TAGS


class MetadataEditorDialog(QDialog):
    """
    Dynamic EXIF editor dialog. It discovers existing EXIF entries and
    builds editable fields for text-like values. Updates in-memory data
    without automatically saving to the file.
    """

    def __init__(self, parent, image_path: str):
        super().__init__(parent)
        self.setWindowTitle("Edit EXIF Metadata")
        self.image_path = image_path
        self.parent_window = parent  # Store reference to parent

        self._editors = {}  # tag_id -> (QLineEdit, was_bytes: bool)
        self._build_ui()
        self._load_existing_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Scrollable area for many tags
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.form = QFormLayout(self.container)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self._on_save)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _load_existing_values(self):
        try:
            with Image.open(self.image_path) as img:
                exif = img.getexif()
                if exif:
                    count = 0
                    for tag_id, value in exif.items():
                        # Only edit text-like values (str or bytes)
                        was_bytes = False
                        text_value = None
                        if isinstance(value, bytes):
                            try:
                                text_value = value.decode("utf-8", errors="replace")
                                was_bytes = True
                            except Exception:
                                continue
                        elif isinstance(value, str):
                            text_value = value
                        else:
                            # Skip non-text values for safety
                            continue

                        label = TAGS.get(tag_id, str(tag_id))
                        editor = QLineEdit()
                        editor.setText(text_value)
                        self.form.addRow(label, editor)
                        self._editors[tag_id] = (editor, was_bytes)
                        count += 1

                    if count == 0:
                        self.status_label.setText("No text-like EXIF fields available to edit.")
                else:
                    self.status_label.setText("No EXIF data found.")
        except Exception as e:
            self.status_label.setText(f"Warning: Unable to read EXIF ({e})")

    def _on_save(self):
        """Update the parent's in-memory EXIF data without saving to file."""
        try:
            with Image.open(self.image_path) as img:
                exif = img.getexif() or {}

                # Update exif dictionary with edited values
                for tag_id, (editor, was_bytes) in self._editors.items():
                    text = editor.text()
                    exif[tag_id] = text.encode("utf-8") if was_bytes else text

                # Update parent's _last_exif_data instead of saving to file
                if hasattr(self.parent_window, '_last_exif_data'):
                    self.parent_window._last_exif_data = dict(exif)

            self.accept()
        except Exception as e:
            self.status_label.setText(f"Error updating metadata: {e}")
