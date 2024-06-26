"""
"""
import random
from abc import ABC, abstractmethod
from numpy.random import poisson
from .utils import EventType


class Event:
    def __init__(self, event_type: EventType, groups: list[list[int]], resources: int):
        self.event_type: EventType = event_type
        self.groups: list[list[int]] = groups
        self.resources: int = resources

    def __hash__(self) -> int:
        return id(self)

    def __str__(self) -> str:
        return (
            f"{self.event_type}, agents id: {self.groups}, resources: {self.resources}"
        )

    def __repr__(self) -> str:
        return str(self)


class EventGenerator(ABC):
    @abstractmethod
    def GetNewEvent(self, agents) -> Event:
        pass


class SimpleEventGenerator(EventGenerator):
    def GetNewEvent(self, agents: list[int]) -> Event:
        event_type: EventType = random.choice(list(EventType))
        groups: list[list[int]] = self.select_groups(agents)
        resources: int = random.randint(-100, 350) * len(agents)
        return Event(event_type, groups, resources)

    def select_groups(self, agents) -> list[list[int]]:
        agents: list[int] = agents.copy()
        random.shuffle(agents)
        index = 0
        result: list[list[int]] = []
        while index < len(agents):
            rand: int = poisson(lam=5)
            end: int = min(index + rand, len(agents))
            result.append(agents[index:end])
            index: int = end
        return result
