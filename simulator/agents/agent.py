"""
This module contains the abstract class Agent and the basic implementation of it.
"""

from abc import ABC, abstractmethod
import random

from enviroment_info import EnviromentInfo, Event
from utils import Action
from event_generator import EventInfo


class Agent(ABC):
    """
    Abstract base class for defining an agent in the simulator.
    """

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

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        pass

    def active_action(
        self, enviroment_info: EnviromentInfo, event: EventInfo
    ) -> Action:
        return Action.EXPLOIT


class TipForTapAgent(Agent):
    def __init__(self) -> None:
        self.decitions: dict[int, Action] = {}

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


# Adaptative Based Reputation Agent
class ABRAgent(Agent):
    def __init__(self) -> None:
        self.reputation: dict[int, int] = {}

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
