"""
weather_tool.py

Consulta la API gratuita de Open-Meteo para obtener datos climáticos
de la ubicación de Parachute S.A.

Responsabilidades:
- Validar fecha solicitada (formato, rango, no pasada)
- Consultar Open-Meteo API usando parámetro 'hourly'
- Agregar datos horarios al nivel de día
- Devolver datos climáticos en estructura limpia
- Manejar errores de red y API claramente

NO contiene:
- Lógica de decisión de seguridad
- Criterios de aceptabilidad
- Hardcoded API keys

Agregación de datos (de 24 horas a 1 valor por día):
- temperature_2m: promedio (informativa)
- precipitation: suma (acumulado del día)
- cloud_cover: máximo (más conservador)
- wind_speed_10m: máximo (peor momento del día)
- wind_gusts_10m: máximo (peor momento del día)
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics


LATITUDE = 14.013722
LONGITUDE = -90.771611


MAX_FORECAST_DAYS = 16


def validar_fecha(fecha_str: str) -> tuple[bool, str]:
    """
    Valida que la fecha sea válida y esté dentro del rango permitido.
    
    Criterios:
    - Formato: YYYY-MM-DD
    - No puede ser anterior a hoy
    - No puede ser más de 16 días en el futuro
    
    Args:
        fecha_str: Fecha en formato YYYY-MM-DD
    
    Returns:
        (es_valida: bool, error_msg: str)
        Si es válida: (True, "")
        Si no: (False, mensaje de error)
    """
    # Validar formato
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        return False, "Formato de fecha inválido. Use YYYY-MM-DD (ej: 2026-09-15)."
    
    
    hoy = datetime.now().date()
    if fecha.date() < hoy:
        return False, f"La fecha no puede ser anterior a hoy ({hoy})."
    
   
    dias_adelante = (fecha.date() - hoy).days
    if dias_adelante > MAX_FORECAST_DAYS:
        return False, (
            f"Open-Meteo solo proporciona pronóstico hasta 16 días. "
            f"La fecha solicitada está {dias_adelante} días adelante."
        )
    
    return True, ""


def agregar_datos_horarios(datos_horarios: Dict[str, List[float]], fecha_str: str) -> Dict:
    """
    Agrega datos horarios (24 valores) a nivel de día según criterios de seguridad.
    
    Estrategia de agregación:
    - temperature_2m: promedio (solo informativa)
    - precipitation: suma (acumulado del día)
    - cloud_cover: máximo (más conservador para seguridad)
    - wind_speed_10m: máximo (peor momento del día)
    - wind_gusts_10m: máximo (peor momento del día)
    
    Args:
        datos_horarios: Dict con arrays de 24 valores por hora
        fecha_str: Fecha para referencia (YYYY-MM-DD)
    
    Returns:
        Dict con valores agregados
    """

  
    temp_array = datos_horarios.get("temperature_2m", [0])
    precip_array = datos_horarios.get("precipitation", [0])
    nubes_array = datos_horarios.get("cloud_cover", [0])
    viento_array = datos_horarios.get("wind_speed_10m", [0])
    rachas_array = datos_horarios.get("wind_gusts_10m", [0])
    
  
    temperatura_promedio = statistics.mean(temp_array) if temp_array else 0
    precipitacion_suma = sum(precip_array) if precip_array else 0
    nubes_maximo = max(nubes_array) if nubes_array else 0
    viento_maximo = max(viento_array) if viento_array else 0
    rachas_maximo = max(rachas_array) if rachas_array else 0
    
    return {
        "fecha": fecha_str,
        "temperatura_2m": round(temperatura_promedio, 1),
        "precipitacion": round(precipitacion_suma, 1),
        "cobertura_nubes": round(nubes_maximo, 1),
        "velocidad_viento": round(viento_maximo, 1),
        "rachas_viento": round(rachas_maximo, 1),
    }


def consultar_clima_open_meteo(fecha_str: str) -> Dict:
    """
    Consulta Open-Meteo API para obtener datos climáticos de la fecha solicitada.
    
    Usa el parámetro 'hourly' para obtener datos de cada hora del día,
    luego agrega a nivel de día según criterios de seguridad.
    
    Args:
        fecha_str: Fecha en formato YYYY-MM-DD (ej: "2026-09-15")
    
    Returns:
        Dict con estructura:
        {
            "fecha": "2026-09-15",
            "temperatura_2m": 24.5,        # Celsius (promedio)
            "precipitacion": 0.0,          # mm (suma del día)
            "cobertura_nubes": 45,         # % (máximo del día)
            "velocidad_viento": 18.2,      # km/h (máximo del día)
            "rachas_viento": 32.1,         # km/h (máximo del día)
        }
    
    Raises:
        ValueError: Si la fecha es inválida o está fuera de rango
        ConnectionError: Si hay problemas al consultar la API
    """
   
    es_valida, error_msg = validar_fecha(fecha_str)
    if not es_valida:
        raise ValueError(error_msg)
    
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,precipitation,cloud_cover,wind_speed_10m,wind_gusts_10m",
        "start_date": fecha_str,
        "end_date": fecha_str,
        "timezone": "auto"
    }
    
    try:
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
     
        if "hourly" not in data:
            raise ValueError("Respuesta inesperada de Open-Meteo: falta sección 'hourly'")
        
        hourly = data["hourly"]
        
        
        required_params = ["temperature_2m", "precipitation", "cloud_cover", "wind_speed_10m", "wind_gusts_10m"]
        for param in required_params:
            if param not in hourly:
                raise ValueError(f"Parámetro faltante en respuesta: {param}")
        
      
        resultado = agregar_datos_horarios(hourly, fecha_str)
        
        return resultado
    
    except requests.exceptions.Timeout:
        raise ConnectionError(
            "Tiempo de espera agotado al consultar Open-Meteo. "
            "Verifique su conexión a Internet."
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "No se puede conectar a Open-Meteo. "
            "Verifique su conexión a Internet."
        )
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(
            f"Error HTTP al consultar Open-Meteo: {response.status_code} - {response.text}"
        )
    except ValueError as e:
        raise ConnectionError(f"Error al parsear respuesta de Open-Meteo: {str(e)}")
    except Exception as e:
        raise ConnectionError(f"Error inesperado al consultar Open-Meteo: {str(e)}")




if __name__ == "__main__":
    print("\n" + "="*70)
    print("PRUEBAS: weather_tool.py")
    print("="*70 + "\n")
    
 
    print("PRUEBA 1 Consulta de fecha válida")
    fecha_futura = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    try:
        datos = consultar_clima_open_meteo(fecha_futura)
        print(f"Éxito. Datos recuperados para {fecha_futura}:")
        for key, value in datos.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    print("[PRUEBA 2] Fecha fuera de rango (> 16 días)")
    fecha_lejana = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
    try:
        datos = consultar_clima_open_meteo(fecha_lejana)
        print(f"Debería haber fallado pero no lo hizo.")
    except ValueError as e:
        print(f"Validación correcta: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    print()
    
  
    print("PRUEBA 3 Fecha pasada")
    fecha_pasada = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        datos = consultar_clima_open_meteo(fecha_pasada)
        print(f"Debería haber fallado pero no lo hizo.")
    except ValueError as e:
        print(f"Validación correcta: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    print()
    
   
    print("[PRUEBA 4] Formato de fecha inválido")
    try:
        datos = consultar_clima_open_meteo("15-09-2026") 
        print(f"Debería haber fallado pero no lo hizo.")
    except ValueError as e:
        print(f"Validación correcta: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    print("\n" + "--"*70 + "\n")