from models.domain import Clinica

def cargar_catalogo_inicial(clinica):
    """Carga un catálogo de demostración solo cuando está vacío."""
    if clinica.sintomas or clinica.enfermedades:
        return
    fiebre = clinica.registrar_sintoma("Fiebre", "Temperatura elevada")
    tos = clinica.registrar_sintoma("Tos", "Expulsión brusca de aire")
    apetito = clinica.registrar_sintoma("Pérdida de apetito", "Deja de comer")
    vomito = clinica.registrar_sintoma("Vómito", "Expulsa el contenido del estómago")
    diarrea = clinica.registrar_sintoma("Diarrea", "Heces líquidas")
    estornudos = clinica.registrar_sintoma("Estornudos", "Expulsión brusca por la nariz")
    clinica.registrar_enfermedad("Gripe canina", [fiebre, tos, apetito], ["Perro"])
    clinica.registrar_enfermedad("Gastroenteritis", [vomito, diarrea, apetito], ["Perro", "Gato"])
    clinica.registrar_enfermedad("Rinotraqueítis felina", [estornudos, fiebre, apetito], ["Gato"])
    clinica.registrar_enfermedad("Infección general", [fiebre, apetito], ["Perro", "Gato"])
