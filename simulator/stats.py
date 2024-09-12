import matplotlib.pyplot as plt
import numpy as np

from enviroment import Enviroment, EnviromentInfo
from event_generator import Event
from utils import Action


class Stats:
    def __init__(self, environment: Enviroment):
        self.environment = environment
        self.days = []
        self.avg_resources_per_day = []

        # Colores asignados a cada tipo de agente
        self.agent_colors = {
            "ABRAgent": "blue",
            "PusilanimeAgent": "green",
            "ThiefAgent": "red",
            "TipForTapAgent": "orange",
            "TipForTapSecureAgent": "brown",
            "RandomAgent": "purple",
            "SearchAgent": "yellow",
            "Resentful": "magenta",
        }

        # Crear dos subplots (una para los recursos por agente y otra para la media de recursos por día)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))

    def plot_agent_resources(self, event: Event):
        self.ax1.clear()
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

        bars = self.ax1.bar(
            range(len(agents_alive)), agent_resources, color=agent_colors
        )
        self.ax1.set_xlabel("Agent ID")
        self.ax1.set_ylabel("Resources")
        self.ax1.set_title(f"Resources per Agent on Day {self.environment.day}")
        self.ax1.set_xticks(range(len(agents_alive)))
        self.ax1.set_xticklabels(agents_alive, rotation=45)

        # Añadir puntos encima de las barras
        for i, bar in enumerate(bars):
            self.ax1.plot(
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
                self.ax1.axhline(
                    y=avg,
                    color=color,
                    linestyle="--",
                    linewidth=2,
                    label=f"{agent_type} Avg",
                )

        self.ax1.legend()

        # Actualizar gráfica de la media de recursos contra el día
        self.update_avg_resources()

        # Actualizar ambas gráficas sin cerrar la ventana
        plt.pause(0.4)

    def update_avg_resources(self):
        # Calcular el promedio de recursos de todos los agentes vivos
        agents_alive = self.environment.agents_alive
        total_resources = sum(
            [self.environment.public_resources[agent_id] for agent_id in agents_alive]
        )
        avg_resources = total_resources / len(agents_alive) if agents_alive else 0

        # Actualizar los datos de días y media de recursos
        self.days.append(self.environment.day)
        self.avg_resources_per_day.append(avg_resources)

        # Graficar la media de recursos por día
        self.ax2.clear()
        self.ax2.plot(self.days, self.avg_resources_per_day, marker="o", color="blue")
        self.ax2.set_xlabel("Day")
        self.ax2.set_ylabel("Average Resources")
        self.ax2.set_title("Average Resources per Day")
        self.ax2.grid(True)
