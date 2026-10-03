"""
safety_tool.py

Evalúa criterios de seguridad para saltos de paracaídas basado en datos climáticos.

Responsabilidades:
- Recibir datos climáticos (dict producido por weather_tool.py)
- Aplicar criterios de seguridad definidos
- Determinar estado general (IDEAL, MARGINAL, PROHIBIDO)
- Proporcionar motivos claros de la clasificación
- Indicar restricciones aplicables

NO contiene:
- Consultas de red
- Lógica de agentes
- Decisions sobre calendarización

Criterios de Seguridad:
- Velocidad viento: <20 IDEAL, 20-28 MARGINAL, >28 PROHIBIDO
- Ráfagas: >35 PROHIBIDO
- Precipitación: >0 PROHIBIDO
- Cobertura nubes: <30 IDEAL, 30-75 MARGINAL, >75 PROHIBIDO
- Temperatura: solo informativa, sin umbral
"""

from typing import Dict, List


def evaluar_seguridad(datos_clima: Dict) -> Dict:
    """
    Evalúa si es seguro realizar un salto de paracaídas según datos climáticos.
    
    Args:
        datos_clima: Dict con estructura:
        {
            "fecha": "2026-09-15",
            "temperatura_2m": 24.5,
            "precipitacion": 0.0,
            "cobertura_nubes": 45,
            "velocidad_viento": 18.2,
            "rachas_viento": 32.1,
        }
    
    Returns:
        Dict con estructura:
        {
            "estado": "IDEAL" | "MARGINAL" | "PROHIBIDO",
            "puede_saltar": True | False,
            "restriccion": None | "Solo tándem experimentado" | "No se permite realizar el salto",
            "motivos": [list of strings],
            "condiciones": {
                "velocidad_viento": "IDEAL" | "MARGINAL" | "PROHIBIDO",
                "rachas_viento": "OK" | "PROHIBIDO",
                "precipitacion": "OK" | "PROHIBIDO",
                "cobertura_nubes": "IDEAL" | "MARGINAL" | "PROHIBIDO",
                "temperatura": float (informativa)
            }
        }
    
    Lógica de estado general:
    - Si CUALQUIER criterio es PROHIBIDO -> estado PROHIBIDO
    - Si ninguno es PROHIBIDO pero AL MENOS UNO es MARGINAL -> estado MARGINAL
    - Si TODOS están en rango IDEAL -> estado IDEAL
    """
    
    estado_general = "IDEAL"
    motivos: List[str] = []
    condiciones: Dict = {}
    
    # criterio 1
    vel_viento = datos_clima["velocidad_viento"]
    
    if vel_viento > 28:
        estado_general = "PROHIBIDO"
        motivos.append(
            f"Velocidad de viento PROHIBIDA: {vel_viento} km/h (> 28 km/h). "
            f"Muy difícil de controlar el salto."
        )
        condiciones["velocidad_viento"] = "PROHIBIDO"
    elif vel_viento >= 20:
        if estado_general != "PROHIBIDO":
            estado_general = "MARGINAL"
        motivos.append(
            f"Velocidad de viento MARGINAL: {vel_viento} km/h (20-28 km/h). "
            f"Solo para tándem experimentado."
        )
        condiciones["velocidad_viento"] = "MARGINAL"
    else:
        motivos.append(
            f"Velocidad de viento IDEAL: {vel_viento} km/h (< 20 km/h). "
            f"Condición óptima."
        )
        condiciones["velocidad_viento"] = "IDEAL"
    
    # criterio 2
    rachas = datos_clima["rachas_viento"]
    
    if rachas > 35:
        estado_general = "PROHIBIDO"
        motivos.append(
            f"Ráfagas PROHIBIDAS: {rachas} km/h (> 35 km/h). "
            f"Peligro crítico de estabilidad."
        )
        condiciones["rachas_viento"] = "PROHIBIDO"
    else:
        motivos.append(
            f"Ráfagas OK: {rachas} km/h (≤ 35 km/h)."
        )
        condiciones["rachas_viento"] = "OK"
    
    # criterio 3
    precipitacion = datos_clima["precipitacion"]
    
    if precipitacion > 0.0:
        estado_general = "PROHIBIDO"
        motivos.append(
            f"Precipitación PROHIBIDA: {precipitacion} mm (> 0 mm). "
            f"Lluvia daña el equipo y lastima la piel."
        )
        condiciones["precipitacion"] = "PROHIBIDO"
    else:
        motivos.append(
            f"Precipitación OK: {precipitacion} mm (sin lluvia)."
        )
        condiciones["precipitacion"] = "OK"
    
    # criterio 4
    nubes = datos_clima["cobertura_nubes"]
    
    if nubes > 75:
        estado_general = "PROHIBIDO"
        motivos.append(
            f"Cobertura de nubes PROHIBIDA: {nubes}% (> 75%). "
            f"Techo de nubes bajo impide reglas de vuelo visual."
        )
        condiciones["cobertura_nubes"] = "PROHIBIDO"
    elif nubes >= 30:
        if estado_general != "PROHIBIDO":
            estado_general = "MARGINAL"
        motivos.append(
            f"Cobertura de nubes MARGINAL: {nubes}% (30-75%). "
            f"Nubes dispersas, visibilidad limitada."
        )
        condiciones["cobertura_nubes"] = "MARGINAL"
    else:
        motivos.append(
            f"Cobertura de nubes IDEAL: {nubes}% (< 30%). "
            f"Visibilidad clara."
        )
        condiciones["cobertura_nubes"] = "IDEAL"
    
    # temperatura (solo informativa)
    temperatura = datos_clima["temperatura_2m"]
    condiciones["temperatura_2m"] = temperatura
    motivos.append(f"Temperatura: {temperatura}°C (informativa, sin criterio de seguridad).")
    
    # determinar restricciones y si puede saltar
    if estado_general == "PROHIBIDO":
        restriccion = "No se permite realizar el salto"
        puede_saltar = False
    elif estado_general == "MARGINAL":
        restriccion = "Solo tándem experimentado"
        puede_saltar = True
    else:  # IDEAL
        restriccion = None
        puede_saltar = True
    
    # resultado final 
    return {
        "estado": estado_general,
        "puede_saltar": puede_saltar,
        "restriccion": restriccion,
        "motivos": motivos,
        "condiciones": condiciones,
    }


# pruebas unitarias

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PRUEBAS: safety_tool.py")
    print("="*70 + "\n")
    
    # Prueba 1 condiciones ideales 
    print("PRUEBA 1 condiciones Ideales")
    datos_ideal = {
        "fecha": "2026-09-15",
        "temperatura_2m": 24.5,
        "precipitacion": 0.0,
        "cobertura_nubes": 25,
        "velocidad_viento": 15.0,
        "rachas_viento": 22.0,
    }
    resultado = evaluar_seguridad(datos_ideal)
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    print(f"Motivos:")
    for motivo in resultado['motivos']:
        print(f"  • {motivo}")
    print()
    
    # Prueba 2 condiciones marginales 
    print("PRUEBA 2 condiciones MARGINALES")
    datos_marginal = {
        "fecha": "2026-09-16",
        "temperatura_2m": 22.0,
        "precipitacion": 0.0,
        "cobertura_nubes": 50,
        "velocidad_viento": 24.0,
        "rachas_viento": 28.0,
    }
    resultado = evaluar_seguridad(datos_marginal)
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    print(f"Motivos:")
    for motivo in resultado['motivos']:
        print(f"  • {motivo}")
    print()
    
    # Prueba 3 condiciones prohibidas
    print("[PRUEBA 3] Condiciones PROHIBIDAS (viento > 28)")
    datos_prohibido_viento = {
        "fecha": "2026-09-17",
        "temperatura_2m": 20.0,
        "precipitacion": 0.0,
        "cobertura_nubes": 40,
        "velocidad_viento": 32.0,
        "rachas_viento": 38.0,
    }
    resultado = evaluar_seguridad(datos_prohibido_viento)
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    print(f"Motivos:")
    for motivo in resultado['motivos']:
        print(f"  • {motivo}")
    print()
    
    # Prueba 4 condiciones prohibidas 
    print("PRUEBA 4 condiciones PROHIBIDAS")
    datos_prohibido_lluvia = {
        "fecha": "2026-09-18",
        "temperatura_2m": 23.0,
        "precipitacion": 5.5,
        "cobertura_nubes": 90,
        "velocidad_viento": 18.0,
        "rachas_viento": 25.0,
    }
    resultado = evaluar_seguridad(datos_prohibido_lluvia)
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    print(f"Motivos:")
    for motivo in resultado['motivos']:
        print(f"  • {motivo}")
    print()
    
    # Prueba 5 condiciones
    print("PRUEBA 5 condiciones PROHIBIDAS")
    datos_prohibido_nubes = {
        "fecha": "2026-09-19",
        "temperatura_2m": 21.0,
        "precipitacion": 0.0,
        "cobertura_nubes": 88,
        "velocidad_viento": 16.0,
        "rachas_viento": 20.0,
    }
    resultado = evaluar_seguridad(datos_prohibido_nubes)
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    print(f"Motivos:")
    for motivo in resultado['motivos']:
        print(f"  • {motivo}")
    
    print("\n" + "="*70 + "\n")