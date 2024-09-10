# pylint: disable=consider-using-enumerate
from enum import Enum


class EventType(Enum):
    SPECIAL = 0
    COOP = 1


class Action(Enum):
    COOP = 0
    EXPLOIT = 1
    INACT = 2

    def __str__(self) -> str:
        return super().__str__()[7:]


def prisioners_game(desition1: Action, desition2: Action) -> int:
    if desition1 == Action.COOP and desition2 == Action.COOP:
        return 10
    if desition1 == Action.COOP and desition2 == Action.EXPLOIT:
        return 0
    if desition1 == Action.EXPLOIT and desition2 == Action.COOP:
        return 15
    if desition1 == Action.EXPLOIT and desition2 == Action.EXPLOIT:
        return 0
    return 8


def negative_prisioners_game(desition1: Action, desition2: Action) -> int:
    if desition1 == Action.COOP and desition2 == Action.COOP:
        return -5
    if desition1 == Action.COOP and desition2 == Action.EXPLOIT:
        return -15
    if desition1 == Action.EXPLOIT and desition2 == Action.COOP:
        return 0
    if desition1 == Action.EXPLOIT and desition2 == Action.EXPLOIT:
        return -15
    return -7


def group_prisioners_game(desitions: list[Action], resources: int) -> list[int]:
    if len(desitions) == 1:
        if resources > 0:
            return [resources // (10 / 8)]
        return [resources // (15 / 7)]

    list_result: list[int] = [0] * len(desitions)
    for d1 in range(len(desitions)):
        for d2 in range(len(desitions)):
            if d1 < d2:
                if resources > 0:
                    list_result[d1] += prisioners_game(desitions[d1], desitions[d2])
                else:
                    list_result[d1] += negative_prisioners_game(
                        desitions[d1], desitions[d2]
                    )

    # Calculate the proportion between the total individual points and the total possible points
    if resources > 0:
        list_result = [
            resources * x // (len(desitions) * 10 * (len(desitions) - 1))
            for x in list_result
        ]

    else:
        list_result = [
            resources * x // (len(desitions) * -15 * (len(desitions) - 1))
            for x in list_result
        ]

    return list_result
