import matplotlib.pyplot as plt
import numpy as np

from enviroment import Enviroment, EnviromentInfo
from event_generator import Event
from utils import Action

import matplotlib.pyplot as plt


class Stats:
    def __init__(self, environment: Enviroment):
        self.environment = environment
        self.days = []
        self.avg_resources_per_day = []
        self.total_thefts = 0  # Total de robos acumulados
        self.thefts_per_day = []  # Robos por día

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

        # Crear un layout con 3 subplots verticales (una debajo de la otra)
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(
            3, 1, figsize=(12, 16)
        )  # Tres subplots verticales

    def plot_agent_resources(self, event: Event, environment: Enviroment):
        self.ax1.clear()
        agents_alive = environment.agents_alive
        agent_resources = []
        agent_types = []
        agent_colors = []
        action_colors = []

        daily_thefts = 0  # Contador de robos diarios

        for agent_id in agents_alive:
            agent = environment.agents[agent_id]
            agent_resources.append(environment.public_resources[agent_id])
            agent_type = type(agent).__name__
            agent_types.append(agent_type)
            agent_colors.append(self.agent_colors.get(agent_type, "gray"))

            # Obtener la acción del agente y definir el color del punto
            if agent_id in environment.log[event]:
                action = environment.log[event][agent_id]
                if action == Action.COOP:
                    action_colors.append("green")
                elif action == Action.EXPLOIT:
                    action_colors.append("red")
                    daily_thefts += 1  # Incrementar contador de robos
                elif action == Action.INACT:
                    action_colors.append("gray")
            else:
                action_colors.append("black")

        # Actualizar el total de robos
        self.total_thefts += daily_thefts
        self.thefts_per_day.append(daily_thefts)

        # Graficar los recursos de los agentes
        bars = self.ax1.bar(
            range(len(agents_alive)), agent_resources, color=agent_colors
        )
        self.ax1.set_xlabel("Agent ID")
        self.ax1.set_ylabel("Resources")
        self.ax1.set_title(f"Resources per Agent on Day {environment.day}")
        # self.ax1.set_xticks(range(len(agents_alive)))
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

        # Calcular el promedio de recursos por tipo de agente
        type_resource_sum = {key: 0 for key in self.agent_colors.keys()}
        type_agent_count = {key: 0 for key in self.agent_colors.keys()}

        for agent_id in agents_alive:
            agent = environment.agents[agent_id]
            agent_type = type(agent).__name__
            type_resource_sum[agent_type] += environment.public_resources[agent_id]
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

        # Actualizar la media de recursos
        self.update_avg_resources(environment)

        # Actualizar los conteos de agentes por tipo
        self.update_agent_counts(environment)

        # Mostrar los indicadores de robos
        self.show_theft_stats()

        # Actualizar todas las gráficas sin cerrar la ventana
        plt.pause(0.4)

    def update_avg_resources(self, environment: Enviroment):
        # Calcular el promedio de recursos de todos los agentes vivos
        agents_alive = environment.agents_alive
        total_resources = sum(
            [environment.public_resources[agent_id] for agent_id in agents_alive]
        )
        avg_resources = total_resources / len(agents_alive) if agents_alive else 0

        # Actualizar los datos de días y media de recursos
        self.days.append(environment.day)
        self.avg_resources_per_day.append(avg_resources)

        # Graficar la media de recursos por día
        self.ax2.clear()
        self.ax2.plot(self.days, self.avg_resources_per_day, marker="o", color="blue")
        self.ax2.set_xlabel("Day")
        self.ax2.set_ylabel("Average Resources")
        self.ax2.set_title("Average Resources per Day")
        self.ax2.grid(True)

    def update_agent_counts(self, environment: Enviroment):
        # Contar la cantidad de agentes vivos por tipo
        agent_count = {key: 0 for key in self.agent_colors.keys()}

        for agent_id in environment.agents_alive:
            agent_type = type(environment.agents[agent_id]).__name__
            if agent_type in agent_count:
                agent_count[agent_type] += 1

        # Crear listas para los tipos de agentes con agentes vivos y sus conteos
        types_with_agents = []
        counts = []
        colors = []

        total_agents_alive = len(environment.agents_alive)

        for agent_type, count in agent_count.items():
            if count > 0:  # Solo mostrar los tipos que tienen agentes vivos
                types_with_agents.append(agent_type)
                counts.append(count)
                colors.append(self.agent_colors[agent_type])

        # Asegúrate de que haya agentes vivos para graficar
        if total_agents_alive > 0:
            self.ax3.clear()
            # Crear el gráfico de pastel
            wedges, texts, autotexts = self.ax3.pie(
                counts,
                labels=types_with_agents,
                colors=colors,
                autopct=lambda pct: (
                    f"{pct:.1f}%" if pct > 0 else ""
                ),  # Mostrar el porcentaje
                startangle=90,
                counterclock=False,
            )

            # Añadir leyenda
            # self.ax3.legend(
            #     wedges,
            #     [
            #         f"{agent_type} ({count})"
            #         for agent_type, count in zip(types_with_agents, counts)
            #     ],
            #     title="Agent Types",
            #     loc="upper right",
            # )

            self.ax3.set_title("Agent Distribution (Alive)")

    def show_theft_stats(self):
        # Mostrar los indicadores de robos
        total_thefts_label = f"Total Thefts: {self.total_thefts}"
        daily_thefts_label = (
            f"Daily Thefts: {self.thefts_per_day[-1]}"
            if self.thefts_per_day
            else "Daily Thefts: 0"
        )

        # Mostrar texto en la gráfica de pastel
        self.ax3.text(
            2, 0, total_thefts_label, fontsize=12, color="black", weight="bold"
        )
        self.ax3.text(
            2, 0.2, daily_thefts_label, fontsize=12, color="black", weight="bold"
        )
