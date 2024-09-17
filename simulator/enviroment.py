"""
"""

import random
import numpy as np

from agents.agent import Agent
from enviroment_info import EnviromentInfo, Event


class Enviroment:
    """
    Represents the environment in which agents interact and simulate their behavior.

    Attributes:
        agents (list[Agent]): A list of Agent objects representing the agents in the environment.
        agents_alive (list[int]): A list of indices representing the indices of alive agents.
        day (int): An integer representing the current day of the simulation.
        log (dict): A dictionary containing the log of events in the environment.
        public_resources (list[int]): A list of integers representing the available public resources.

    Methods:
        get_enviroment_from(agent: int) -> EnviromentInfo:
            Returns an EnviromentInfo object containing information about the environment for a specific agent.

        next_day() -> None:
            Advances the simulation to the next day.

        __str__() -> str:
            Returns a string representation of the Enviroment object.

        __repr__() -> str:
            Returns a string representation of the Enviroment object.
    """

    def __init__(self, agents: list[Agent], lost_per_day: int):
        self.agents: list[Agent] = agents
        self.agents_alive: list[int] = list(range(len(agents)))
        self.day = 0
        self.log: dict[Event, dict] = {}
        self.lost_per_day = lost_per_day
        self.public_resources: list[int] = [
            random.randint(300, 600) for x in range(len(agents))
        ]
        self.global_reputation: dict[Agent:int] = {}
        self.trust_matrix: list[list[int]] = [
            [50 for j in range(len(agents))] for i in range(len(agents))
        ]
        self.generation = 1

    def copy(self, new_agents=None, reproduction_density=1):
        new_env = Enviroment(
            new_agents if new_agents is not None else self.agents,
            self.lost_per_day,
        )
        new_env.agents_alive = self.agents_alive[:] + [
            index
            for index in range(
                len(self.agents), len(self.agents) + 1 + reproduction_density
            )
        ]

        new_env.day = self.day
        new_env.log = self.log.copy()
        new_env.public_resources = self.public_resources[:] + [
            random.randint(300, 600) for x in range(reproduction_density + 1)
        ]
        new_env.global_reputation = self.global_reputation.copy()
        new_env.trust_matrix.extend(
            [
                [50 for _ in range(len(self.agents) + reproduction_density)]
                for _ in range(reproduction_density)
            ]
        )
        new_env.generation = self.generation + 1
        return new_env

    def get_enviroment_from(self, agent: int) -> EnviromentInfo:
        return EnviromentInfo(
            self.day,
            self.lost_per_day,
            self.public_resources,
            self.agents_alive,
            self.trust_matrix,
        )

    def next_day(self) -> None:
        self.day += 1

    def __str__(self) -> str:
        return f"Agents: {self.agents}"

    def __repr__(self) -> str:
        return str(self)
