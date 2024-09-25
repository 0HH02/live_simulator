import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import numpy as np


def main():
    # 1. Cargar el archivo CSV
    df = pd.read_csv("simulation_summary.csv")

    # 2. Definir los días de interés
    record_days = [0, 180, 365, 540, 730]

    # 3. Filtrar los datos para los días de interés
    df_filtered = df[df["day"].isin(record_days)]

    # 4. Variables de interés
    continuous_vars = ["avg_resources", "total_thefts", "agents_alive"]
    agent_types = [
        "PusilanimeAgent",
        "ThiefAgent",
        "TipForTapAgent",
        "TipForTapSecureAgent",
        "RandomAgent",
        "ABRAgent",
        "SearchAgent",
        "ResentfulAgent",
        "ExploteAgent",
    ]

    # 5. Estadísticas Descriptivas Generales
    mean_values = df_filtered[continuous_vars].mean()
    std_values = df_filtered[continuous_vars].std()

    print("Medias:")
    print(mean_values)
    print("\nDesviaciones Estándar:")
    print(std_values)

    # 6. Distribución de Agentes por Tipo en Días Clave
    agent_counts = df_filtered[[f"count_{agent}" for agent in agent_types]].mean()
    print("\nMedia de Agentes por Tipo en Días Seleccionados:")
    print(agent_counts)

    # 7. Recursos Promedio por Tipo de Agente en Días Clave
    agent_resources = df_filtered[
        [f"avg_resources_{agent}" for agent in agent_types]
    ].mean()
    print("\nMedia de Recursos por Tipo de Agente en Días Seleccionados:")
    print(agent_resources)

    # 8. Correlaciones entre Variables
    correlation_matrix = df_filtered[
        ["avg_resources", "total_thefts", "agents_alive"]
    ].corr()
    print("\nMatriz de Correlación:")
    print(correlation_matrix)

    # 9. Gráficas

    # a. Evolución del Promedio de Recursos a lo Largo del Tiempo
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="day", y="avg_resources", ci=None)
    plt.title("Evolución del Promedio de Recursos a lo Largo del Tiempo")
    plt.xlabel("Día")
    plt.ylabel("Promedio de Recursos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # b. Cantidad de Agentes Vivos a lo Largo del Tiempo
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="day", y="agents_alive", color="green", ci=None)
    plt.title("Cantidad de Agentes Vivos a lo Largo del Tiempo")
    plt.xlabel("Día")
    plt.ylabel("Cantidad de Agentes Vivos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # c. Distribución de Tipos de Agentes en Días Clave
    num_days = len(record_days)
    fig, axes = plt.subplots(
        1, num_days, figsize=(20, 5), subplot_kw={"aspect": "equal"}
    )

    for idx, day in enumerate(record_days):
        ax = axes[idx]
        data_day = df_filtered[df_filtered["day"] == day]
        counts = data_day[[f"count_{agent}" for agent in agent_types]].sum()
        ax.pie(counts, labels=agent_types, autopct="%1.1f%%", startangle=90)
        ax.set_title(f"Día {day}")

    plt.suptitle("Distribución de Tipos de Agentes en Días Clave", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    # d. Recursos Promedio por Tipo de Agente en Días Clave
    fig, axes = plt.subplots(1, num_days, figsize=(20, 5), sharey=True)

    for idx, day in enumerate(record_days):
        ax = axes[idx]
        data_day = df_filtered[df_filtered["day"] == day]
        avg_resources = data_day[
            [f"avg_resources_{agent}" for agent in agent_types]
        ].mean()
        sns.barplot(x=agent_types, y=avg_resources.values, ax=ax, palette="viridis")
        ax.set_title(f"Día {day}")
        ax.set_ylim(0, max(agent_resources) * 1.2)  # Ajustar el límite y

    plt.suptitle("Recursos Promedio por Tipo de Agente en Días Clave", fontsize=16)
    plt.xlabel("Tipo de Agente")
    plt.ylabel("Recursos Promedio")
    plt.xticks(rotation=45)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    # e. Correlación entre Promedio de Recursos y Agentes Vivos
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x="agents_alive", y="avg_resources")
    plt.title("Correlación entre Agentes Vivos y Promedio de Recursos")
    plt.xlabel("Cantidad de Agentes Vivos")
    plt.ylabel("Promedio de Recursos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # f. Distribución de Robos Totales en la Simulación
    plt.figure(figsize=(10, 6))
    sns.histplot(df["total_thefts"], bins=30, kde=True, color="red")
    plt.title("Distribución de Robos Totales en la Simulación")
    plt.xlabel("Robos Totales")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.show()

    # g. Boxplot de Recursos Promedio por Tipo de Agente
    # Preparar los datos para el boxplot
    resource_columns = [f"avg_resources_{agent}" for agent in agent_types]
    resource_data = df_filtered[resource_columns].melt(
        var_name="Agent_Type", value_name="Avg_Resources"
    )

    # Renombrar los tipos de agentes para que sean más legibles
    resource_data["Agent_Type"] = resource_data["Agent_Type"].str.replace(
        "avg_resources_", ""
    )

    plt.figure(figsize=(12, 6))
    sns.boxplot(x="Agent_Type", y="Avg_Resources", data=resource_data, palette="Set3")
    plt.title("Distribución de Recursos Promedio por Tipo de Agente")
    plt.xlabel("Tipo de Agente")
    plt.ylabel("Recursos Promedio")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # h. Análisis de Correlaciones Detalladas
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        df_filtered[["avg_resources", "total_thefts", "agents_alive"]].corr(),
        annot=True,
        cmap="coolwarm",
    )
    plt.title("Matriz de Correlación entre Variables Clave")
    plt.tight_layout()
    plt.show()

    # i. Evolución de la Media de Recursos por Día
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_filtered, x="day", y="avg_resources", marker="o")
    plt.title("Media de Recursos por Día en Días Clave")
    plt.xlabel("Día")
    plt.ylabel("Media de Recursos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # j. Evolución de la Cantidad de Agentes por Tipo de Agente en Días Clave
    agent_counts_melted = df_filtered.melt(
        id_vars=["simulation_number", "day"],
        value_vars=[f"count_{agent}" for agent in agent_types],
        var_name="Agent_Type",
        value_name="Count",
    )
    agent_counts_melted["Agent_Type"] = agent_counts_melted["Agent_Type"].str.replace(
        "count_", ""
    )

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=agent_counts_melted, x="day", y="Count", hue="Agent_Type", marker="o"
    )
    plt.title("Evolución de la Cantidad de Agentes por Tipo de Agente en Días Clave")
    plt.xlabel("Día")
    plt.ylabel("Cantidad de Agentes")
    plt.legend(title="Tipo de Agente", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # k. Evolución de los Robos Totales a lo Largo del Tiempo
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="day", y="total_thefts", color="orange", marker="o")
    plt.title("Evolución de los Robos Totales a lo Largo del Tiempo")
    plt.xlabel("Día")
    plt.ylabel("Robos Totales")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
