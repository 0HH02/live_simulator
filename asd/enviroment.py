from agent import Agent
from enviroment_info import EnviromentInfo
import random
import numpy

# pylint: disable=consider-using-enumerate


class Enviroment:
    def __init__(self, agents: list[Agent], lost_per_day: int):
        self.agents: list[Agent] = agents
        self.agents_alive: list[int] = list(range(len(agents)))
        self.day = 0
        self.log = {}
        self.lost_per_day = lost_per_day
        self.public_resources: list[int] = [
            random.randint(300, 600) for x in range(len(agents))
        ]

    def get_enviroment_from(self, agent: int):
        return EnviromentInfo(self.day, self.lost_per_day, self.public_resources)

    def next_day(self) -> None:
        self.day += 1

    def __str__(self) -> str:
        return f"Agents: {self.agents}"

    def __repr__(self) -> str:
        return str(self)
