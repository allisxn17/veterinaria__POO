import unittest
from datetime import datetime, timedelta
from models.domain import Clinica, Sexo, EstadoCita, Medicamento, Persona


class TestClinica(unittest.TestCase):
    def setUp(self):
        self.c = Clinica()
        self.owner = self.c.registrar_propietario("Laura", "P1", "300")
        self.vet = self.c.registrar_veterinario("Carlos", "V1", "301")
        self.pet = self.c.registrar_mascota("Luna", "Perro", "Criollo", 4, Sexo.HEMBRA, 8.2, self.owner)
        self.fever = self.c.registrar_sintoma("Fiebre")
        self.cough = self.c.registrar_sintoma("Tos")
        self.appetite = self.c.registrar_sintoma("Pérdida de apetito")
        self.disease = self.c.registrar_enfermedad("Gripe canina", [self.fever, self.cough, self.appetite], ["Perro"])

    def test_duplicate_document_rejected(self):
        with self.assertRaises(ValueError):
            self.c.registrar_veterinario("Otro", "P1", "302")

    def test_consult_requires_symptoms(self):
        with self.assertRaises(ValueError):
            self.c.registrar_consulta(self.pet, self.vet, datetime.now(), [])

    def test_analysis_calculates_percentage_and_marks_consult(self):
        consult, _ = self.c.registrar_consulta(self.pet, self.vet, datetime.now(), [self.fever, self.cough])
        results = self.c.analizar_molestias(consult)
        self.assertEqual(results[0][0], self.disease)
        self.assertAlmostEqual(results[0][1], 200 / 3)
        self.assertTrue(consult.analizada)

    def test_diagnosis_requires_analysis(self):
        consult, _ = self.c.registrar_consulta(self.pet, self.vet, datetime.now(), [self.fever])
        with self.assertRaises(ValueError):
            self.c.registrar_diagnostico(consult, self.disease)

    def test_disease_must_apply_to_species(self):
        cat_disease = self.c.registrar_enfermedad("Enfermedad felina", [self.fever], ["Gato"])
        consult, _ = self.c.registrar_consulta(self.pet, self.vet, datetime.now(), [self.fever])
        self.c.analizar_molestias(consult)
        with self.assertRaises(ValueError):
            self.c.registrar_diagnostico(consult, cat_disease)

    def test_vet_cannot_have_two_same_time_appointments(self):
        moment = datetime.now() + timedelta(days=1)
        self.c.programar_cita(self.pet, self.vet, moment)
        pet2 = self.c.registrar_mascota("Max", "Perro", "Pug", 2, Sexo.MACHO, 7, self.owner)
        with self.assertRaises(ValueError):
            self.c.programar_cita(pet2, self.vet, moment)

    def test_empty_history(self):
        self.assertEqual(self.c.consultar_historial(self.pet), [])

    def test_invalid_medicine_duration(self):
        with self.assertRaises(ValueError):
            Medicamento("Medicamento", "1 mg", "diaria", 0)


if __name__ == "__main__":
    unittest.main()
