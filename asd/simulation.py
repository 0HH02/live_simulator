from agent import (
    Agent,
    Action,
    EnviromentInfo,
    Event,
    PusilanimeAgent,
    RandomAgent,
    ThiefAgent,
)
from event_generator import EventGenerator, SimpleEventGenerator, EventType
from enviroment import Enviroment
from utils import group_prisioners_game


class Simulator:
    def __init__(
        self, agents: list[Agent], event_generator: EventGenerator, lost_per_day: int
    ) -> None:
        self.event_generator: EventGenerator = event_generator
        self.enviroment = Enviroment(agents, lost_per_day)
        self.lost_per_day: int = lost_per_day

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

            self.update_enviroment(resources)

            for agent in self.enviroment.agents_alive:
                self.enviroment.agents[agent].passive_action(
                    EnviromentInfo(
                        self.enviroment.day,
                        self.enviroment.lost_per_day,
                        self.enviroment.public_resources[agent],
                    ),
                    self.enviroment.log[new_event],
                )

            print(f"Public resources: {self.enviroment.public_resources}")
            input()
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

    def decide(self, new_event) -> None:
        print("Desitions: {")
        self.enviroment.log[new_event] = {}
        for agent in self.enviroment.agents_alive:
            enviroment_info: EnviromentInfo = self.enviroment.get_enviroment_from(agent)
            action: Action = self.enviroment.agents[agent].active_action(
                enviroment_info, new_event
            )
            self.enviroment.log[new_event][agent] = action
            print("\t", agent, ": ", action)
        print("}")

    def __str__(self) -> str:
        return f"Agents: {self.enviroment.agents}, Day: {self.enviroment.day}, Log: {self.enviroment.log}, Public resources: {self.enviroment.public_resources}"

    def __repr__(self) -> str:
        return str(self)


Simulator(
    [
        ThiefAgent(),
        RandomAgent(),
        RandomAgent(),
        RandomAgent(),
        RandomAgent(),
        RandomAgent(),
        RandomAgent(),
        RandomAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
        PusilanimeAgent(),
    ],
    SimpleEventGenerator(),
    100,
).run(1 * 360)
