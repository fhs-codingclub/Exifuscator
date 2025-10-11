from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
)
from PIL import Image


class MetadataEditorDialog(QDialog):
    """
    Simple EXIF editor dialog for a handful of common text fields.
    Saves back to the same file using Pillow's EXIF API.
    """

    # Common EXIF tag IDs for textual data
    TAG_IMAGE_DESCRIPTION = 270
    TAG_ARTIST = 315
    TAG_COPYRIGHT = 33432
    TAG_USER_COMMENT = 37510

    def __init__(self, parent, image_path: str):
        super().__init__(parent)
        self.setWindowTitle("Edit EXIF Metadata")
        self.image_path = image_path

        self._build_ui()
        self._load_existing_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.form = QFormLayout()
        self.input_description = QLineEdit()
        self.input_artist = QLineEdit()
        self.input_copyright = QLineEdit()
        self.input_comment = QLineEdit()

        self.form.addRow("Description", self.input_description)
        self.form.addRow("Artist", self.input_artist)
        self.form.addRow("Copyright", self.input_copyright)
        self.form.addRow("User Comment", self.input_comment)
        layout.addLayout(self.form)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self._on_save)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _load_existing_values(self):
        try:
            with Image.open(self.image_path) as img:
                exif = img.getexif()
                if exif:
                    self.input_description.setText(str(exif.get(self.TAG_IMAGE_DESCRIPTION, "")))
                    self.input_artist.setText(str(exif.get(self.TAG_ARTIST, "")))
                    self.input_copyright.setText(str(exif.get(self.TAG_COPYRIGHT, "")))
                    self.input_comment.setText(str(exif.get(self.TAG_USER_COMMENT, "")))
        except Exception as e:
            self.status_label.setText(f"Warning: Unable to read EXIF ({e})")

    def _on_save(self):
        try:
            with Image.open(self.image_path) as img:
                exif = img.getexif() or {}

                # Update only if non-empty; allow clearing by setting empty text
                exif[self.TAG_IMAGE_DESCRIPTION] = self.input_description.text()
                exif[self.TAG_ARTIST] = self.input_artist.text()
                exif[self.TAG_COPYRIGHT] = self.input_copyright.text()
                exif[self.TAG_USER_COMMENT] = self.input_comment.text()

                # Save back with updated EXIF
                img.save(self.image_path, exif=exif)

            self.accept()
        except Exception as e:
            self.status_label.setText(f"Error saving metadata: {e}")
