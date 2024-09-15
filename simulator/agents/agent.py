"""
This module contains the abstract class Agent and the basic implementation of it.
"""

from abc import ABC, abstractmethod
import random
from numpy.random import poisson


from enviroment_info import EnviromentInfo, Event
from utils import Action
from event_generator import EventInfo
from utils import group_prisioners_game


class Agent(ABC):
    """
    Abstract base class for defining an agent in the simulator.
    """

    agent_id: int

    @abstractmethod
    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        """
        Perform a passive action based on the given environment information.

        Args:
            enviroment_info (EnviromentInfo): The information about the current environment.

        Returns:
            None
        """

    @abstractmethod
    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        """
        Perform an active action based on the given environment information and event.

        Args:
            enviroment_info (EnviromentInfo): The information about the current environment.
            event (Event): The event triggering the active action.

        Returns:
            Action: The action to be taken by the agent.
        """

    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        return self.__str__()


class RandomAgent(Agent):
    """
    This class represents an agent that takes random actions.
    """

    def __init__(self, id) -> None:
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        pass

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        return random.choice(list(Action))


class PusilanimeAgent(Agent):
    """
    This class represents an agent that always cooperates.
    """

    def __init__(self, id) -> None:
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        pass

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        return Action.COOP


class ThiefAgent(Agent):
    """
    This class represent an agent that always exploits.
    """

    def __init__(self, id) -> None:
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        pass

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        return Action.EXPLOIT


class TipForTapAgent(Agent):
    def __init__(self, id) -> None:
        self.decitions: dict[int, Action] = {}
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        for agent, action in decitions.items():
            self.decitions[agent] = action

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        coop_actions = 0
        exploit_actions = 0
        inact_actions = 0
        for agent in event.group:
            if agent not in self.decitions:
                coop_actions += 1
            elif self.decitions[agent] == Action.COOP:
                coop_actions += 1
            elif self.decitions[agent] == Action.EXPLOIT:
                exploit_actions += 1
            else:
                inact_actions += 1
        if coop_actions > exploit_actions and coop_actions > inact_actions:
            return Action.COOP
        elif exploit_actions > inact_actions:
            return Action.EXPLOIT
        else:
            return Action.INACT


class TipForTapSecureAgent(Agent):
    def __init__(self, id) -> None:
        self.decitions: dict[int, Action] = {}
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        for agent, action in decitions.items():
            self.decitions[agent] = action

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        coop_actions = 0
        exploit_actions = 0
        inact_actions = 0
        for agent in event.group:
            if agent not in self.decitions:
                coop_actions += 1
            elif self.decitions[agent] == Action.COOP:
                coop_actions += 1
            elif self.decitions[agent] == Action.EXPLOIT:
                exploit_actions += 1
            else:
                inact_actions += 1
        if coop_actions > exploit_actions and coop_actions > inact_actions:
            return Action.COOP
        else:
            return Action.INACT


class ABRAgent(Agent):
    def __init__(self, id) -> None:
        self.reputation: dict[int, int] = {}
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        for agent, action in decitions.items():
            if agent not in self.reputation:
                self.reputation[agent] = 50

            if action == Action.EXPLOIT:
                self.reputation[agent] -= 30
            elif action == Action.COOP:
                self.reputation[agent] += 10
            else:
                self.reputation[agent] += 3

            self.reputation[agent] = max(self.reputation[agent], 0)
            self.reputation[agent] = min(self.reputation[agent], 100)

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        reputation = 0
        group_lenth: int = len(event.group)
        if group_lenth == 0:
            return Action.INACT
        for agent in event.group:
            if agent not in self.reputation:
                reputation += 50
            else:
                reputation += self.reputation[agent]
        group_reputation = reputation / group_lenth
        if group_reputation > 55:
            return Action.COOP
        return Action.INACT


class SearchAgent(Agent):
    def __init__(self, id) -> None:
        self.reputation: dict[int, int] = {}
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        for agent, action in decitions.items():
            if agent not in self.reputation:
                self.reputation[agent] = 50

            if action == Action.EXPLOIT:
                self.reputation[agent] -= 30
            elif action == Action.COOP:
                self.reputation[agent] += 10
            else:
                self.reputation[agent] += 3

            self.reputation[agent] = max(self.reputation[agent], 0)
            self.reputation[agent] = min(self.reputation[agent], 100)

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        return self.best_play(
            enviroment_info.public_resources[self.agent_id],
            5,
            self.reputation,
            enviroment_info,
        )[1]

    def best_play(
        self,
        resources: int,
        deep: int,
        reputation: dict[int, int],
        enviroment: EnviromentInfo,
    ) -> tuple[int, Action]:
        copy_reputation: dict[int, int] = reputation.copy()
        if deep == 0:
            return resources, Action.COOP

        group: list[int] = self.select_groups_with_trust(
            enviroment.agents_alive, enviroment.matrix_of_trust
        )

        desitions = []
        for agent in group:
            if agent not in copy_reputation:
                desitions.append(Action.COOP)
                copy_reputation[agent] = 50
            elif copy_reputation[agent] > 55:
                desitions.append(Action.COOP)
                copy_reputation[agent] += 10
            elif copy_reputation[agent] < 40:
                desitions.append(Action.EXPLOIT)
                copy_reputation[agent] -= 30
            else:
                desitions.append(Action.INACT)
                copy_reputation[agent] += 3

        for agent in group:
            for other in group:
                if agent != other:
                    if enviroment.matrix_of_trust[other] == Action.EXPLOIT:
                        enviroment.matrix_of_trust[agent][other] -= 0.2
                    elif enviroment.matrix_of_trust[other] == Action.INACT:
                        enviroment.matrix_of_trust[agent][other] += 0.05
                    elif enviroment.matrix_of_trust[other] == Action.COOP:
                        enviroment.matrix_of_trust[agent][other] += 0.1

        event_resources: int = random.randint(-100, 300) * len(desitions)

        # COOP
        desitions.append(Action.COOP)
        my_coop_resources = (
            resources + group_prisioners_game(desitions, event_resources)[-1]
        )
        coop_reosurce: int = self.best_play(
            my_coop_resources, deep - 1, copy_reputation, enviroment
        )[0]

        # INACT
        desitions.append(Action.INACT)
        my_inact_resources = (
            resources + group_prisioners_game(desitions, event_resources)[-1]
        )
        inact_reosurce: int = self.best_play(
            my_inact_resources, deep - 1, copy_reputation, enviroment
        )[0]

        # EXPLOIT
        desitions.append(Action.EXPLOIT)
        my_exploit_resources = (
            resources + group_prisioners_game(desitions, event_resources)[-1]
        )
        exploit_reosurce: int = self.best_play(
            my_exploit_resources, deep - 1, copy_reputation, enviroment
        )[0]

        if coop_reosurce > inact_reosurce and coop_reosurce > exploit_reosurce:
            return coop_reosurce, Action.COOP
        elif inact_reosurce > exploit_reosurce:
            return inact_reosurce, Action.INACT
        else:
            return exploit_reosurce, Action.EXPLOIT

    def ordenar_por_posiciones(self, array: list[int]) -> list[int]:
        arr: list[int] = array.copy()
        # Paso 2: Crear una lista de pares (valor, índice)
        pares: list[tuple[int, int]] = [
            (valor, indice) for indice, valor in enumerate(arr)
        ]

        # Paso 3: Ordenar la lista de pares en orden descendente por el valor
        pares_ordenados: list[tuple[int, int]] = sorted(
            pares, key=lambda x: x[0], reverse=True
        )

        # Paso 4: Extraer los índices ordenados
        indices_ordenados: list[int] = [par[1] for par in pares_ordenados]

        # Paso 5: Devolver los índices ordenados
        return indices_ordenados

    def select_groups_with_trust(self, agents, matrix) -> list[list[int]]:
        agents: list[int] = agents.copy()
        random.shuffle(agents)
        result: list[list[int]] = []
        while agents:
            rand: int = poisson(lam=5)
            group = []
            group.append(agents[0])
            indices_ordenados: list[int] = self.ordenar_por_posiciones(
                matrix[agents[0]]
            )
            for i in range(len(indices_ordenados)):
                if rand == 0:
                    break
                for roommate in group:
                    if not (
                        indices_ordenados[i] != roommate
                        and indices_ordenados[i] in agents
                        and random.random() < matrix[roommate][indices_ordenados[i]]
                    ):
                        break
                else:
                    group.append(indices_ordenados[i])
                    agents.remove(indices_ordenados[i])
                    rand -= 1

            result.append(group)
            agents.remove(agents[0])
        for group in result:
            if self.agent_id in group:
                return group
        return []

    def select_group(self, agents_alive: list[int]) -> list[int]:
        agents: list[int] = agents_alive.copy()
        agents.remove(self.agent_id)
        random.shuffle(agents)
        rand: int = poisson(lam=5)
        start: int = random.randint(0, len(agents))
        end: int = min(start + rand, len(agents))
        return agents[start:end]


class Resentful(Agent):
    def __init__(self, id) -> None:
        self.bad_people: list[int] = []
        self.agent_id = id

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        for agent, action in decitions.items():
            if agent not in self.bad_people and action == Action.EXPLOIT:
                self.bad_people.append(agent)

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        for agent in event.group:
            if agent in self.bad_people:
                return Action.INACT
        return Action.COOP


# Jugador que juegue random o juega la jugada que le ha hecho ganar más puntos en el pasado
