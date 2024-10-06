import random
import csv
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from agents.agent import (
    Agent,
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
from event_generator import ProbabilisticEventGenerator
from simulation import Simulator


def run_single_simulation(args):
    simulation_params, simulation_number = args
    agents = population_random_generator(simulation_params["population_size"])

    event_generator = ProbabilisticEventGenerator(
        good_coop_resource_probability=simulation_params[
            "good_coop_resource_probability"
        ],
        good_time_probabilities=simulation_params["good_time_probabilities"],
        coop_event_probability=simulation_params["coop_event_probability"],
    )

    sim = Simulator(
        agents,
        event_generator,
        lost_per_day=simulation_params["lost_per_day"],
        thief_toleration=simulation_params["thief_toleration"],
        reproduction_rate=simulation_params["reproduction_rate"],
        reproduction_density=simulation_params["reproduction_density"],
        max_population=simulation_params["max_population"],
        global_visible_desitions=simulation_params["global_visible_desitions"],
        noise=simulation_params["noise"],
    )

    result = sim.run(simulation_params["days"], verbose=False)
    summary_data = result["summary_data"]

    # Retornar los resultados incluyendo summary_data
    return {
        "simulation_number": simulation_number,
        "final_day": sim.enviroment.day,
        "agents_alive": len(sim.enviroment.agents_alive),
        "total_resources": sum(sim.enviroment.public_resources),
        "agent_types": [type(agent).__name__ for agent in sim.enviroment.agents],
        "summary_data": summary_data,
    }


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


def save_simulation_summary(simulation_results):
    agent_types_list = [
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

    # Definir los campos del CSV
    fieldnames = [
        "simulation_number",
        "day",
        "avg_resources",
        "total_thefts",
        "agents_alive",
    ]
    for agent_type in agent_types_list:
        fieldnames.append(f"count_{agent_type}")
    for agent_type in agent_types_list:
        fieldnames.append(f"avg_resources_{agent_type}")

    all_rows = []
    for result in simulation_results:
        sim_number = result["simulation_number"]
        summary_data = result["summary_data"]
        for data in summary_data:
            row = {
                "simulation_number": sim_number,
                "day": data["day"],
                "avg_resources": data["avg_resources"],
                "total_thefts": data["total_thefts"],
                "agents_alive": data["agents_alive"],
            }
            # Añadir conteo de agentes por tipo
            for agent_type in agent_types_list:
                count = data["agent_type_counts"].get(agent_type, 0)
                row[f"count_{agent_type}"] = count

            # Añadir recursos promedio por tipo de agente
            for agent_type in agent_types_list:
                avg_res = data["agent_type_avg_resources"].get(agent_type, 0)
                row[f"avg_resources_{agent_type}"] = avg_res

            all_rows.append(row)

    # Guardar en un archivo CSV
    with open("simulation_summary.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)


def main():
    simulation_params = {
        "population_size": 80,
        "good_coop_resource_probability": 0.8,
        "good_time_probabilities": 0.7,
        "coop_event_probability": 0.9,
        "lost_per_day": 100,
        "thief_toleration": 1,
        "reproduction_rate": 10,
        "reproduction_density": 10,
        "max_population": 100,
        "global_visible_desitions": False,
        "noise": 0.1,
        "days": 360,
    }

    num_simulations = 1
    simulation_numbers = list(range(1, num_simulations + 1))

    # Crear una lista de argumentos para mapear
    args_list = [(simulation_params, sim_num) for sim_num in simulation_numbers]

    # Determinar el número de procesos (opcionalmente puedes usar cpu_count())
    num_processes = cpu_count()

    print(
        f"Ejecutando {num_simulations} simulaciones en paralelo usando {num_processes} procesos"
    )

    # Usar Pool para ejecutar simulaciones en paralelo
    run_single_simulation((simulation_params, 1))
    # with Pool(processes=num_processes) as pool:
    #     simulation_results = list(
    #         tqdm(
    #             pool.imap_unordered(run_single_simulation, args_list),
    #             total=num_simulations,
    #         )
    #     )

    # save_simulation_summary(simulation_results)


if __name__ == "__main__":
    main()
