import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

from enviroment import Enviroment, EnviromentInfo
from event_generator import Event
from utils import Action


class Stats:
    def __init__(self, environment: Enviroment):
        self.environment = environment
        self.days = []
        self.avg_resources_per_day = []
        self.total_thefts = 0  # Total de robos acumulados
        self.thefts_per_day = []  # Robos por día
        self.people_count_per_day = []

        # Colores asignados a cada tipo de agente
        self.agent_colors = {
            "ABRAgent": "blue",
            "PusilanimeAgent": "green",
            "ThiefAgent": "red",
            "TipForTapAgent": "orange",
            "TipForTapSecureAgent": "brown",
            "RandomAgent": "purple",
            "SearchAgent": "yellow",
            "ResentfulAgent": "magenta",
            "ExploteAgent": "cyan",
        }

        # Activar el modo interactivo
        plt.ion()

        # Definir estilo de gráfico
        plt.style.use("Solarize_Light2")  # Cambiado a 'ggplot' para evitar el error

        # Crear una figura con subplots
        self.fig, self.axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 8))
        self.fig.tight_layout(pad=4.0)

        # Asignar cada subplot a una variable para facilitar el acceso
        self.ax1 = self.axes[0, 0]
        self.ax2 = self.axes[0, 1]
        self.ax3 = self.axes[0, 2]
        self.ax4 = self.axes[1, 0]
        self.ax5 = self.axes[1, 1]
        self.ax6 = self.axes[
            1, 2
        ]  # Nuevo subplot para la distribución de recursos por tipo

        # Configurar los títulos iniciales
        self.ax1.set_title("Recursos por Agente")
        self.ax2.set_title("Media de Recursos por Día")
        self.ax3.set_title("Distribución de Agentes (Vivos)")
        self.ax4.set_title("Cantidad de Personas en el Tiempo")
        self.ax5.set_title("Recursos Promedio por Tipo de Agente")
        self.ax6.set_title("Recursos Totales por Tipo de Agente")  # Título actualizado

        # Inicializar variables adicionales
        self.type_resource_history = {key: [] for key in self.agent_colors.keys()}
        self.type_counts_history = {key: [] for key in self.agent_colors.keys()}

        # Inicializar la funcionalidad de pausa
        self.paused = False

        # Añadir botón de pausa
        pause_ax = self.fig.add_axes(
            [0.45, 0.0, 0.1, 0.04]
        )  # Ajusta la posición y tamaño según sea necesario
        self.pause_button = Button(pause_ax, "Pausar")
        self.pause_button.on_clicked(self.toggle_pause)

    def toggle_pause(self, event):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.label.set_text("Continuar")
        else:
            self.pause_button.label.set_text("Pausar")

    def plot_agent_resources(self, event: Event, environment: Enviroment):
        # Esperar si está en pausa
        while self.paused:
            plt.pause(0.1)

        # Actualizar Gráfica 1: Recursos por Agente
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
        self.ax1.set_xlabel("ID del Agente")
        self.ax1.set_ylabel("Recursos")
        self.ax1.set_title(f"Recursos por Agente en el Día {environment.day}")
        self.ax1.set_xticks(range(len(agents_alive)))
        self.ax1.set_xticklabels(agents_alive, rotation=45)

        # Añadir puntos encima de las barras
        for i, bar in enumerate(bars):
            self.ax1.plot(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                "o",
                color=action_colors[i],
                markersize=6,
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

        # Actualizar el historial de recursos por tipo
        for agent_type in self.agent_colors.keys():
            self.type_resource_history[agent_type].append(type_resource_avg[agent_type])
            self.type_counts_history[agent_type].append(type_agent_count[agent_type])

        # Añadir líneas horizontales discontinuas para cada tipo de agente
        for agent_type, color in self.agent_colors.items():
            if type_agent_count[agent_type] > 0:
                avg = type_resource_avg[agent_type]
                self.ax1.axhline(
                    y=avg,
                    color=color,
                    linestyle="--",
                    linewidth=2,
                    label=f"{agent_type} Promedio",
                )

        self.ax1.legend()

        # Actualizar Gráficas
        self.update_avg_resources(environment)
        self.update_agent_counts(environment)
        self.update_type_resources(environment)
        self.update_resource_distribution(environment, type_resource_sum)

        # Mostrar los indicadores de robos en la Gráfica 1
        self.show_theft_stats()

        # Dibujar las figuras
        self.fig.canvas.draw()

        # Pausar brevemente para actualizar
        plt.pause(0.01)

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

        # Almacenar el número de personas vivas
        self.people_count_per_day.append(len(agents_alive))

        # Graficar la media de recursos por día en ax2
        self.ax2.clear()
        self.ax2.plot(self.days, self.avg_resources_per_day, marker="o", color="blue")
        self.ax2.set_xlabel("Día")
        self.ax2.set_ylabel("Recursos Promedio")
        self.ax2.set_title("Media de Recursos por Día")
        self.ax2.grid(True)

        # Graficar el número de personas vivas por día en ax4
        self.ax4.clear()
        self.ax4.plot(self.days, self.people_count_per_day, marker="o", color="green")
        self.ax4.set_xlabel("Día")
        self.ax4.set_ylabel("Número de Personas")
        self.ax4.set_title("Cantidad de Personas en la Sociedad a lo Largo del Tiempo")
        self.ax4.grid(True)

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

            self.ax3.set_title("Distribución de Agentes (Vivos)")

    def update_type_resources(self, environment: Enviroment):
        # Graficar los recursos promedio por tipo de agente a lo largo del tiempo en ax5
        self.ax5.clear()
        for agent_type, color in self.agent_colors.items():
            if any(self.type_resource_history[agent_type]):
                self.ax5.plot(
                    self.days,
                    self.type_resource_history[agent_type],
                    label=agent_type,
                    color=color,
                )

        self.ax5.set_xlabel("Día")
        self.ax5.set_ylabel("Recursos Promedio")
        self.ax5.set_title("Recursos Promedio por Tipo de Agente")
        self.ax5.legend()
        self.ax5.grid(True)

    def update_resource_distribution(self, environment: Enviroment, type_resource_sum):
        # Crear gráfico de pastel mostrando los recursos totales por tipo de agente
        self.ax6.clear()

        # Filtrar los tipos de agentes que tienen recursos (están vivos)
        types_with_resources = []
        total_resources = []
        colors = []

        for agent_type, resource_sum in type_resource_sum.items():
            if resource_sum > 0:
                types_with_resources.append(agent_type)
                total_resources.append(resource_sum)
                colors.append(self.agent_colors[agent_type])

        # Asegúrate de que haya recursos para graficar
        if total_resources:
            self.ax6.pie(
                total_resources,
                labels=types_with_resources,
                colors=colors,
                autopct=lambda pct: f"{pct:.1f}%" if pct > 0 else "",
                startangle=90,
                counterclock=False,
            )
            self.ax6.set_title("Recursos Totales por Tipo de Agente")
        else:
            self.ax6.set_title("Sin recursos para mostrar")

    def show_theft_stats(self):
        # Eliminar todos los textos anteriores
        for text in self.ax1.texts:
            text.remove()

        # Mostrar los indicadores de robos en la gráfica de recursos
        total_thefts_label = f"Robos Totales: {self.total_thefts}"
        daily_thefts_label = (
            f"Robos Diarios: {self.thefts_per_day[-1]}"
            if self.thefts_per_day
            else "Robos Diarios: 0"
        )

        # Mostrar texto en la gráfica de recursos por agente
        self.ax1.text(
            0.02,
            0.95,
            total_thefts_label,
            fontsize=12,
            color="black",
            weight="bold",
            transform=self.ax1.transAxes,
            verticalalignment="top",
        )
        self.ax1.text(
            0.02,
            0.90,
            daily_thefts_label,
            fontsize=12,
            color="black",
            weight="bold",
            transform=self.ax1.transAxes,
            verticalalignment="top",
        )
