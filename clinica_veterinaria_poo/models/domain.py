"""
PROYECTO DE AULA - ENTREGA 1: Clínica veterinaria
Programación Orientada a Objetos - Universidad de Medellín - 2026-2

Este código sale directamente del documento:
  - Cada clase y sus atributos salen de "Asignación de responsabilidades".
  - Cada requisito R1..R10 es un método de Clinica.
  - Cada regla de "Reglas de validación" lanza un ValueError.

Criterio para usar @dataclass:
  - Son dataclass: Sintoma, Medicamento, Tratamiento y Diagnostico.
  - Las demás clases (personas, Enfermedad, Mascota, Consulta, Cita y
    Clinica) son clases normales con __init__.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


# ============================================================
# ENUMERACIONES (tablas de Mascota y Cita)
# ============================================================

class Sexo(Enum):
    MACHO = "macho"
    HEMBRA = "hembra"


class EstadoCita(Enum):
    PROGRAMADA = "programada"
    ATENDIDA = "atendida"
    CANCELADA = "cancelada"


# ============================================================
# UTILIDAD DE VALIDACIÓN
# ============================================================

def exigir_texto(valor, campo):
    """Devuelve el texto sin espacios sobrantes o lanza error si falta."""
    if not isinstance(valor, str) or valor.strip() == "":
        raise ValueError(f"{campo} es obligatorio.")
    return valor.strip()


# ============================================================
# PERSONAS
# ============================================================

class Persona(ABC):
    """Clase abstracta: datos comunes y el método abstracto rol()."""

    def __init__(self, nombre, documento, telefono):
        self.nombre = exigir_texto(nombre, "El nombre")
        self.documento = exigir_texto(documento, "El documento")
        self.telefono = exigir_texto(telefono, "El teléfono")

    @abstractmethod
    def rol(self):
        """Función de la persona en la clínica."""


class Propietario(Persona):
    def __init__(self, nombre, documento, telefono):
        super().__init__(nombre, documento, telefono)
        self.mascotas = []

    def rol(self):
        return "Propietario"

    def agregar_mascota(self, mascota):
        if mascota not in self.mascotas:
            self.mascotas.append(mascota)

    def consultar_mascotas(self):
        return list(self.mascotas)


class Veterinario(Persona):
    def __init__(self, nombre, documento, telefono):
        super().__init__(nombre, documento, telefono)
        self.consultas = []
        self.citas = []

    def rol(self):
        return "Veterinario"

    def agregar_consulta(self, consulta):
        if consulta not in self.consultas:
            self.consultas.append(consulta)

    def agregar_cita(self, cita):
        if cita not in self.citas:
            self.citas.append(cita)

    def tiene_cita_programada(self, fecha_hora):
        """True si ya tiene una cita PROGRAMADA a esa fecha y hora."""
        return any(
            cita.estado == EstadoCita.PROGRAMADA and cita.fecha_hora == fecha_hora
            for cita in self.citas
        )

    def confirmar_diagnostico(self, consulta, enfermedad, fecha, observaciones):
        """El sistema sugiere, el veterinario decide."""
        if consulta.veterinario is not self:
            raise ValueError("Solo el veterinario que atendió la consulta puede diagnosticarla.")
        diagnostico = Diagnostico(enfermedad, fecha, observaciones)
        consulta.asignar_diagnostico(diagnostico)
        return diagnostico


class Recepcionista(Persona):
    def rol(self):
        return "Recepcionista"


# ============================================================
# CATÁLOGO: SÍNTOMA Y ENFERMEDAD
# ============================================================

@dataclass(eq=False)
class Sintoma:
    nombre: str
    descripcion: str = ""

    def __post_init__(self):
        self.nombre = exigir_texto(self.nombre, "El nombre del síntoma")

    # "Permitir compararse con otros síntomas por nombre"
    # (eq=False porque la comparación es solo por nombre, sin importar mayúsculas)
    def __eq__(self, otro):
        return isinstance(otro, Sintoma) and self.nombre.lower() == otro.nombre.lower()

    def __hash__(self):
        return hash(self.nombre.lower())

    def __repr__(self):
        return f"Sintoma({self.nombre!r})"


class Enfermedad:
    def __init__(self, nombre, sintomas, especies):
        self.nombre = exigir_texto(nombre, "El nombre de la enfermedad")
        if len(sintomas) == 0:
            raise ValueError("La enfermedad debe tener al menos un síntoma.")
        if len(especies) == 0:
            raise ValueError("La enfermedad debe tener al menos una especie.")
        self.sintomas = list(sintomas)
        self.especies = list(especies)

    def aplica_a_especie(self, especie):
        return especie.strip().lower() in [e.lower() for e in self.especies]

    def calcular_coincidencia(self, sintomas_consulta):
        """porcentaje = (sintomas_coincidentes / total_sintomas_enfermedad) x 100"""
        total_sintomas_enfermedad = len(self.sintomas)
        if total_sintomas_enfermedad == 0:
            return 0.0
        sintomas_coincidentes = sum(1 for s in self.sintomas if s in sintomas_consulta)
        return sintomas_coincidentes / total_sintomas_enfermedad * 100


# ============================================================
# TRATAMIENTO
# ============================================================

@dataclass
class Medicamento:
    nombre: str
    dosis: str
    frecuencia: str
    duracion_dias: int

    def __post_init__(self):
        self.nombre = exigir_texto(self.nombre, "El nombre del medicamento")
        self.dosis = exigir_texto(self.dosis, "La dosis")
        self.frecuencia = exigir_texto(self.frecuencia, "La frecuencia")
        if not isinstance(self.duracion_dias, int) or self.duracion_dias <= 0:
            raise ValueError("La duración del medicamento debe ser mayor que cero.")


@dataclass(eq=False)
class Tratamiento:
    medicamentos: list[Medicamento]
    indicaciones: str = ""
    recomendaciones: str = ""

    def __post_init__(self):
        if len(self.medicamentos) == 0:
            raise ValueError("El tratamiento debe tener al menos un medicamento.")
        self.medicamentos = list(self.medicamentos)

    def fecha_fin(self, fecha_diagnostico):
        """Fecha del diagnóstico + duración del medicamento más largo."""
        dias = max(m.duracion_dias for m in self.medicamentos)
        return fecha_diagnostico + timedelta(days=dias)

    def esta_vigente(self, fecha_diagnostico, fecha_actual):
        return fecha_actual < self.fecha_fin(fecha_diagnostico)


@dataclass(eq=False)
class Diagnostico:
    enfermedad: Enfermedad
    fecha: datetime
    observaciones: str = ""
    tratamiento: Tratamiento | None = None  # como máximo uno

    def __post_init__(self):
        if self.enfermedad is None:
            raise ValueError("El diagnóstico necesita una enfermedad.")

    def tiene_tratamiento(self):
        return self.tratamiento is not None

    def asignar_tratamiento(self, tratamiento):
        if self.tiene_tratamiento():
            raise ValueError("El diagnóstico ya tiene un tratamiento.")
        self.tratamiento = tratamiento


# ============================================================
# MASCOTA, CONSULTA Y CITA
# ============================================================

class Mascota:
    def __init__(self, nombre, especie, raza, edad, sexo, peso, propietario):
        self.nombre = exigir_texto(nombre, "El nombre de la mascota")
        self.especie = exigir_texto(especie, "La especie")
        self.raza = exigir_texto(raza, "La raza")
        if not isinstance(edad, int) or edad < 0:
            raise ValueError("La edad no puede ser negativa.")
        if not isinstance(sexo, Sexo):
            raise ValueError("El sexo debe ser macho o hembra.")
        if not isinstance(peso, (int, float)) or peso <= 0:
            raise ValueError("El peso debe ser mayor que cero.")
        if propietario is None:
            raise ValueError("La mascota debe tener un propietario.")
        self.edad = edad
        self.sexo = sexo
        self.peso = peso
        self.propietario = propietario
        self.consultas = []
        self.citas = []

    def agregar_consulta(self, consulta):
        if consulta not in self.consultas:
            self.consultas.append(consulta)

    def agregar_cita(self, cita):
        if cita not in self.citas:
            self.citas.append(cita)

    def historial_medico(self):
        """El historial no es una entidad: se obtiene de las consultas, por fecha."""
        return sorted(self.consultas, key=lambda c: c.fecha)


class Consulta:
    def __init__(self, id, mascota, veterinario, fecha, sintomas, observaciones=""):
        self.id = exigir_texto(id, "El id de la consulta")
        if mascota is None:
            raise ValueError("La consulta necesita una mascota válida.")
        if veterinario is None:
            raise ValueError("La consulta necesita un veterinario válido.")
        if len(sintomas) == 0:
            raise ValueError("La consulta debe tener al menos un síntoma.")
        if not isinstance(fecha, datetime):
            raise ValueError("La fecha de la consulta debe ser válida.")
        self.mascota = mascota
        self.veterinario = veterinario
        self.fecha = fecha
        self.sintomas = list(sintomas)
        self.observaciones = observaciones
        self.analizada = False
        self.diagnostico = None  # como máximo uno

    def tiene_diagnostico(self):
        return self.diagnostico is not None

    def asignar_diagnostico(self, diagnostico):
        if self.tiene_diagnostico():
            raise ValueError("La consulta ya tiene un diagnóstico.")
        self.diagnostico = diagnostico


class Cita:
    def __init__(self, id, mascota, veterinario, fecha_hora):
        if mascota is None:
            raise ValueError("La cita necesita una mascota válida.")
        if veterinario is None:
            raise ValueError("La cita necesita un veterinario válido.")
        self.id = exigir_texto(id, "El id de la cita")
        self.mascota = mascota
        self.veterinario = veterinario
        self.fecha_hora = fecha_hora
        self.estado = EstadoCita.PROGRAMADA
        self.consulta = None

    def cambiar_estado(self, nuevo_estado, consulta=None):
        """Único cambio válido: programada -> atendida o cancelada."""
        if self.estado != EstadoCita.PROGRAMADA:
            raise ValueError(f"La cita ya está {self.estado.value}; no puede modificarse.")
        if nuevo_estado == EstadoCita.ATENDIDA:
            if consulta is None:
                raise ValueError("Para atender la cita se necesita la consulta generada.")
            if consulta.mascota is not self.mascota or consulta.veterinario is not self.veterinario:
                raise ValueError("La consulta no corresponde a la mascota y veterinario de la cita.")
            self.consulta = consulta
        elif nuevo_estado != EstadoCita.CANCELADA:
            raise ValueError("La cita solo puede pasar a atendida o cancelada.")
        self.estado = nuevo_estado


# ============================================================
# CLÍNICA: coordina todo y aplica las reglas del negocio
# ============================================================

class Clinica:
    def __init__(self, umbral_coincidencia=30.0):
        self.propietarios = []
        self.mascotas = []
        self.veterinarios = []
        self.recepcionistas = []
        self.consultas = []
        self.citas = []
        self.enfermedades = []
        self.sintomas = []
        self.umbral_coincidencia = umbral_coincidencia

    # ---------- personas ----------

    def _validar_documento_libre(self, documento):
        personas = self.propietarios + self.veterinarios + self.recepcionistas
        if any(p.documento == str(documento).strip() for p in personas):
            raise ValueError(f"Ya existe una persona con el documento {documento}.")

    def registrar_propietario(self, nombre, documento, telefono):
        self._validar_documento_libre(documento)
        propietario = Propietario(nombre, documento, telefono)
        self.propietarios.append(propietario)
        return propietario

    def registrar_veterinario(self, nombre, documento, telefono):
        self._validar_documento_libre(documento)
        veterinario = Veterinario(nombre, documento, telefono)
        self.veterinarios.append(veterinario)
        return veterinario

    def registrar_recepcionista(self, nombre, documento, telefono):
        self._validar_documento_libre(documento)
        recepcionista = Recepcionista(nombre, documento, telefono)
        self.recepcionistas.append(recepcionista)
        return recepcionista

    # ---------- R1: registrar mascota ----------

    def registrar_mascota(self, nombre, especie, raza, edad, sexo, peso, propietario):
        if propietario not in self.propietarios:
            raise ValueError("La mascota debe tener un propietario registrado.")
        mascota = Mascota(nombre, especie, raza, edad, sexo, peso, propietario)
        propietario.agregar_mascota(mascota)
        self.mascotas.append(mascota)
        return mascota

    # ---------- R8: catálogo de síntomas y enfermedades ----------

    def registrar_sintoma(self, nombre, descripcion=""):
        sintoma = Sintoma(nombre, descripcion)
        if sintoma in self.sintomas:  # compara por nombre
            raise ValueError(f"Ya existe el síntoma '{sintoma.nombre}'.")
        self.sintomas.append(sintoma)
        return sintoma

    def registrar_enfermedad(self, nombre, sintomas, especies):
        enfermedad = Enfermedad(nombre, sintomas, especies)
        if any(e.nombre.lower() == enfermedad.nombre.lower() for e in self.enfermedades):
            raise ValueError(f"Ya existe la enfermedad '{enfermedad.nombre}'.")
        for sintoma in sintomas:
            if sintoma not in self.sintomas:
                raise ValueError(f"El síntoma '{sintoma.nombre}' no está en el catálogo.")
        self.enfermedades.append(enfermedad)
        return enfermedad

    # ---------- R2 (+ R10): registrar consulta ----------

    def registrar_consulta(self, mascota, veterinario, fecha, sintomas, observaciones=""):
        """Devuelve (consulta, tratamientos_vigentes): la alerta de R10 va con el registro."""
        if mascota not in self.mascotas:
            raise ValueError("La consulta necesita una mascota registrada.")
        if veterinario not in self.veterinarios:
            raise ValueError("La consulta necesita un veterinario registrado.")
        if not isinstance(fecha, datetime):
            raise ValueError("La fecha de la consulta debe ser válida.")
        if not sintomas or any(s not in self.sintomas for s in sintomas):
            raise ValueError("La consulta necesita síntomas válidos del catálogo.")
        consulta = Consulta(f"C{len(self.consultas) + 1:03d}", mascota, veterinario,
                            fecha, sintomas, observaciones)
        vigentes = self.alertar_tratamientos_activos(mascota, fecha)
        mascota.agregar_consulta(consulta)
        veterinario.agregar_consulta(consulta)
        self.consultas.append(consulta)
        return consulta, vigentes

    # ---------- R3: analizar molestias ----------

    def analizar_molestias(self, consulta):
        """Lista de (enfermedad, porcentaje), de mayor a menor, solo si >= umbral."""
        if consulta not in self.consultas:
            raise ValueError("La consulta no existe.")
        if len(consulta.sintomas) == 0:
            raise ValueError("No se puede analizar una consulta sin síntomas.")
        resultados = []
        for enfermedad in self.enfermedades:
            if len(enfermedad.sintomas) == 0:
                continue
            if not enfermedad.aplica_a_especie(consulta.mascota.especie):
                continue
            porcentaje = enfermedad.calcular_coincidencia(consulta.sintomas)
            if porcentaje >= self.umbral_coincidencia:
                resultados.append((enfermedad, porcentaje))
        resultados.sort(key=lambda r: r[1], reverse=True)
        consulta.analizada = True
        return resultados

    # ---------- R4: registrar diagnóstico ----------

    def registrar_diagnostico(self, consulta, enfermedad, observaciones="", fecha=None):
        if consulta not in self.consultas:
            raise ValueError("La consulta no existe.")
        if not consulta.analizada:
            raise ValueError("La consulta debe analizarse antes de diagnosticar.")
        if consulta.tiene_diagnostico():
            raise ValueError("La consulta ya tiene un diagnóstico.")
        if enfermedad not in self.enfermedades:
            raise ValueError("La enfermedad debe estar en el catálogo.")
        if not enfermedad.aplica_a_especie(consulta.mascota.especie):
            raise ValueError("La enfermedad no aplica a la especie de esta mascota.")
        return consulta.veterinario.confirmar_diagnostico(
            consulta, enfermedad, fecha or datetime.now(), observaciones)

    # ---------- R5: registrar tratamiento ----------

    def registrar_tratamiento(self, consulta, medicamentos, indicaciones="", recomendaciones=""):
        if consulta not in self.consultas:
            raise ValueError("La consulta no existe.")
        if not consulta.tiene_diagnostico():
            raise ValueError("No hay tratamiento sin un diagnóstico establecido.")
        tratamiento = Tratamiento(medicamentos, indicaciones, recomendaciones)
        consulta.diagnostico.asignar_tratamiento(tratamiento)
        return tratamiento

    # ---------- R6: consultar historial médico ----------

    def consultar_historial(self, mascota):
        if mascota not in self.mascotas:
            raise ValueError("La mascota no está registrada.")
        return mascota.historial_medico()  # [] si no tiene antecedentes

    # ---------- R7: programar cita ----------

    def programar_cita(self, mascota, veterinario, fecha_hora):
        if mascota not in self.mascotas:
            raise ValueError("La cita necesita una mascota registrada.")
        if veterinario not in self.veterinarios:
            raise ValueError("La cita necesita un veterinario registrado.")
        if not isinstance(fecha_hora, datetime):
            raise ValueError("La fecha y hora de la cita deben ser válidas.")
        if veterinario.tiene_cita_programada(fecha_hora):
            raise ValueError("El veterinario ya tiene una cita en esa fecha y hora.")
        cita = Cita(f"CT{len(self.citas) + 1:03d}", mascota, veterinario, fecha_hora)
        mascota.agregar_cita(cita)
        veterinario.agregar_cita(cita)
        self.citas.append(cita)
        return cita

    # ---------- R9: actualizar estado de una cita ----------

    def actualizar_estado_cita(self, cita, nuevo_estado, consulta=None):
        if cita not in self.citas:
            raise ValueError("La cita no existe.")
        if consulta is not None and consulta not in self.consultas:
            raise ValueError("La consulta asociada no existe.")
        cita.cambiar_estado(nuevo_estado, consulta)

    # ---------- R10: alertar tratamiento activo ----------

    def alertar_tratamientos_activos(self, mascota, fecha):
        """Lista de (diagnostico, fecha_fin) de los tratamientos aún vigentes."""
        vigentes = []
        for consulta in mascota.consultas:
            diagnostico = consulta.diagnostico
            if diagnostico is not None and diagnostico.tiene_tratamiento():
                tratamiento = diagnostico.tratamiento
                if tratamiento.esta_vigente(diagnostico.fecha, fecha):
                    vigentes.append((diagnostico, tratamiento.fecha_fin(diagnostico.fecha)))
        return vigentes


