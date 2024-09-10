"""
"""

import random
from abc import ABC, abstractmethod
from numpy.random import poisson
from utils import EventType


class EventInfo:
    def __init__(self, event_type: EventType, group: list[int], resources: int):
        self.event_type: EventType = event_type
        self.group: list[int] = group
        self.resources: int = resources


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

    def getEventInfo(self, agent_id: int) -> EventInfo:
        for group in self.groups:
            if agent_id in group:
                new_group: list[int] = group.copy()
                new_group.remove(agent_id)
                return EventInfo(self.event_type, new_group, self.resources)
        raise ValueError("The agent is not in the event.")


class EventGenerator(ABC):
    @abstractmethod
    def GetNewEvent(self, agents, thief_toleration) -> Event:
        pass


class SimpleEventGenerator(EventGenerator):
    def GetNewEvent(
        self,
        agents: list[int],
        thief_toleration: int,
        global_reputation: dict,
    ) -> Event:
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


class ProbabilisticEventGenerator(EventGenerator):
    def __init__(
        self,
        good_time_probabilities: float,
        coop_event_probability: float,
        good_coop_resource_probability: float,
    ):
        self.good_time_probabilities: float = good_time_probabilities
        self.coop_event_probability: float = coop_event_probability
        self.good_coop_resource_probability: float = good_coop_resource_probability

    def GetNewEvent(
        self,
        agents: list[int],
        thief_toleration: int,
        global_reputation: dict,
    ) -> Event:
        event_type: EventType = self.select_event_type()
        groups: list[list[int]] = self.select_groups(agents)

        if event_type == EventType.COOP:
            if random.random() < self.good_coop_resource_probability:
                self.thief_control(thief_toleration, groups, global_reputation)
                resources: int = random.randint(100, 300) * len(agents)
            else:
                resources: int = random.randint(-50, 0) * len(agents)
        else:
            if random.random() < self.good_time_probabilities:
                resources: int = random.randint(0, 50) * len(agents)
            else:
                resources: int = random.randint(-10, 0) * len(agents)
        return Event(event_type, groups, resources)

    def thief_control(
        self,
        thief_toleration: int,
        groups: list[list[int]],
        global_reputation: dict,
    ):
        for group in groups:
            group[:] = [
                agent
                for agent in group
                if agent not in global_reputation
                or global_reputation[agent] > 30
                or random.random() < thief_toleration
            ]

    def select_event_type(self) -> EventType:
        if random.random() < self.coop_event_probability:
            return EventType.COOP
        return EventType.SPECIAL

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
