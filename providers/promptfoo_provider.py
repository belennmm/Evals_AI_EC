"""Provider temporal para validar la conexión entre Promptfoo y Python."""


def call_api(prompt: str, options: dict, context: dict) -> dict:


    respuesta = f"Prompt recibido correctamente: {prompt}"

    return {
        "output": respuesta
    }


if __name__ == "__main__":
    resultado = call_api(
        "Prueba de conexión",
        {"config": {}},
        {"vars": {}}
    )

    print(resultado)
