from models.domain import Clinica
from services.seed import cargar_catalogo_inicial
from ui.app import iniciar_interfaz


def main():
    clinica = Clinica(umbral_coincidencia=30.0)
    cargar_catalogo_inicial(clinica)
    iniciar_interfaz(clinica)


if __name__ == "__main__":
    main()
