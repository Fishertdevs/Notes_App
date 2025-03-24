"""
Aplicación de Notas
Autor: Harry Fishert
GitHub: https://github.com/Fishertdevs
Descripción: Una aplicación para gestionar notas con soporte para adjuntar y visualizar archivos.
"""
import csv 
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget, QTextEdit,
    QLineEdit, QMessageBox, QWidget, QLabel, QHBoxLayout, QInputDialog , QFileDialog, QDialog, QVBoxLayout
)
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap
import pandas as pd  # Necesario para manejar archivos de Excel

class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicación de Notas Mejorada")
        self.setGeometry(100, 100, 800, 500)

        # Estilo de colores
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)

        # Lista de notas en memoria
        self.notes = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Título de la aplicación
        self.title_label = QLabel("Gestor de Notas")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self.layout.addWidget(self.title_label)

        # Lista de notas
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.view_note)
        self.layout.addWidget(self.list_widget)

        # Entrada de título y contenido
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Título de la nota")
        self.layout.addWidget(self.title_input)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Contenido de la nota")
        self.layout.addWidget(self.content_input)

        # Botones
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Añadir Nota")
        self.add_button.clicked.connect(self.add_note)
        self.button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Editar Nota")
        self.edit_button.clicked.connect(self.edit_note)
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Eliminar Nota")
        self.delete_button.clicked.connect(self.delete_note)
        self.button_layout.addWidget(self.delete_button)

        self.attach_button = QPushButton("Adjuntar Archivo")
        self.attach_button.clicked.connect(self.attach_file)
        self.button_layout.addWidget(self.attach_button)

        self.download_button = QPushButton("Descargar Nota")
        self.download_button.clicked.connect(self.download_note)
        self.button_layout.addWidget(self.download_button)

        self.layout.addLayout(self.button_layout)

        # Animación de entrada
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)
        self.animation.setStartValue(QRect(100, 100, 0, 0))
        self.animation.setEndValue(QRect(100, 100, 800, 500))
        self.animation.start()

    def load_notes_to_list(self):
        self.list_widget.clear()
        for note in self.notes:
            self.list_widget.addItem(note["title"])

    def add_note(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        if not title or not content:
            QMessageBox.warning(self, "Error", "El título y el contenido no pueden estar vacíos.")
            return
        self.notes.append({"title": title, "content": content, "attachment": None})
        self.load_notes_to_list()
        self.title_input.clear()
        self.content_input.clear()
        QMessageBox.information(self, "Éxito", "Nota añadida con éxito.")

    def view_note(self, item):
        selected_index = self.list_widget.currentRow()
        if selected_index >= 0:
            note = self.notes[selected_index]
            attachment = note.get("attachment", None)
            if attachment:
                self.display_attachment(attachment)
            else:
                QMessageBox.information(self, note["title"], note["content"])

    def display_attachment(self, file_path):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            self.display_image(file_path)
        elif file_path.lower().endswith(('.xls', '.xlsx')):
            self.display_excel(file_path)
        else:
            QMessageBox.warning(self, "Error", "No se puede visualizar este tipo de archivo.")

    def display_image(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("Vista previa de la imagen")
        layout = QVBoxLayout(dialog)
        label = QLabel(dialog)
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap.scaled(600, 400, aspectRatioMode=1))
        layout.addWidget(label)
        dialog.exec_()

    def display_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            content = df.to_string()
            dialog = QDialog(self)
            dialog.setWindowTitle("Vista previa del archivo Excel")
            layout = QVBoxLayout(dialog)
            text_edit = QTextEdit(dialog)
            text_edit.setText(content)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo leer el archivo Excel: {e}")

    def edit_note(self):
        selected_index = self.list_widget.currentRow()
        if selected_index >= 0:
            note = self.notes[selected_index]
            new_title, ok_title = QInputDialog.getText(self, "Editar Título", "Nuevo título:", text=note["title"])
            new_content, ok_content = QInputDialog.getMultiLineText(self, "Editar Contenido", "Nuevo contenido:", text=note["content"])
            if ok_title and ok_content:
                self.notes[selected_index]["title"] = new_title
                self.notes[selected_index]["content"] = new_content
                self.load_notes_to_list()
                QMessageBox.information(self, "Éxito", "Nota editada con éxito.")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una nota para editar.")

    def delete_note(self):
        selected_index = self.list_widget.currentRow()
        if selected_index >= 0:
            confirm = QMessageBox.question(self, "Confirmar", "¿Estás seguro de que deseas eliminar esta nota?")
            if confirm == QMessageBox.Yes:
                self.notes.pop(selected_index)
                self.load_notes_to_list()
                QMessageBox.information(self, "Éxito", "Nota eliminada con éxito.")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una nota para eliminar.")

    def attach_file(self):
        selected_index = self.list_widget.currentRow()
        if selected_index >= 0:
            file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
            if file_path:
                self.notes[selected_index]["attachment"] = file_path
                QMessageBox.information(self, "Éxito", "Archivo adjuntado con éxito.")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una nota para adjuntar un archivo.")

    def download_note(self):
        selected_index = self.list_widget.currentRow()
        if selected_index >= 0:
            note = self.notes[selected_index]
            file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Nota", f"{note['title']}.txt", "Archivos de Texto (*.txt)")
            if file_path:
                with open(file_path, "w") as file:
                    file.write(f"Título: {note['title']}\n\nContenido:\n{note['content']}")
                QMessageBox.information(self, "Éxito", "Nota descargada con éxito.")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una nota para descargar.")

def main():
    app = QApplication([])
    window = NotesApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()