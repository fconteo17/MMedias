from pulp import LpProblem, LpMinimize, LpVariable
import os
import json

folder = os.path.dirname(__file__)


def get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16):
    f = open(os.path.join(folder, 'funcoes.json'))
    funcoes = json.load(f)
    if materia not in funcoes.keys():
        return (t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9 + t10 + t11 + t12 + t13 + t14 + t15 + t16 + p1 + p2 + p3 + p4)/20
    return eval(funcoes[materia])


def solve(materias: dict):
    calculos = {}
    for materia, notas in materias.items():
        notas = format_notas(notas)

        prob = LpProblem("Nota", LpMinimize)

        variables = {}
        for key in ['P1', 'P2', 'P3', 'P4', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', 'T13', 'T14', 'T15', 'T16']:
            if key in notas:
                variables[key] = LpVariable(key, notas[key][0], notas[key][1])
            else:
                variables[key] = LpVariable(key, 0, 10)

        p1 = variables['P1']
        p2 = variables['P2']
        p3 = variables['P3']
        p4 = variables['P4']
        t1 = variables['T1']
        t2 = variables['T2']
        t3 = variables['T3']
        t4 = variables['T4']
        t5 = variables['T5']
        t6 = variables['T6']
        t7 = variables['T7']
        t8 = variables['T8']
        t9 = variables['T9']
        t10 = variables['T10']
        t11 = variables['T11']
        t12 = variables['T12']
        t13 = variables['T13']
        t14 = variables['T14']
        t15 = variables['T15']
        t16 = variables['T16']

        prob += get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16), "Nota Final"

        prob += get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16) >= 6, "Calculo da nota final"

        prob.solve()

        calculo = {}
        for v in prob.variables():
            calculo[v.name] = ['%.2f' % v.varValue, notas[v.name][2]]
        calculos[materia] = calculo
    return calculos


def format_notas(notas):
    for tipo, nota in notas.items():
        if type(nota) is list:
            if nota[1] == 0:
                nota = [0, 10, 0]
            else:
                nota = [float(nota[0]), float(nota[0]), 1]
        else:
            if nota == '':
                nota = [0, 10, 0]
            else:
                nota = [float(nota), float(nota), 1]
        notas[tipo] = nota
    return notas
