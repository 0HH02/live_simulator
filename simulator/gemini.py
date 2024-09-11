import PyPDF2
import os
from typing import Literal, LiteralString
import google.generativeai as genai
from google.generativeai.types.generation_types import GenerateContentResponse


def make_history() -> LiteralString:
    genai.configure(api_key="AIzaSyCpQ7M42a7fsZtqCoeYrZCJDVOn-9GexP0")
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    def leer_libro(path):
        texto = ""
        if path.endswith(".pdf"):
            with open(path, "rb") as file:
                lector = PyPDF2.PdfReader(file)
                for pagina in range(len(lector.pages)):
                    texto += lector.pages[pagina].extract_text()
        elif path.endswith(".txt"):
            with open(path, "r", encoding="ISO-8859-1") as file:
                texto = file.read()
        else:
            raise ValueError("Formato de archivo no soportado.")
        return texto

    generation_config = genai.GenerationConfig(
        temperature=0.7  # Ajusta la temperatura según tus preferencias
    )
    texto: str = leer_libro("log.txt")

    history: list[dict[str, str]] = [
        {
            "role": "system",
            "content": f"""Estoy simulando una sociedad. En mi simulación hay atributos como la: cantidad de recursos que se pierden por día. Hay aldeanos que tienen que sobrevivir juntos y cada día se lleva a cabo un evento, este puede ser de tipo especial en los que todos ganan o pierden recursos por igual o de tipo cooperativo donde se hacen grupos con los aldeanos y tienen que decidir si cooperar, robar o mantenerse al margen del equipo en el que les tocó. Esto se resuelve con una especie de juego del prisionero adaptado al grupo y dependiendo de las decisiones que tomen los integrantes se reparten los recursos en el equipo. Si todos cooperan ganan todos los recursos disponibles, si todos se mantienen al margen ganan solo el 80% de los recursos y si todos roban ganan 0 recursos, cualquier distribución de por medio causará una repartición intermedia dependiendo de sus decisiones. El aldeano que se quede sin recursos muere. Cada aldeano tiene una reputación que inicialmente es de 50, si roban baja 30, si coopera sube 10 y si se mantiene al margen sube 3. Si tu reputación baja de 30 tienes una probabilidad de que en este turno no te dejen jugar en el evento cooperativo. Si en un evento cooperativo los recursos a repartir son negativos significa que es una catástrofe que a la que están intentando aminorar el daño, esto significa que todos van a perder recursos pero si todos cooperan pierden la menor cantidad de recursos posible.
            Te voy a pasar el log de la simulación y tienes que inventar una historia alrededor de la simulación que debe tener política, romance, aventura, personajes principales y personajes icónicos. Sé creativa.Tenemos varios tipos de agentes:
            Thief (Siempre roba)
            Pusilanime (Siempre coopera)
            Random (Toma decisiones aleatoreamente)
            TipForTap (Juega lo que la mayoría de su grupo jugó la última vez que jugó con él)
            TipForTapSecure (lo mismo que el anterior pero este no roba, en cambio se mantiene al margen)
            ARB (Mantiene una memoria de la reputación de cada agente contra el que juega, promedia las reputaciones y si es mayor que 55 coopera y si no se mantiene al margen)
            Search (Simula 5 jugadas en el futuro y juega la decisión que maximice los recursos)
            Tienen que verse los días desde el 1ro hasta el último pero puedes saltarte algunos si no los vevs relevante para la historia. Es fundamental que se vea la correlacion entre el Log y la narracion, donde se especifique el dia en concreto del que se habla""",
        },
        {
            "role": "user",
            "content": f"Log: {texto}",
        },
    ]

    response: GenerateContentResponse = model.generate_content(
        [
            "\n".join(
                [f"{message['role']}: {message['content']}" for message in history]
            )
        ],
        generation_config=generation_config,
    )

    return response.text
