from abc import ABC, abstractmethod
import random

from enviroment_info import EnviromentInfo
from event_generator import Event
from utils import Action


class Agent(ABC):
    @abstractmethod
    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        pass

    @abstractmethod
    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        pass


class RandomAgent(Agent):

    def passive_action(
        self, enviroment_info: EnviromentInfo, decitions: dict[int, Action]
    ) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        return random.choice(list(Action))

    def __str__(self) -> str:
        return f"Agent"

    def __repr__(self) -> str:
        return str(self)


class PusilanimeAgent(Agent):
    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        return Action.COOP

    def __str__(self) -> str:
        return f"Agent"

    def __repr__(self) -> str:
        return str(self)


class ThiefAgent(Agent):
    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        return Action.EXPLOIT

    def __str__(self) -> str:
        return f"Agent"

    def __repr__(self) -> str:
        return str(self)
