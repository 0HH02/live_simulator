from agents.agent import (
    Agent,
    BDIAgent,
    PusilanimeAgent,
    RandomAgent,
    ThiefAgent,
    TipForTapAgent,
    TipForTapSecureAgent,
    ABRAgent,
    SearchAgent,
    ResentfulAgent,
    ExploteAgent,
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
        max_population: int,
        global_visible_desitions: bool,
        noise: float,
    ) -> None:
        self.event_generator: EventGenerator = event_generator
        self.enviroment = Enviroment(agents, lost_per_day)
        self.lost_per_day: int = lost_per_day
        self.stats = Stats(self.enviroment)
        self.thief_toleration: int = thief_toleration
        self.reproduction_rate: int = reproduction_rate
        self.reproduction_density: int = reproduction_density
        self.max_population: int = max_population
        self.global_visible_desitions: bool = global_visible_desitions
        self.record_days: list[int] = [1, 90, 180, 270, 360, 450, 540, 630, 720]
        self.summary_data: list = []
        self.total_thefts = 0
        self.noise: float = noise

    def collect_summary_data(self, day):
        agents_alive = self.enviroment.agents_alive
        public_resources = self.enviroment.public_resources

        # Calcular recursos totales y promedio
        total_resources = sum([public_resources[agent] for agent in agents_alive])
        avg_resources = total_resources / len(agents_alive) if agents_alive else 0

        # Contar agentes por tipo
        agent_type_counts = {}
        agent_type_resources = {}
        for agent_id in agents_alive:
            agent_type = type(self.enviroment.agents[agent_id]).__name__
            agent_type_counts[agent_type] = agent_type_counts.get(agent_type, 0) + 1
            agent_type_resources.setdefault(agent_type, []).append(
                public_resources[agent_id]
            )

        # Calcular recursos promedio por tipo de agente
        agent_type_avg_resources = {}
        for agent_type, resources in agent_type_resources.items():
            agent_type_avg_resources[agent_type] = sum(resources) / len(resources)

        # Crear un diccionario con los datos recopilados
        data = {
            "day": day,
            "avg_resources": avg_resources,
            "agent_type_counts": agent_type_counts,
            "total_thefts": self.total_thefts,
            "agents_alive": len(agents_alive),
            "agent_type_avg_resources": agent_type_avg_resources,
        }

        return data

    def run(self, days: int, verbose=False) -> dict:
        for _ in range(days):

            self.enviroment.next_day()
            # if verbose:
            # print("Day: ", self.enviroment.day)
            new_event: Event = self.event_generator.GetNewEvent(
                self.enviroment.agents_alive,
                self.thief_toleration,
                self.enviroment.global_reputation,
                self.enviroment.trust_matrix,
            )
            if verbose:
                # print("Trust: ", self.enviroment.trust_matrix)
                print("Event: ", new_event)

            if new_event.event_type == EventType.COOP:
                self.decide(new_event, verbose)
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
                            self.get_visible_desitions(
                                new_event,
                                agent,
                                self.global_visible_desitions,
                                self.noise,
                            )
                        )
                        self.enviroment.agents[agent].passive_action(
                            EnviromentInfo(
                                self.enviroment.day,
                                self.enviroment.lost_per_day,
                                self.enviroment.public_resources,
                                self.enviroment.agents_alive,
                                self.enviroment.trust_matrix,
                                self.enviroment.global_reputation,
                            ),
                            visible_desitions,
                        )
            if verbose:
                print(f"Public resources: {self.enviroment.public_resources}")
            if not self.enviroment.agents_alive:
                return self.enviroment.log
            # Graficas:
            if new_event.event_type == EventType.COOP:
                self.stats.plot_agent_resources(new_event, self.enviroment)

            self.actual_summary_data = self.collect_summary_data(self.enviroment.day)

            if self.enviroment.day in self.record_days:
                # Añadir el diccionario a la lista summary_data
                self.summary_data.append(self.actual_summary_data)

        if verbose:
            print(dict_to_string(self.enviroment.log, self.enviroment.agents))
        with open("log.txt", "w", encoding="ISO-8859-1") as f:
            f.write(dict_to_string(self.enviroment.log, self.enviroment.agents))

        return {"log": self.enviroment.log, "summary_data": self.summary_data}

    def update_enviroment(self, resources) -> None:

        for agent, resource in resources.items():
            self.enviroment.public_resources[agent] += resource

        for agent in self.enviroment.agents_alive:
            self.enviroment.public_resources[agent] -= self.lost_per_day

        # Reproduction
        if self.enviroment.day % self.reproduction_rate == 0:

            agent_type_avg_resources = self.actual_summary_data[
                "agent_type_avg_resources"
            ]
            total_avg_resources = sum(agent_type_avg_resources.values())
            agent_type_probabilities = {
                agent_type: avg_resources / total_avg_resources
                for agent_type, avg_resources in agent_type_avg_resources.items()
            }

            new_agents = []
            for _ in range(self.reproduction_density):

                agent_type = random.choices(
                    list(agent_type_probabilities.keys()),
                    weights=list(agent_type_probabilities.values()),
                    k=1,
                )[0]
                agent_class: Agent = next(
                    cls
                    for cls in BDIAgent.__subclasses__()
                    if cls.__name__ == agent_type
                )
                new_agents.append(
                    agent_class(len(self.enviroment.agents) + len(new_agents))
                )

            self.add_agents(new_agents)

        # Eliminar los n agentes con menos recursos
        overpopulation = len(self.enviroment.agents_alive) - self.max_population
        if overpopulation > 0:
            sorted_agents: list[int] = sorted(
                self.enviroment.agents_alive,
                key=lambda agent: self.enviroment.public_resources[agent],
            )
            agents_to_remove: list[int] = sorted_agents[:overpopulation]
            for agent in agents_to_remove:
                self.enviroment.public_resources[agent] = 0

        self.enviroment.agents_alive = [
            agent
            for agent in self.enviroment.agents_alive
            if self.enviroment.public_resources[agent] > 0
        ]

    def add_agents(self, new_agents):

        new_agents_count: int = len(new_agents)

        # Add the new agents to the list of alive agents
        self.enviroment.agents_alive.extend(
            list(
                range(
                    len(self.enviroment.agents),
                    len(self.enviroment.agents) + new_agents_count,
                )
            )
        )

        # Add the new agents to the public resources with a little variation
        agent_type_avg_resources = self.actual_summary_data["agent_type_avg_resources"]
        for new_agent in new_agents:
            agent_type = type(new_agent).__name__
            avg_resources = agent_type_avg_resources.get(agent_type, 450)
            variation = random.uniform(-0.1, 0.1)  # 10% variation
            self.enviroment.public_resources.append(
                int(avg_resources * (1 + variation))
            )

        # Extend the trust matrix for existing agents
        for row in self.enviroment.trust_matrix:
            row.extend([50] * new_agents_count)

        # Add new rows for the new agents
        self.enviroment.trust_matrix.extend(
            [[50] * (len(self.enviroment.agents) + new_agents_count)] * new_agents_count
        )

        # Add the new agents to the list
        self.enviroment.agents.extend(new_agents)

        self.enviroment.generation += 1

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

    def decide(self, new_event: Event, verbose) -> None:
        if verbose:
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

                if action == Action.EXPLOIT:
                    self.total_thefts += 1

                self.set_reputation(agent, action)
                if verbose:
                    print(
                        "\t",
                        agent,
                        ": ",
                        action,
                        "(",
                        self.enviroment.agents[agent],
                        ")",
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
        if verbose:
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
        ResentfulAgent,
        ExploteAgent,
    ]
    return [random.choice(agent_classes)(i) for i in range(length)]
