import json
import logging
import os
import sys

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QMessageBox

from telas import tela_notas, tela_inicial
from util.mauanet import get_notas
from util.solver import solve

SAVED_GRADES = os.path.join(os.path.dirname(__file__), 'saved_grades.json')


def get_max_t(materias):
    max_t = 0
    for materia, notas in materias.items():
        for key in notas.keys():
            if key[0] == 'T':
                valor = int(key[1:])
                if valor > max_t:
                    max_t = valor
    return max_t


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
        self.tela_notas_ui.provas.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.tela_notas_ui.trabalhos.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.tela_inicial_ui.btn_login.clicked.connect(self.login)
        self.tela_notas_ui.provas.itemChanged.connect(self.update_notas_prova)
        self.tela_notas_ui.trabalhos.itemChanged.connect(self.update_notas_trabalho)
        self.tela_notas_ui.recalcular.clicked.connect(self.recalcular)

    def show_tela_inicial(self):
        self.tela_inicial_window.show()

    def close_tela_inicial(self):
        self.tela_inicial_window.close()

    def show_tela_notas(self):
        self.tela_notas_window.show()

    def login(self):
        self.tela_inicial_ui.btn_login.setText(self._translate("Dialog", "Buscando notas..."))
        if not os.path.exists(SAVED_GRADES):
            f = open(SAVED_GRADES, 'w')
            f.write('{}')
            f.close()
        f = open(SAVED_GRADES)
        self.saved_grades = json.load(f)
        f.close()
        if self.tela_inicial_ui.login.text() in self.saved_grades:
            self.show_popup()
        else:
            self.materias = get_notas(
                self.tela_inicial_ui.login.text(), self.tela_inicial_ui.senha.text()
            )
            self.save_grades()
        self.close_tela_inicial()
        self.show_tela_notas()
        self.load_data(self.materias)

    def show_popup(self):
        msg = QMessageBox()
        msg.setText("Gostaria de atualizar as notas?")
        msg.addButton('Sim', QMessageBox.ButtonRole.YesRole)
        msg.addButton('Não', QMessageBox.ButtonRole.NoRole)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.buttonClicked.connect(self.popup_button)
        msg.exec()

    def popup_button(self, btn):
        if btn.text() == 'Sim':
            self.materias = get_notas(
                self.tela_inicial_ui.login.text(), self.tela_inicial_ui.senha.text()
            )
            self.save_grades()
        else:
            self.materias = self.saved_grades[self.tela_inicial_ui.login.text()]

    def load_data(self, materias):
        self.tela_notas_ui.provas.setRowCount(len(materias))
        self.tela_notas_ui.trabalhos.setRowCount(len(materias))
        row = 0
        for materia, notas in materias.items():
            for table, keys in [(self.tela_notas_ui.provas, ['P1', 'P2', 'P3', 'P4']),
                                (self.tela_notas_ui.trabalhos, [
                                    'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8',
                                    'T9', 'T10', 'T11', 'T12', 'T13', 'T14', 'T15', 'T16'
                                ])]:
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
        max_t = get_max_t(materias)
        for i in range(max_t + 1, self.tela_notas_ui.trabalhos.columnCount()):
            self.tela_notas_ui.trabalhos.removeColumn(max_t + 1)
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

    def save_grades(self):
        self.saved_grades[self.tela_inicial_ui.login.text()] = self.materias
        json_object = json.dumps(self.saved_grades, ensure_ascii=False)
        with open(SAVED_GRADES, "w") as outfile:
            outfile.write(json_object)


if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.show_tela_inicial()
    sys.exit(app.exec())
