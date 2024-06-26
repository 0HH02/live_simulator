from .agents.agent import (
    Agent,
    Action,
    EnviromentInfo,
    Event,
    PusilanimeAgent,
    RandomAgent,
    ThiefAgent,
)
from .event_generator import EventGenerator, SimpleEventGenerator
from .enviroment import Enviroment
from .utils import group_prisioners_game


class Simulator:
    def __init__(self, agents: list[Agent], event_generator: EventGenerator):
        self.event_generator: EventGenerator = event_generator
        self.enviroment = Enviroment(agents)
        self.lost_per_day = 100

    def run(self, days: int):
        for _ in range(days):

            self.enviroment.next_day()
            print("Day: ", self.enviroment.day)
            new_event: Event = self.event_generator.GetNewEvent(
                self.enviroment.agents_alive
            )
            print("Event: ", new_event)
            print("Desitions: {")
            self.enviroment.log[new_event] = {}
            for agent in self.enviroment.agents_alive:
                enviroment_info: EnviromentInfo = self.enviroment.get_enviroment_from(
                    agent
                )
                action: Action = self.enviroment.agents[agent].active_action(
                    enviroment_info, new_event
                )
                self.enviroment.log[new_event][agent] = action
                print("\t", agent, ": ", action)
            print("}")

            for group in new_event.groups:
                resources: list[int] = group_prisioners_game(
                    [self.enviroment.log[new_event][agent] for agent in group],
                    new_event.resources
                    * len(group)
                    // len(self.enviroment.agents_alive),
                )
                for i, agent_id in enumerate(group):
                    self.enviroment.public_resources[agent_id] += resources[i]

            for agent in self.enviroment.agents_alive:
                self.enviroment.public_resources[agent] -= self.lost_per_day

            self.enviroment.agents_alive = [
                agent
                for agent in self.enviroment.agents_alive
                if self.enviroment.public_resources[agent] > 0
            ]

            for agent in self.enviroment.agents_alive:
                self.enviroment.agents[agent].passive_action(
                    EnviromentInfo(
                        self.enviroment.log, self.enviroment.public_resources
                    )
                )

            print(f"Public resources: {self.enviroment.public_resources}")
            input()
        return self.enviroment.log

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
).run(1 * 360)
