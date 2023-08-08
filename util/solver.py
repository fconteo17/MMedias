# -*- coding: utf-8 -*-
"""Modulo para resolver o problema de otimizacao."""

import os
import json

from pulp import LpProblem, LpMinimize, LpVariable

folder = os.path.dirname(__file__)


def get_funcoes(materia):
    """Retorna a funcao de otimizacao da materia.

    :param materia: str
    :return: str
    """
    with open(os.path.join(folder, 'funcoes.json')) as file:
        funcoes = json.load(file)
    if materia not in funcoes.keys():
        return 'teste'
    return funcoes[materia]


def solve(materias: dict):
    """Resolve o problema de otimizacao.

    :param materias: dict
    :return: dict
    """
    calculos = {}
    for materia, notas in materias.items():
        notas = format_notas(notas)

        prob = LpProblem("Nota", LpMinimize)

        for key in ['p1', 'p2', 'p3', 'p4', 't1', 't2', 't3', 't4', 't5', 't6',
                    't7', 't8', 't9', 't10', 't11', 't12', 't13', 't14', 't15', 't16']:
            if key in notas:
                globals()[key] = LpVariable(key, notas[key][0], notas[key][1])
            else:
                globals()[key] = LpVariable(key, 0, 9)

        funcao = eval(get_funcoes(materia))
        prob += funcao, "Nota Final"
        prob += funcao >= 6, "Calculo da nota final"

        prob.solve()

        calculo = {}
        for variable in prob.variables():
            calculo[variable.name] = [f'{variable.varValue:.2f}', notas[variable.name][2]]
        calculos[materia] = calculo
    return calculos


def format_notas(notas):
    """Formata as notas para o formato [min, max, peso]
    :param notas: dict
    :return: dict
    """
    for tipo, nota in notas.items():
        if isinstance(nota, list):
            if nota[1] == 0:
                nota = [0, 9, 0]
            else:
                nota = [float(nota[0]), float(nota[0]), 1]
        else:
            if nota == '':
                nota = [0, 9, 0]
            else:
                nota = [float(nota), float(nota), 1]
        notas[tipo] = nota
    return notas
