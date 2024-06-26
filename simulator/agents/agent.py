"""
This module contains the abstract class Agent and the basic implementation of it.
"""
from abc import ABC, abstractmethod
import random

from ..enviroment_info import EnviromentInfo, Event
from ..utils import Action



class Agent(ABC):
    """
    Abstract base class for defining an agent in the simulator.
    """

    @abstractmethod
    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
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
        return "Agent"

    def __repr__(self) -> str:
        return self.__str__()


class RandomAgent(Agent):
    """
    This class represents an agent that takes random actions.
    """
    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        return random.choice(list(Action))



class PusilanimeAgent(Agent):
    """
    This class represents an agent that always cooperates.
    """
    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        return Action.COOP




class ThiefAgent(Agent):
    """
    This class represent an agent that always exploits.
    """
    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        return Action.EXPLOIT

