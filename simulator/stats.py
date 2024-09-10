import matplotlib.pyplot as plt
import numpy as np

from enviroment import Enviroment, EnviromentInfo
from event_generator import Event
from utils import Action


class Stats:
    def __init__(self, environment: Enviroment):
        self.environment = environment
        # Colores asignados a cada tipo de agente
        self.agent_colors = {
            "ABRAgent": "blue",
            "PusilanimeAgent": "green",
            "ThiefAgent": "red",
            "TipForTapAgent": "orange",
            "TipForTapSecureAgent": "brown",
            "RandomAgent": "purple",
            "SearchAgent": "yellow",
        }
        self.fig, self.ax = plt.subplots(figsize=(10, 6))

    def plot_agent_resources(self, event: Event):
        self.ax.clear()
        agents_alive = self.environment.agents_alive
        agent_resources = []
        agent_types = []
        agent_colors = []
        action_colors = []

        for agent_id in agents_alive:
            agent = self.environment.agents[agent_id]
            agent_resources.append(self.environment.public_resources[agent_id])
            agent_type = type(agent).__name__
            agent_types.append(agent_type)
            agent_colors.append(self.agent_colors.get(agent_type, "gray"))

            # Obtener la acción del agente y definir el color del punto
            if agent_id in self.environment.log[event]:
                action = self.environment.log[event][agent_id]
                if action == Action.COOP:
                    action_colors.append("green")
                elif action == Action.EXPLOIT:
                    action_colors.append("red")
                elif action == Action.INACT:
                    action_colors.append("gray")
            else:
                action_colors.append("black")

        bars = self.ax.bar(
            range(len(agents_alive)), agent_resources, color=agent_colors
        )
        self.ax.set_xlabel("Agent ID")
        self.ax.set_ylabel("Resources")
        self.ax.set_title(f"Resources per Agent on Day {self.environment.day}")
        self.ax.set_xticks(range(len(agents_alive)))
        self.ax.set_xticklabels(agents_alive, rotation=45)

        # Añadir puntos encima de las barras
        for i, bar in enumerate(bars):
            self.ax.plot(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                "o",
                color=action_colors[i],
                markersize=4,
            )

        # Calcular el promedio de recursos para cada tipo de agente
        type_resource_sum = {key: 0 for key in self.agent_colors.keys()}
        type_agent_count = {key: 0 for key in self.agent_colors.keys()}

        for agent_id in agents_alive:
            agent = self.environment.agents[agent_id]
            agent_type = type(agent).__name__
            type_resource_sum[agent_type] += self.environment.public_resources[agent_id]
            type_agent_count[agent_type] += 1

        type_resource_avg = {
            key: (
                type_resource_sum[key] / type_agent_count[key]
                if type_agent_count[key] > 0
                else 0
            )
            for key in self.agent_colors.keys()
        }

        # Añadir líneas horizontales discontínuas para cada tipo de agente
        for agent_type, color in self.agent_colors.items():
            if type_agent_count[agent_type] > 0:
                avg = type_resource_avg[agent_type]
                self.ax.axhline(
                    y=avg,
                    color=color,
                    linestyle="--",
                    linewidth=2,
                    label=f"{agent_type} Avg",
                )

        self.ax.legend()

        # Actualizar la gráfica sin cerrar la ventana
        plt.pause(0.4)


# Ejemplo de uso:
# Suponiendo que 'env' es una instancia de la clase Environment
# stats = Stats(env)
# stats.update()
