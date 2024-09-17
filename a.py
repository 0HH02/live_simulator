import random
from numpy.random import poisson

agents2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
matrix = {
    #     1     2     3     4     5      6     7     8      9
    1: [0.50, 0.34, 0.54, 0.26, 0.72, 0.234, 0.2345, 0.2, 0.50, 0.50],
    2: [0.0, 0.50, 0.0, 0.98, 0.78, 0.67, 0.8, 0.8, 0.67, 0.98],
    3: [0.50, 0.50, 0.87, 0.98, 0.897, 0.50, 0.4, 0.23, 0.54, 0.50],
    4: [0.50, 0.356, 0.50, 0.50, 0.39, 0.50, 0.50, 0.50, 0.3, 0.50],
    5: [0.50, 0.50, 0.539, 0.50, 0.50, 0.96, 0.50, 0.50, 0.50, 0.50],
    6: [0.50, 0.96, 0.50, 0.50, 0.50, 0.50, 0.50, 0.69, 0.50, 0.50],
    7: [0.50, 0.50, 0.50, 0.536, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
    8: [0.50, 0.50, 0.35, 0.50, 0.65, 0.50, 0.50, 0.50, 0.50, 0.50],
    9: [0.50, 0.50, 0.50, 0.50, 0.35, 0.50, 0.635, 0.96, 0.50, 0.50],
    10: [0.50, 0.95, 0.50, 0.5350, 0.50, 0.50, 0.54, 0.50, 0.50, 0.50],
}


def ordenar_por_posiciones(array: list[int]) -> list[int]:
    arr: list[int] = array.copy()
    # Paso 2: Crear una lista de pares (valor, índice)
    pares: list[tuple[int, int]] = [(valor, indice) for indice, valor in enumerate(arr)]

    # Paso 3: Ordenar la lista de pares en orden descendente por el valor
    pares_ordenados: list[tuple[int, int]] = sorted(
        pares, key=lambda x: x[0], reverse=True
    )

    # Paso 4: Extraer los índices ordenados
    indices_ordenados: list[int] = [par[1] for par in pares_ordenados]

    # Paso 5: Devolver los índices ordenados
    return indices_ordenados


agents: list[int] = agents2.copy()
random.shuffle(agents)
result: list[list[int]] = []
while agents:
    rand: int = poisson(lam=5)
    group = []
    group.append(agents[0])
    indices_ordenados: list[int] = ordenar_por_posiciones(matrix[agents[0]])
    for i in range(len(indices_ordenados)):
        if rand == 0:
            break
        for roommate in group:
            if not (
                indices_ordenados[i] + 1 != roommate
                and indices_ordenados[i] + 1 in agents
                and random.random() < matrix[roommate][indices_ordenados[i]]
            ):
                break
        else:
            group.append(indices_ordenados[i] + 1)
            agents.remove(indices_ordenados[i] + 1)
            rand -= 1

    result.append(group)
    agents.remove(agents[0])

print(result)
