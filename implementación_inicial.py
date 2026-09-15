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

@dataclass
class Tratamiento:
    medicamentos: list[str]
    dosis: str
    frecuencia: str
    duracion: str
    indicaciones: str
    recomendaciones: str


@dataclass(eq=False)
class Consulta:
    id: str
    mascota: Mascota
    veterinario: Veterinario
    fecha: datetime
    sintomas: list[Sintoma]
    observaciones: str

    enfermedad_diagnosticada: Enfermedad | None = None
    fecha_diagnostico: datetime | None = None
    observaciones_diagnostico: str | None = None

    tratamiento: Tratamiento | None = None

    enfermedades_posibles: list[Enfermedad] = field(default_factory=list)

    analisis_realizado: bool = False

    def __post_init__(self):

        if texto_vacio(self.id):
            raise ValueError("La consulta debe tener un identificador.")

        if self.mascota is None:
            raise ValueError("La consulta debe tener una mascota.")

        if self.veterinario is None:
            raise ValueError("La consulta debe tener un veterinario.")

        if len(self.sintomas) == 0:
            raise ValueError("La consulta debe tener al menos un síntoma.")

        self.mascota.agregar_consulta(self)
        self.veterinario.registrar_consulta(self)

    # R3
    def analizar_molestias(self, enfermedades):

        if len(self.sintomas) == 0:
            raise ValueError("No se puede analizar una consulta sin síntomas.")
        self.enfermedades_posibles = []

        resultados = []

        for enfermedad in enfermedades:
            if enfermedad.aplica_a_especie(self.mascota.especie):
                porcentaje = enfermedad.calcular_coincidencia(self.sintomas)

                if porcentaje > 0:
                    resultados.append((enfermedad, porcentaje))

        resultados.sort(key=lambda resultado: resultado[1],reverse=True)

        for enfermedad, porcentaje in resultados:
            self.enfermedades_posibles.append(enfermedad)

        self.analisis_realizado = True

        return resultados

    # R4
    def registrar_diagnostico(self, enfermedad, fecha, observaciones):

        if not self.analisis_realizado:
            raise ValueError("Primero se debe realizar el análisis.")

        if enfermedad is None:
            raise ValueError("Se debe indicar la enfermedad diagnosticada.")

        self.enfermedad_diagnosticada = enfermedad
        self.fecha_diagnostico = fecha
        self.observaciones_diagnostico = observaciones


@dataclass(eq=False)
class Cita:
    id: str
    mascota: Mascota
    veterinario: Veterinario
    fecha_hora: datetime
    estado: str = "programada"
    consulta: Consulta | None = None


def mostrar_resultados_analisis(resultados):

    print("\n======================================")
    print("      POSIBLES ENFERMEDADES")
    print("======================================")

    if len(resultados) == 0:
        print("No se encontraron enfermedades relacionadas.")
        return

    for enfermedad, porcentaje in resultados:

        print(f"- {enfermedad.nombre}: {porcentaje:.2f}% de coincidencia")


def mostrar_historial(mascota):

    print("\n======================================")
    print("       HISTORIAL MÉDICO")
    print("======================================")

    historial = mascota.consultar_historial()

    if len(historial) == 0:
        print(f"{mascota.nombre} no tiene consultas registradas.")
        return

    for consulta in historial:

        print("\n--------------------------------------")
        print(f"Consulta: {consulta.id}")
        print(
            f"Fecha: "
            f"{consulta.fecha.strftime('%d/%m/%Y %H:%M')}"
        )
        print(
            f"Veterinario: {consulta.veterinario.nombre}"
        )

        print("Síntomas:")

        for sintoma in consulta.sintomas:
            print(f"- {sintoma.nombre}")

        print(f"Observaciones: {consulta.observaciones}")

        if consulta.enfermedad_diagnosticada is not None:

            print(
                "Diagnóstico: "
                f"{consulta.enfermedad_diagnosticada.nombre}"
            )

            print(
                "Observaciones del diagnóstico: "
                f"{consulta.observaciones_diagnostico}"
            )

        else:
            print("Diagnóstico: Sin diagnóstico registrado.")



def cargar_catalogo_enfermedades():

    fiebre = Sintoma("Fiebre")
    tos = Sintoma("Tos")
    perdida_apetito = Sintoma("Pérdida de apetito")
    vomito = Sintoma("Vómito")
    diarrea = Sintoma("Diarrea")
    estornudos = Sintoma("Estornudos")

    gripe_canina = Enfermedad(
        nombre="Gripe canina",
        sintomas=[
            fiebre,
            tos,
            perdida_apetito
        ],
        especies=["Perro"]
    )

    gastroenteritis = Enfermedad(
        nombre="Gastroenteritis",
        sintomas=[
            vomito,
            diarrea,
            perdida_apetito
        ],
        especies=["Perro", "Gato"]
    )

    rinotraqueitis = Enfermedad(
        nombre="Rinotraqueítis felina",
        sintomas=[
            estornudos,
            fiebre,
            perdida_apetito
        ],
        especies=["Gato"]
    )

    infeccion_general = Enfermedad(
        nombre="Infección general",
        sintomas=[
            fiebre,
            perdida_apetito
        ],
        especies=["Todas"]
    )

    return [
        gripe_canina,
        gastroenteritis,
        rinotraqueitis,
        infeccion_general
    ]

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

