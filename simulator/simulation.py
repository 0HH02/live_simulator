from agents.agent import (
    Agent,
    PusilanimeAgent,
    RandomAgent,
    ThiefAgent,
    TipForTapAgent,
    TipForTapSecureAgent,
    ABRAgent,
    SearchAgent,
    Resentful,
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

from gemini import make_history


def dict_to_string(log: dict, agents: list[Agent]) -> str:
    log_text = []
    day = 1
    for event, decisions in log.items():
        # Convertir el evento a string
        log_text.append(f"Day: {day}\n")
        day += 1
        event_str = str(event)
        log_text.append(f"Event: {event_str}\n")

        # Convertir el dict de decisiones a string
        for agent, action in decisions.items():
            agent_str = str(agent)
            action_str = str(action)
            log_text.append(f"\tAgent {agent_str}: {action_str} ( {agents[agent]} )\n")

    return "".join(log_text)


class Simulator:
    def __init__(
        self,
        agents: list[Agent],
        event_generator: EventGenerator,
        lost_per_day: int,
        thief_toleration: int,
        reproduction_rate: int,
        reproduction_density: int,
    ) -> None:
        self.event_generator: EventGenerator = event_generator
        self.enviroment = Enviroment(agents, lost_per_day)
        self.lost_per_day: int = lost_per_day
        self.stats = Stats(self.enviroment)
        self.thief_toleration: int = thief_toleration
        self.reproduction_rate: int = reproduction_rate
        self.reproduction_density: int = reproduction_density

    def run(self, days: int) -> dict:
        for _ in range(days):

            self.enviroment.next_day()
            print("Day: ", self.enviroment.day)
            new_event: Event = self.event_generator.GetNewEvent(
                self.enviroment.agents_alive,
                self.thief_toleration,
                self.enviroment.global_reputation,
                self.enviroment.trust_matrix,
            )
            # print("Trust: ", self.enviroment.trust_matrix)
            print("Event: ", new_event)

            if new_event.event_type == EventType.COOP:
                self.decide(new_event)
                resources = self.play_the_game(new_event)

            elif new_event.event_type == EventType.SPECIAL:
                resources = {}
                special_agent: list[int] = random.sample(
                    self.enviroment.agents_alive,
                    random.randint(1, len(self.enviroment.agents_alive)),
                )
                for agent in special_agent:
                    resources[agent] = new_event.resources // len(
                        self.enviroment.agents_alive
                    )
                self.enviroment.log[new_event] = {}

            self.update_enviroment(resources)

            if new_event.event_type == EventType.COOP:
                for group in new_event.groups:
                    for agent in group:
                        visible_desitions: dict[int, Action] = (
                            self.get_visible_desitions(new_event, agent, False, 0)
                        )
                        self.enviroment.agents[agent].passive_action(
                            EnviromentInfo(
                                self.enviroment.day,
                                self.enviroment.lost_per_day,
                                self.enviroment.public_resources[agent],
                                self.enviroment.agents_alive,
                                self.enviroment.trust_matrix,
                            ),
                            visible_desitions,
                        )

            print(f"Public resources: {self.enviroment.public_resources}")
            if new_event.event_type == EventType.COOP:
                self.stats.plot_agent_resources(new_event, self.enviroment)

        print(dict_to_string(self.enviroment.log, self.enviroment.agents))
        with open("log.txt", "w", encoding="ISO-8859-1") as f:
            f.write(dict_to_string(self.enviroment.log, self.enviroment.agents))

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
        if self.enviroment.day % self.reproduction_rate == 0:

            alive_agents_with_resources = {
                agent: self.enviroment.public_resources[agent]
                for agent in self.enviroment.agents_alive
            }

            sorted_agents: list[tuple[int, int]] = sorted(
                alive_agents_with_resources.items(), key=lambda x: x[1], reverse=True
            )

            top_agents: list[int] = [
                agent for agent, _ in sorted_agents[: self.reproduction_density + 1]
            ]

            new_agents: list[Agent] = self.enviroment.agents[:]
            new_agents.extend([self.enviroment.agents[agent] for agent in top_agents])

            self.enviroment: Enviroment = self.enviroment.copy(
                new_agents=new_agents, reproduction_density=self.reproduction_density
            )

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
        for group in new_event.groups:
            for agent in group:
                enviroment_info: EnviromentInfo = self.enviroment.get_enviroment_from(
                    agent
                )
                event_info: EventInfo = new_event.getEventInfo(agent)
                action: Action = self.enviroment.agents[agent].active_action(
                    enviroment_info, event_info
                )
                self.enviroment.log[new_event][agent] = action
                self.set_reputation(agent, action)

                print(
                    "\t", agent, ": ", action, "(", self.enviroment.agents[agent], ")"
                )
            for agent in group:
                for other in group:
                    if agent != other:
                        if self.enviroment.log[new_event][other] == Action.EXPLOIT:
                            self.enviroment.trust_matrix[agent][other] -= 0.2
                        elif self.enviroment.log[new_event][other] == Action.INACT:
                            self.enviroment.trust_matrix[agent][other] += 0.05
                        elif self.enviroment.log[new_event][other] == Action.COOP:
                            self.enviroment.trust_matrix[agent][other] += 0.1

        print("}")

    def set_reputation(self, agent: int, action: Action):
        if agent in self.enviroment.global_reputation:
            if action == Action.COOP:
                self.enviroment.global_reputation[agent] = max(
                    self.enviroment.global_reputation[agent] + 10, 100
                )
            elif action == Action.INACT:
                self.enviroment.global_reputation[agent] = max(
                    self.enviroment.global_reputation[agent] + 3, 100
                )
            else:
                self.enviroment.global_reputation[agent] = max(
                    self.enviroment.global_reputation[agent] - 30, 0
                )
        else:
            self.enviroment.global_reputation[agent] = 50

    def get_visible_desitions(
        self, event: Event, agent: int, get_all: bool, noise: float
    ) -> dict[int, Action]:
        if get_all:
            log = self.enviroment.log[event].copy()
            if agent in log:
                log.pop(agent)

            # Add missunderstanding with 10% probability
            for ag in log:
                if random.random() < noise:
                    log[ag] = random.choice([Action.COOP, Action.EXPLOIT, Action.INACT])

            return log

        else:
            group: list[int] = event.getEventInfo(agent).group
            desitions: dict[int, Action] = {
                agent: self.enviroment.log[event][agent] for agent in group
            }
            # Add missunderstanding with 10% probability
            for ag in desitions:
                if random.random() < noise:
                    desitions[ag] = random.choice(
                        [Action.COOP, Action.EXPLOIT, Action.INACT]
                    )

            return desitions

    def str(self) -> str:
        return f"Agents: {self.enviroment.agents}, Day: {self.enviroment.day}, Log: {self.enviroment.log}, Public resources: {self.enviroment.public_resources}"

    def repr(self) -> str:
        return str(self)


def population_random_generator(length: int) -> list[Agent]:
    agent_classes = [
        PusilanimeAgent,
        ThiefAgent,
        TipForTapAgent,
        TipForTapSecureAgent,
        RandomAgent,
        ABRAgent,
        SearchAgent,
        Resentful,
    ]
    return [random.choice(agent_classes)(i) for i in range(length)]


Simulator(
    population_random_generator(50),
    ProbabilisticEventGenerator(
        good_coop_resource_probability=0.8,
        good_time_probabilities=0.7,
        coop_event_probability=0.8,
    ),
    lost_per_day=60,
    thief_toleration=1,
    reproduction_rate=20,
    reproduction_density=10,
).run(365)

print(make_history())
