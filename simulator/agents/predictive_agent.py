"""
This module contains the definition of the PredictiveAgent class.
"""

from simulator.event_generator import Event
from simulator.utils import Action
from .agent import Agent
from ..enviroment_info import EnviromentInfo


class PredictiveAgent(Agent):

    def __init__(self) -> None:
        self.memory: dict[int, dict[int, Action]] = {}

    def passive_action(self, enviroment_info: EnviromentInfo) -> None:
        pass

    def active_action(self, enviroment_info: EnviromentInfo, event: Event) -> Action:
        pass
