"""
This module contains the abstract class Agent and the basic implementation of it.
"""

from abc import ABC, abstractmethod
import random
from numpy.random import poisson
import numpy as np

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


class Desire(ABC):
    @abstractmethod
    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        pass


class Random(Desire):
    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        return random.choice(list(Action))


class Pusilanime(Desire):

    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        return Action.COOP


class Thief(Desire):
    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        return Action.EXPLOIT


class TipForTap(Desire):
    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        coop_actions = 0
        exploit_actions = 0
        inact_actions = 0
        for agent in event_info.group:
            if agent not in belive["global_actions"]:
                coop_actions += 1
            elif belive["global_actions"][agent][-1] == Action.COOP:
                coop_actions += 1
            elif belive["global_actions"][agent][-1] == Action.EXPLOIT:
                exploit_actions += 1
            else:
                inact_actions += 1
        if coop_actions > exploit_actions and coop_actions > inact_actions:
            return Action.COOP
        elif exploit_actions > inact_actions:
            return Action.EXPLOIT
        else:
            return Action.INACT


class TipForTapSecure(Desire):
    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        coop_actions = 0
        exploit_actions = 0
        inact_actions = 0
        for agent in event_info.group:
            if agent not in belive["global_actions"]:
                coop_actions += 1
            elif belive["global_actions"][agent][-1] == Action.COOP:
                coop_actions += 1
            elif belive["global_actions"][agent][-1] == Action.EXPLOIT:
                exploit_actions += 1
            else:
                inact_actions += 1
        if coop_actions > exploit_actions and coop_actions > inact_actions:
            return Action.COOP
        else:
            return Action.INACT


class ABR(Desire):

    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        reputation = 0
        group_lenth: int = len(event_info.group)
        if group_lenth == 0:
            return Action.INACT
        for agent in event_info.group:
            if agent not in belive["trust"]:
                reputation += 50
            else:
                reputation += belive["trust"][agent]
        group_reputation = reputation / group_lenth
        if group_reputation > 55:
            return Action.COOP
        return Action.INACT


class Search(Desire):

    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        return self.best_play(
            belive["resources"],
            0 if len(belive["agents_alive"]) == 0 else 5,
            belive["trust"],
            belive["agents_alive"],
        )[1]

    def best_play(
        self,
        resources: int,
        deep: int,
        reputation: dict[int, int],
        agents_alive: list[int],
    ) -> tuple[int, Action]:
        if deep == 0:
            return resources, Action.COOP

        copy_reputation: dict[int, int] = reputation.copy()
        copy_agents_alive: list[int] = agents_alive.copy()
        group: list[int] = self.select_group(copy_agents_alive)

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

        event_resources: int = random.randint(-100, 300) * len(desitions)

        # COOP
        desitions.append(Action.COOP)
        my_coop_resources = (
            resources + group_prisioners_game(desitions, event_resources)[-1]
        )
        coop_reosurce: int = self.best_play(
            my_coop_resources, deep - 1, copy_reputation, copy_agents_alive
        )[0]
        desitions.pop()

        # INACT
        desitions.append(Action.INACT)
        my_inact_resources = (
            resources + group_prisioners_game(desitions, event_resources)[-1]
        )
        inact_reosurce: int = self.best_play(
            my_inact_resources, deep - 1, copy_reputation, copy_agents_alive
        )[0]
        desitions.pop()
        # EXPLOIT
        desitions.append(Action.EXPLOIT)
        my_exploit_resources = (
            resources + group_prisioners_game(desitions, event_resources)[-1]
        )
        exploit_reosurce: int = self.best_play(
            my_exploit_resources, deep - 1, copy_reputation, copy_agents_alive
        )[0]
        desitions.pop()

        if coop_reosurce > inact_reosurce and coop_reosurce > exploit_reosurce:
            return coop_reosurce, Action.COOP
        elif inact_reosurce > exploit_reosurce:
            return inact_reosurce, Action.INACT
        else:
            return exploit_reosurce, Action.EXPLOIT

    def select_group(self, agents_alive: list[int]) -> list[int]:
        agents: list[int] = agents_alive.copy()
        random.shuffle(agents)
        rand: int = poisson(lam=5)
        start: int = random.randint(0, len(agents))
        end: int = min(start + rand, len(agents))
        return agents[start:end]


class Resentful(Desire):

    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        for agent in event_info.group:
            if agent in belive["betrayers"]:
                return Action.INACT
        return Action.COOP


class Explote(Desire):

    def decide(self, belive: dict, event_info: EventInfo) -> Action:
        return max(
            belive["best_action"], key=lambda x: np.mean(belive["best_action"].get(x))
        )


# Jugador que juegue random o juega la jugada que le ha hecho ganar más puntos en el pasado


class BDIAgent(Agent):
    def __init__(self, agent_id: int, desires: dict):
        self.agent_id: int = agent_id
        self.beliefs = {
            "trust": {},  # Confianza en otros agentes
            "resources": 0,  # Recursos actuales
            "day": 0,  # Día actual
            "betrayers": set(),  # Agentes que han traicionado
            "best_action": {
                Action.COOP: [],
                Action.EXPLOIT: [],
                Action.INACT: [],
            },  # Acción que más recursos aportó
            "global_actions": {},  # Acción que más recursos aportó
            "agents_alive": [],
        }
        self.desires: dict[str, int] = desires  # Lista de deseos (objetivos)
        self.intentions: dict[Action, int] = {
            Action.COOP: 0,
            Action.EXPLOIT: 0,
            Action.INACT: 0,
        }  # Lista de intenciones (planes)

    def update_beliefs(
        self, enviroment_info: EnviromentInfo, visible_desitions: dict[int, Action]
    ):
        # Actualizamos las creencias según la información del entorno
        self.beliefs["day"] = enviroment_info.day

        for agent_id, desitions in visible_desitions.items():
            if agent_id != self.agent_id:
                if agent_id not in self.beliefs["trust"]:
                    self.beliefs["trust"][agent_id] = 50  # Valor inicial de confianza
                elif desitions == Action.COOP:
                    self.beliefs["trust"][agent_id] = min(
                        self.beliefs["trust"][agent_id] + 10, 100
                    )
                elif desitions == Action.EXPLOIT:
                    self.beliefs["trust"][agent_id] = max(
                        self.beliefs["trust"][agent_id] - 30, 0
                    )
                    self.beliefs["betrayers"].add(agent_id)
                elif desitions == Action.INACT:
                    self.beliefs["trust"][agent_id] = min(
                        self.beliefs["trust"][agent_id] + 3, 100
                    )
                if self.agent_id not in self.beliefs["global_actions"]:

                    self.beliefs["global_actions"][agent_id] = [desitions]
                else:
                    self.beliefs["global_actions"][agent_id].append(desitions)

        self.beliefs["agents_alive"] = enviroment_info.agents_alive.copy()

        # if self.agent_id not in self.beliefs["best_action"]:
        #     self.beliefs["best_action"][visible_desitions[self.agent_id]] = [
        #         enviroment_info.public_resources[self.agent_id]
        #         - self.beliefs["resources"]
        #     ]
        # else:
        #     self.beliefs["best_action"][visible_desitions[self.agent_id]].append(
        #         enviroment_info.public_resources[self.agent_id]
        #         - self.beliefs["resources"]
        #     )

        self.beliefs["resources"] = enviroment_info.public_resources[self.agent_id]

    def decide_action_based_on_beliefs_and_desires(self, event_info: EventInfo):
        intentions: dict[Action, int] = {
            Action.COOP: 0,
            Action.EXPLOIT: 0,
            Action.INACT: 0,
        }
        for desire, weights in self.desires.items():
            if desire == "Pusilanime":
                intentions[Pusilanime().decide(self.beliefs, event_info)] += weights
            elif desire == "Thief":
                intentions[Thief().decide(self.beliefs, event_info)] += weights
            elif desire == "TipForTap":
                intentions[TipForTap().decide(self.beliefs, event_info)] += weights
            elif desire == "TipForTapSecure":
                intentions[
                    TipForTapSecure().decide(self.beliefs, event_info)
                ] += weights
            elif desire == "Random":
                intentions[Random().decide(self.beliefs, event_info)] += weights
            elif desire == "ABR":
                intentions[ABR().decide(self.beliefs, event_info)] += weights
            elif desire == "Search":
                intentions[Search().decide(self.beliefs, event_info)] += weights
            elif desire == "Resentful":
                intentions[Resentful().decide(self.beliefs, event_info)] += weights
            elif desire == "Explote":
                intentions[Explote().decide(self.beliefs, event_info)] += weights
        return max(intentions, key=intentions.get)

    def active_action(
        self, enviroment_info: EnviromentInfo, event_info: EventInfo
    ) -> Action:
        action: Action = self.decide_action_based_on_beliefs_and_desires(event_info)

        return action

    def passive_action(
        self, enviroment_info: EnviromentInfo, visible_desitions: dict[int, Action]
    ) -> None:
        self.update_beliefs(enviroment_info, visible_desitions)


class PusilanimeAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"Pusilanime": 1})


class ThiefAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"Thief": 1})


class RandomAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"Random": 1})


class TipForTapAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"TipForTap": 1})


class TipForTapSecureAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"TipForTapSecure": 1})


class ExploteAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"Explote": 1})


class ABRAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"ABR": 1})


class SearchAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"Search": 1})


class ResentfulAgent(BDIAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, {"Resentful": 1})
