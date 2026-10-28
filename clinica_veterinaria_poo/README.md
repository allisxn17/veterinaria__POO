# VetCare — Sistema de gestión veterinaria

Aplicación de escritorio en Python con Tkinter, organizada por módulos y basada en POO.

## Requisitos
- Python 3.10 o superior.
- Tkinter instalado (normalmente viene incluido con Python).

## Ejecutar
Desde la carpeta del proyecto:

```bash
python main.py
```

## Módulos
- `models/domain.py`: entidades del dominio, enumeraciones y reglas de negocio.
- `services/seed.py`: catálogo de enfermedades y síntomas de demostración.
- `ui/app.py`: interfaz gráfica Tkinter.
- `tests/test_domain.py`: pruebas automatizadas del dominio.

## Ejecutar pruebas

```bash
python -m unittest discover -s tests -v
```
- `main.py`: punto de entrada.

## Funcionalidades
- R1: registrar mascota y asociarla a propietario.
- R2: registrar consulta con síntomas.
- R3: analizar molestias y ordenar coincidencias con umbral del 30%.
- R4: confirmar diagnóstico por el veterinario de la consulta.
- R5: registrar tratamiento y medicamento(s).
- R6: consultar historial médico cronológico.
- R7: programar citas y validar disponibilidad del veterinario.
- R8: gestionar catálogo de síntomas y enfermedades.
- R9: actualizar citas a atendida o cancelada.
- R10: alertar tratamientos vigentes al registrar una consulta.

## Importante
Esta versión mantiene los datos en memoria: al cerrar la aplicación, los registros creados durante esa sesión no se conservan. La persistencia en SQLite debe agregarse como siguiente mejora si la entrega exige conservar información entre ejecuciones.

El catálogo inicial es ilustrativo y no reemplaza el criterio de un veterinario. Las coincidencias son apoyo informativo, no un diagnóstico clínico automático.
