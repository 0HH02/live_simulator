from agents.agent import (
    Agent,
    PusilanimeAgent,
    RandomAgent,
    ThiefAgent,
    TipForTapAgent,
    ABRAgent,
)
from event_generator import (
    EventGenerator,
    SimpleEventGenerator,
    EventType,
    ProbabilisticEventGenerator,
    Event,
    EventInfo,
)
from enviroment import Enviroment, EnviromentInfo
from utils import group_prisioners_game, Action
import random
from stats import Stats


class Simulator:
    def __init__(
        self, agents: list[Agent], event_generator: EventGenerator, lost_per_day: int
    ) -> None:
        self.event_generator: EventGenerator = event_generator
        self.enviroment = Enviroment(agents, lost_per_day)
        self.lost_per_day: int = lost_per_day
        self.stats = Stats(self.enviroment)

    def run(self, days: int) -> dict:
        for _ in range(days):

            self.enviroment.next_day()
            print("Day: ", self.enviroment.day)
            new_event: Event = self.event_generator.GetNewEvent(
                self.enviroment.agents_alive
            )

            print("Event: ", new_event)

            if new_event.event_type == EventType.COOP:
                self.decide(new_event)
                resources = self.play_the_game(new_event)

            elif new_event.event_type == EventType.SPECIAL:
                resources = {}
                for agent in self.enviroment.agents_alive:
                    resources[agent] = new_event.resources // len(
                        self.enviroment.agents_alive
                    )
                self.enviroment.log[new_event] = {}

            self.update_enviroment(resources)

            if new_event.event_type == EventType.COOP:
                for agent in self.enviroment.agents_alive:
                    visible_desitions = self.get_visible_desitions(
                        new_event, agent, True
                    )
                    self.enviroment.agents[agent].passive_action(
                        EnviromentInfo(
                            self.enviroment.day,
                            self.enviroment.lost_per_day,
                            self.enviroment.public_resources[agent],
                        ),
                        visible_desitions,
                    )

            print(f"Public resources: {self.enviroment.public_resources}")
            if new_event.event_type == EventType.COOP:
                self.stats.plot_agent_resources(new_event)
        return self.enviroment.log

    def update_enviroment(self, resources) -> None:

        for agent, resource in resources.items():
            self.enviroment.public_resources[agent] += resource

        for agent in self.enviroment.agents_alive:
            self.enviroment.public_resources[agent] -= self.lost_per_day

        self.enviroment.agents_alive = [
            agent
            for agent in self.enviroment.agents_alive
            if self.enviroment.public_resources[agent] > 0
        ]

    def play_the_game(self, new_event: Event) -> dict:
        general_resources = {}
        for group in new_event.groups:
            resources: list[int] = group_prisioners_game(
                [self.enviroment.log[new_event][agent] for agent in group],
                new_event.resources * len(group) // len(self.enviroment.agents_alive),
            )
            for i, agent_id in enumerate(group):
                general_resources[agent_id] = resources[i]
        return general_resources

    def decide(self, new_event: Event) -> None:
        print("Desitions: {")
        self.enviroment.log[new_event] = {}
        for agent in self.enviroment.agents_alive:
            enviroment_info: EnviromentInfo = self.enviroment.get_enviroment_from(agent)
            event_info: EventInfo = new_event.getEventInfo(agent)
            action: Action = self.enviroment.agents[agent].active_action(
                enviroment_info, event_info
            )
            self.enviroment.log[new_event][agent] = action
            print("\t", agent, ": ", action, "(", self.enviroment.agents[agent], ")")
        print("}")

    def get_visible_desitions(
        self, event: Event, agent: int, get_all: bool
    ) -> dict[int, Action]:
        if get_all:
            log = self.enviroment.log[event].copy()
            log.pop(agent)
            return log
        else:
            group: list[int] = event.getEventInfo(agent).group
            return {agent: self.enviroment.log[event][agent] for agent in group}

    def str(self) -> str:
        return f"Agents: {self.enviroment.agents}, Day: {self.enviroment.day}, Log: {self.enviroment.log}, Public resources: {self.enviroment.public_resources}"

    def repr(self) -> str:
        return str(self)


def population_random_generator(length: int) -> list[Agent]:
    agent_classes = [
        PusilanimeAgent,
        ThiefAgent,
        TipForTapAgent,
        RandomAgent,
        ABRAgent,
    ]
    return [random.choice(agent_classes)() for i in range(length)]


Simulator(
    population_random_generator(400),
    ProbabilisticEventGenerator(
        good_coop_resource_probability=0.8,
        good_time_probabilities=0.7,
        coop_event_probability=0.8,
    ),
    100,
).run(10 * 360)
