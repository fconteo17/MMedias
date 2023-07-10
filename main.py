import json
import logging
import os
import sys
import time
from threading import Thread

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QMessageBox

from telas import tela_notas, tela_inicial
from util.mauanet import get_notas
from util.solver import solve

folder = os.path.dirname(__file__)

threads = []


class Controller:
    def __init__(self):
        self._translate = QtCore.QCoreApplication.translate
        self.materias = {}
        self.saved_grades = {}
        self.is_shown = False

        self.tela_inicial_window = QtWidgets.QMainWindow()
        self.tela_inicial_ui = tela_inicial.Ui_Dialog()
        self.tela_inicial_ui.setupUi(self.tela_inicial_window)

        self.tela_notas_window = QtWidgets.QMainWindow()
        self.tela_notas_ui = tela_notas.Ui_Dialog()
        self.tela_notas_ui.setupUi(self.tela_notas_window)
        self.tela_notas_ui.provas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tela_notas_ui.trabalhos.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.tela_inicial_ui.btn_login.clicked.connect(self.login)
        self.tela_notas_ui.provas.itemChanged.connect(self.update_notas_prova)
        self.tela_notas_ui.trabalhos.itemChanged.connect(self.update_notas_trabalho)
        self.tela_notas_ui.recalcular.clicked.connect(self.recalcular)

    def show_tela_inicial(self):
        self.tela_inicial_window.show()

    def login(self):
        self.tela_inicial_ui.btn_login.setText(self._translate("Dialog", "Buscando Notas"))
        f = open(os.path.join(folder, 'saved_grades.json'))
        self.saved_grades = json.load(f)
        f.close()
        if self.tela_inicial_ui.login.text() in self.saved_grades:
            self.show_popup()
        else:
            self.materias = get_notas(self.tela_inicial_ui.login.text(), self.tela_inicial_ui.senha.text())
        self.tela_inicial_window.close()
        self.tela_notas_window.show()
        self.load_data(self.materias)

    def show_popup(self):
        msg = QMessageBox()
        msg.setText("Gostaria de atualizar as notas?")
        msg.addButton('Sim', QMessageBox.ButtonRole.YesRole)
        msg.addButton('Não', QMessageBox.ButtonRole.NoRole)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.buttonClicked.connect(self.popup_button)
        x = msg.exec()

    def popup_button(self, btn):
        if btn.text() == 'Sim':
            self.materias = get_notas(self.tela_inicial_ui.login.text(), self.tela_inicial_ui.senha.text())
        else:
            self.materias = self.saved_grades[self.tela_inicial_ui.login.text()]

    def load_data(self, materias):
        self.tela_notas_ui.provas.setRowCount(len(materias))
        self.tela_notas_ui.trabalhos.setRowCount(len(materias))
        row = 0
        for materia, notas in materias.items():
            for table, keys in [(self.tela_notas_ui.provas, ['P1', 'P2', 'P3', 'P4']),
                                (self.tela_notas_ui.trabalhos, ['T1', 'T2', 'T3', 'T4'])]:
                for i, key in enumerate(keys):
                    item = QtWidgets.QTableWidgetItem(str(notas.get(key, [''])[0]))
                    if key in notas and notas[key][1] == 0:
                        item.setBackground(QColor(133, 226, 255))
                    elif key not in notas:
                        item.setBackground(QColor(66, 66, 66))
                    table.setItem(row, i + 1, item)

            self.tela_notas_ui.provas.setItem(row, 0, QtWidgets.QTableWidgetItem(materia))
            self.tela_notas_ui.trabalhos.setItem(row, 0, QtWidgets.QTableWidgetItem(materia))

            row += 1
        self.is_shown = True

    def update_notas_prova(self, item):
        if self.is_shown:
            materia = self.tela_notas_ui.provas.item(item.row(), 0).text()
            nota = self.tela_notas_ui.provas.horizontalHeaderItem(item.column()).text()
            self.materias[materia][nota] = [item.text(), 1]

    def update_notas_trabalho(self, item):
        if self.is_shown:
            materia = self.tela_notas_ui.trabalhos.item(item.row(), 0).text()
            nota = self.tela_notas_ui.trabalhos.horizontalHeaderItem(item.column()).text()
            self.materias[materia][nota] = [item.text(), 1]

    def recalcular(self):
        self.is_shown = False
        self.materias = solve(self.materias)
        self.load_data(self.materias)
        self.is_shown = True


if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.show_tela_inicial()
    sys.exit(app.exec())
