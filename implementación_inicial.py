from dataclasses import dataclass, field
from datetime import datetime


def texto_vacio(valor):
    return valor is None or valor.strip() == ""


@dataclass(eq=False)
class Propietario:
    nombre: str
    documento: str
    telefono: str
    mascotas: list["Mascota"] = field(default_factory=list)

    def __post_init__(self):

        if texto_vacio(self.nombre):
            raise ValueError("El nombre del propietario es obligatorio.")

        if texto_vacio(self.documento):
            raise ValueError("El documento del propietario es obligatorio.")

        if texto_vacio(self.telefono):
            raise ValueError("El teléfono del propietario es obligatorio.")

    def agregar_mascota(self, mascota):
        for registrada in self.mascotas:
            if registrada is mascota:
                return

        self.mascotas.append(mascota)


@dataclass(eq=False)
class Mascota:
    nombre: str
    especie: str
    raza: str
    edad: int
    sexo: str
    peso: float
    propietario: Propietario
    consultas: list["Consulta"] = field(default_factory=list)

    def __post_init__(self):

        if texto_vacio(self.nombre):
            raise ValueError("El nombre de la mascota es obligatorio.")

        if texto_vacio(self.especie):
            raise ValueError("La especie de la mascota es obligatoria.")

        if texto_vacio(self.raza):
            raise ValueError("La raza de la mascota es obligatoria.")

        if self.edad < 0:
            raise ValueError("La edad no puede ser negativa.")

        if texto_vacio(self.sexo):
            raise ValueError("El sexo de la mascota es obligatorio.")

        if self.peso <= 0:
            raise ValueError("El peso debe ser mayor que cero.")

        if self.propietario is None:
            raise ValueError("La mascota debe tener un propietario.")

        self.propietario.agregar_mascota(self)

    # R2
    def agregar_consulta(self, consulta):

        for registrada in self.consultas:
            if registrada is consulta:
                return

        self.consultas.append(consulta)

    # R6
    def consultar_historial(self):
        return self.consultas


@dataclass(eq=False)
class Veterinario:
    id: str
    nombre: str
    consultas: list["Consulta"] = field(default_factory=list)

    def __post_init__(self):

        if texto_vacio(self.id):
            raise ValueError("El id del veterinario es obligatorio.")

        if texto_vacio(self.nombre):
            raise ValueError("El nombre del veterinario es obligatorio.")

    def registrar_consulta(self, consulta):
        for registrada in self.consultas:
            if registrada is consulta:
                return

        self.consultas.append(consulta)

    # R4
    def establecer_diagnostico(self, consulta, enfermedad, observaciones):

        if consulta is None:
            raise ValueError("Se necesita una consulta para registrar el diagnóstico.")

        if consulta.veterinario is not self:
            raise ValueError("Un veterinario solo puede diagnosticar las consultas que él mismo atendió.")

        if not consulta.analisis_realizado:
            raise ValueError("No se puede registrar el diagnóstico sin realizar primero el análisis.")

        es_posible = False

        for posible in consulta.enfermedades_posibles:
            if posible is enfermedad:
                es_posible = True
                break

        if not es_posible:
            raise ValueError("La enfermedad seleccionada no está entre las posibles enfermedades.")

        consulta.registrar_diagnostico(enfermedad, datetime.now(), observaciones)

@dataclass
class Sintoma:
    nombre: str

    def __post_init__(self):

        if texto_vacio(self.nombre):
            raise ValueError("El nombre del síntoma es obligatorio.")

        self.nombre = self.nombre.strip()

    def es_igual_a(self, otro):
        return self.nombre.lower() == otro.nombre.lower()


@dataclass(eq=False)
class Enfermedad:
    nombre: str
    sintomas: list[Sintoma]
    especies: list[str]

    def __post_init__(self):

        if texto_vacio(self.nombre):
            raise ValueError("El nombre de la enfermedad es obligatorio.")

        if len(self.sintomas) == 0:
            raise ValueError("La enfermedad debe tener al menos un síntoma.")

        if len(self.especies) == 0:
            raise ValueError("La enfermedad debe tener al menos una especie.")


    def aplica_a_especie(self, especie):
        for especie_registrada in self.especies:
            if especie_registrada.lower() == "todas":
                return True

            if especie_registrada.lower() == especie.lower():
                return True

        return False

    # R3
    def calcular_coincidencia(self, sintomas_consulta):
        sintomas_coincidentes = 0

        for sintoma_enfermedad in self.sintomas:
            for sintoma_consulta in sintomas_consulta:
                if sintoma_enfermedad.es_igual_a(sintoma_consulta):
                    sintomas_coincidentes += 1
                    break

        if len(self.sintomas) == 0:
            return 0.0

        porcentaje = (sintomas_coincidentes / len(self.sintomas)) * 100
        return porcentaje


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def ejecutar_programa():

    print("======================================")
    print("     SISTEMA DE GESTIÓN VETERINARIA")
    print("======================================")

    enfermedades = cargar_catalogo_enfermedades()

    # --------------------------------------------------------
    # DATOS DEL PROPIETARIO
    # --------------------------------------------------------

    propietario = Propietario(
        nombre="Laura Gómez",
        documento="123456789",
        telefono="3001234567"
    )

    # --------------------------------------------------------
    # R1 - REGISTRAR MASCOTA
    # --------------------------------------------------------

    mascota = Mascota(
        nombre="Luna",
        especie="Perro",
        raza="Labrador",
        edad=5,
        sexo="Hembra",
        peso=22.5,
        propietario=propietario
    )

    print("\nR1 - MASCOTA REGISTRADA")
    print(f"Nombre: {mascota.nombre}")
    print(f"Especie: {mascota.especie}")
    print(f"Raza: {mascota.raza}")
    print(f"Edad: {mascota.edad}")
    print(f"Propietario: {mascota.propietario.nombre}")
    print(
        "Mascotas del propietario: "
        f"{len(propietario.mascotas)}"
    )

    # --------------------------------------------------------
    # DATOS DEL VETERINARIO
    # --------------------------------------------------------

    veterinario = Veterinario(
        id="V001",
        nombre="Carlos Martínez"
    )

