from pulp import *


def get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8):
    f = open('util/funcoes.json')
    funcoes = json.load(f)
    if materia not in funcoes.keys():
        return 0.125 * t1 + 0.125 * t2 + 0.125 * t3 + 0.125 * t4 + 0.125 * p1 + 0.125 * p2 + 0.125 * p3 + 0.125 * p4
    return eval(funcoes[materia])


def solve(materias: dict):
    calculos = {}
    for materia, notas in materias.items():
        for tipo, nota in notas.items():
            if nota in ['', 'NC', 'NE']:
                if tipo[0] == 'P':
                    nota = [0, 8, 0]
                else:
                    nota = [0, 9, 0]
            else:
                nota = [float(nota), float(nota), 1]
            notas[tipo] = nota

        prob = LpProblem("Nota", LpMinimize)
        p1 = LpVariable("P1", notas['P1'][0], notas['P1'][1])
        p2 = LpVariable("P2", notas['P2'][0], notas['P2'][1])
        p3 = LpVariable("P3", notas['P3'][0], notas['P3'][1])
        p4 = LpVariable("P4", notas['P4'][0], notas['P4'][1])
        t1 = LpVariable("T1", notas['T1'][0], notas['T1'][1])
        t2 = LpVariable("T2", notas['T2'][0], notas['T2'][1])
        t3 = LpVariable("T3", notas['T3'][0], notas['T3'][1])
        t4 = LpVariable("T4", notas['T4'][0], notas['T4'][1])
        t5 = LpVariable("T5", notas['T5'][0], notas['T5'][1])
        t6 = LpVariable("T6", notas['T6'][0], notas['T6'][1])
        t7 = LpVariable("T7", notas['T7'][0], notas['T7'][1])
        t8 = LpVariable("T8", notas['T8'][0], notas['T8'][1])

        prob += get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8), "Nota Final"

        prob += get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8) >= 6, "Calculo da nota final"

        prob.solve()

        calculo = {}
        for v in prob.variables():
            calculo[v.name] = ['%.2f' % v.varValue, notas[v.name][2]]
        calculos[materia] = calculo
    return calculos


def resolve(materias):
    calculos = {}
    for materia, notas in materias.items():
        for tipo, nota in notas.items():
            if nota[1] == 0:
                if tipo[0] == 'P':
                    nota = [0, 8, 0]
                else:
                    nota = [0, 9, 0]
            else:
                nota = [float(nota[0]), float(nota[0]), 1]
            notas[tipo] = nota

        prob = LpProblem("Nota", LpMinimize)

        variables = {}

        for key in ['P1', 'P2', 'P3', 'P4', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']:
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

        prob += get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8), "Nota Final"

        prob += get_funcoes(materia, p1, p2, p3, p4, t1, t2, t3, t4, t5, t6, t7, t8) >= 6, "Calculo da nota final"

        prob.solve()

        calculo = {}
        for v in prob.variables():
            calculo[v.name] = ['%.2f' % v.varValue, notas[v.name][2]]
        calculos[materia] = calculo

    return calculos
