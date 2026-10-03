"""
test_shared_tools.py

Pruebas manuales integradas para weather_tool.py y safety_tool.py.

Casos de prueba:
1. Fecha válida + clima ideal
2. Fecha fuera de rango (rechazo)
3. Clima marginal
4. Clima prohibido (múltiples criterios)
5. Validaciones de formato

Ejecutar con: python test_shared_tools.py
"""

from datetime import datetime, timedelta
from shared import weather_tool
from shared import safety_tool
from datetime import datetime, timedelta

from shared.weather_tool import consultar_clima_open_meteo
from shared.safety_tool import evaluar_seguridad


def test_weather_tool_validacion():
    """Prueba validaciones de weather_tool."""
    print("\n" + "="*70)
    print("TEST: Validaciones de weather_tool.py")
    print("="*70 + "\n")
    
    # Test 1 formato inválido
    print("[1] Formato inválido: 15-09-2026")
    es_valida, error = weather_tool.validar_fecha("15-09-2026")
    assert not es_valida, "Debería rechazar formato inválido"
    print(f"Rechazado correctamente: {error}\n")
    
    # Test 2 fecha pasada
    print("[2] Fecha pasada: ayer")
    fecha_pasada = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    es_valida, error = weather_tool.validar_fecha(fecha_pasada)
    assert not es_valida, "Debería rechazar fecha pasada"
    print(f"Rechazado correctamente: {error}\n")
    
    # Test 3 fecha muy lejana 
    print("[3] Fecha muy lejana (20 días adelante)")
    fecha_lejana = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
    es_valida, error = weather_tool.validar_fecha(fecha_lejana)
    assert not es_valida, "Debería rechazar fecha > 16 días"
    print(f"Rechazado correctamente: {error}\n")
    
    # Test 4 fecha
    print("[4] Fecha válida (5 días adelante)")
    fecha_valida = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    es_valida, error = weather_tool.validar_fecha(fecha_valida)
    assert es_valida, "Debería aceptar fecha válida"
    print(f"Aceptado correctamente: {fecha_valida}\n")


def test_safety_tool_ideal():
    """Prueba safety_tool con condiciones ideales."""
    print("\n" + "="*70)
    print("TEST: safety_tool.py condiciones ideales")
    print("="*70 + "\n")
    
    datos = {
        "fecha": "2026-09-15",
        "temperatura_2m": 24.5,
        "precipitacion": 0.0,
        "cobertura_nubes": 25,
        "velocidad_viento": 15.0,
        "rachas_viento": 22.0,
    }
    
    resultado = safety_tool.evaluar_seguridad(datos)
    
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    
    assert resultado['estado'] == "IDEAL", "Debería ser IDEAL"
    assert resultado['puede_saltar'] is True, "Debería permitir salto"
    assert resultado['restriccion'] is None, "No debería haber restricción"
    
    print("\nTest pasado\n")


def test_safety_tool_marginal():
    """Prueba safety_tool con condiciones marginales."""
    print("\n" + "="*70)
    print("TEST: safety_tool.py - Condiciones MARGINALES")
    print("="*70 + "\n")
    
    datos = {
        "fecha": "2026-09-16",
        "temperatura_2m": 22.0,
        "precipitacion": 0.0,
        "cobertura_nubes": 50,
        "velocidad_viento": 24.0,
        "rachas_viento": 28.0,
    }
    
    resultado = safety_tool.evaluar_seguridad(datos)
    
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    
    assert resultado['estado'] == "MARGINAL", "Debería ser MARGINAL"
    assert resultado['puede_saltar'] is True, "Debería permitir salto"
    assert resultado['restriccion'] == "Solo tándem experimentado", "Debería indicar restricción"
    
    print("\nTest pasado\n")


def test_safety_tool_prohibido():
    """Prueba safety_tool con condiciones prohibidas."""
    print("\n" + "="*70)
    print("TEST: safety_tool.py - Condiciones PROHIBIDAS")
    print("="*70 + "\n")
    
    datos = {
        "fecha": "2026-09-17",
        "temperatura_2m": 20.0,
        "precipitacion": 2.5,
        "cobertura_nubes": 40,
        "velocidad_viento": 32.0,
        "rachas_viento": 28.0,
    }
    
    resultado = safety_tool.evaluar_seguridad(datos)
    
    print(f"Estado: {resultado['estado']}")
    print(f"Puede saltar: {resultado['puede_saltar']}")
    print(f"Restricción: {resultado['restriccion']}")
    
    assert resultado['estado'] == "PROHIBIDO", "Debería ser PROHIBIDO"
    assert resultado['puede_saltar'] is False, "No debería permitir salto"
    assert resultado['restriccion'] == "No se permite realizar el salto", "Debería indicar prohibición"
    
    print("\nTest pasado\n")


def test_integration_weather_safety():
    """Prueba integración entre weather_tool y safety_tool (con datos simulados)."""
    print("\n" + "="*70)
    print("TEST: Integración weather_tool + safety_tool (simulado)")
    print("="*70 + "\n")
    
    print("Simular: Consultar clima para fecha válida, luego evaluar seguridad\n")
    
    # simular respuesta de Open-Meteo para fecha válida
    fecha_consulta = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    datos_simulados = {
        "fecha": fecha_consulta,
        "temperatura_2m": 23.0,
        "precipitacion": 0.0,
        "cobertura_nubes": 35,
        "velocidad_viento": 19.5,
        "rachas_viento": 28.0,
    }
    
    print(f"Fecha consultada: {fecha_consulta}")
    print(f"Datos climáticos (simulados): {datos_simulados}\n")
    
    
    resultado = safety_tool.evaluar_seguridad(datos_simulados)
    
    print(f"Resultado de seguridad:")
    print(f"  Estado: {resultado['estado']}")
    print(f"  Puede saltar: {resultado['puede_saltar']}")
    print(f"  Restricción: {resultado['restriccion']}")
    
    assert resultado['estado'] == "MARGINAL", "Debería ser MARGINAL (nubes y viento)"
    
    print("\nTest pasado\n")

def test_integracion_real():
    print("\n" + "=" * 70)
    print("TEST: Integración REAL Open-Meteo + safety_tool")
    print("=" * 70 + "\n")

    fecha_prueba = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    print(f"Consultando Open-Meteo para: {fecha_prueba}")

    try:
       
        datos_clima = consultar_clima_open_meteo(fecha_prueba)

        print("\nDatos climáticos reales:")
        print(f"  Fecha: {datos_clima['fecha']}")
        print(f"  Temperatura: {datos_clima['temperatura_2m']} °C")
        print(f"  Precipitación: {datos_clima['precipitacion']} mm")
        print(f"  Cobertura de nubes: {datos_clima['cobertura_nubes']} %")
        print(f"  Velocidad de viento: {datos_clima['velocidad_viento']} km/h")
        print(f"  Ráfagas de viento: {datos_clima['rachas_viento']} km/h")

        
        resultado = evaluar_seguridad(datos_clima)

        print("\nResultado de seguridad:")
        print(f"  Estado: {resultado['estado']}")
        print(f"  Puede saltar: {resultado['puede_saltar']}")
        print(f"  Restricción: {resultado['restriccion']}")

        print("\nMotivos:")
        for motivo in resultado["motivos"]:
            print(f"  • {motivo}")

        print("\nTest de integración REAL pasado")

    except Exception as e:
        print(f"\nERROR en integración real: {e}")
        raise


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("SUITE DE PRUEBAS: weather_tool.py + safety_tool.py")
    
    try:
        test_weather_tool_validacion()
        test_safety_tool_ideal()
        test_safety_tool_marginal()
        test_safety_tool_prohibido()
        test_integration_weather_safety()
        test_integracion_real()
        
        print("\n" + "█"*70)
        print("TODAS LAS PRUEBAS PASARON")
        
    except AssertionError as e:
        print(f"\nError en test: {e}\n")
        raise
    except Exception as e:
        print(f"\nError inesperado: {e}\n")
        raise


