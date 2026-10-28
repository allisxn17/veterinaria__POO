import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.domain import Sexo, EstadoCita, Medicamento, Sintoma, Enfermedad
from services.seed import cargar_catalogo_inicial


class ClinicaApp(tk.Tk):
    def __init__(self, clinica):
        super().__init__()
        self.clinica = clinica
        cargar_catalogo_inicial(self.clinica)
        self.title("VetCare | Gestión veterinaria")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg="#f4f7fb")
        self._estilos()
        self._construir()
        self._refrescar_todo()

    def _estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f4f7fb")
        style.configure("TLabel", background="#f4f7fb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#16324f")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#526579")
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _construir(self):
        header = ttk.Frame(self, padding=(22, 18, 22, 10))
        header.pack(fill="x")
        ttk.Label(header, text="VetCare", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Gestión de pacientes, consultas y seguimiento médico",
                  style="Sub.TLabel").pack(anchor="w", pady=(3, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(4, 18))
        self.tab_pacientes = ttk.Frame(self.tabs, padding=14)
        self.tab_personal = ttk.Frame(self.tabs, padding=14)
        self.tab_consultas = ttk.Frame(self.tabs, padding=14)
        self.tab_citas = ttk.Frame(self.tabs, padding=14)
        self.tab_catalogo = ttk.Frame(self.tabs, padding=14)
        self.tab_historial = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(self.tab_pacientes, text="Propietarios y mascotas")
        self.tabs.add(self.tab_personal, text="Personal")
        self.tabs.add(self.tab_consultas, text="Consultas y diagnóstico")
        self.tabs.add(self.tab_citas, text="Citas")
        self.tabs.add(self.tab_catalogo, text="Catálogo")
        self.tabs.add(self.tab_historial, text="Historial médico")
        self._crear_pacientes()
        self._crear_personal()
        self._crear_consultas()
        self._crear_citas()
        self._crear_catalogo()
        self._crear_historial()

    def _section(self, parent, title, subtitle=None):
        ttk.Label(parent, text=title, style="Title.TLabel").pack(anchor="w", pady=(0, 4))
        if subtitle:
            ttk.Label(parent, text=subtitle, style="Sub.TLabel").pack(anchor="w", pady=(0, 12))

    def _form(self, parent, labels):
        frame = ttk.LabelFrame(parent, text="Datos", padding=12)
        frame.pack(fill="x", pady=(6, 12))
        widgets = {}
        for i, label in enumerate(labels):
            row, col = divmod(i, 3)
            cell = ttk.Frame(frame)
            cell.grid(row=row, column=col, sticky="ew", padx=7, pady=5)
            ttk.Label(cell, text=label).pack(anchor="w")
            ent = ttk.Entry(cell, width=28)
            ent.pack(fill="x", pady=(3, 0))
            widgets[label] = ent
            frame.columnconfigure(col, weight=1)
        return widgets

    def _tree(self, parent, columns, headings, height=8):
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True, pady=6)
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=140, anchor="w")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _button_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(0, 8))
        return row

    def _crear_pacientes(self):
        p = self.tab_pacientes
        self._section(p, "Propietarios y mascotas", "Registra al responsable y asocia cada mascota a un propietario.")
        self.owner_fields = self._form(p, ["Nombre propietario", "Documento", "Teléfono"])
        row = self._button_row(p)
        ttk.Button(row, text="Registrar propietario", style="Accent.TButton",
                   command=self._registrar_propietario).pack(side="left")
        self.pet_fields = self._form(p, ["Nombre mascota", "Especie (Perro/Gato)", "Raza",
                                        "Edad en años", "Sexo (macho/hembra)", "Peso en kg"])
        ttk.Label(p, text="Propietario registrado").pack(anchor="w")
        self.owner_combo = ttk.Combobox(p, state="readonly", width=45)
        self.owner_combo.pack(anchor="w", pady=(3, 8))
        row = self._button_row(p)
        ttk.Button(row, text="Registrar mascota", style="Accent.TButton",
                   command=self._registrar_mascota).pack(side="left")
        self.pet_tree = self._tree(p, ("nombre", "especie", "raza", "edad", "sexo", "peso", "propietario"),
                                   ("Mascota", "Especie", "Raza", "Edad", "Sexo", "Peso kg", "Propietario"), 7)

    def _crear_personal(self):
        p = self.tab_personal

        self._section(
            p,
            "Personal de la clínica",
            "Registra a los veterinarios."
        )

        staff = ttk.LabelFrame(
            p,
            text="Registrar personal de la clínica",
            padding=16
        )
        staff.pack(fill="x", pady=10)

        self.staff_fields = {}

        for i, label in enumerate(["Nombre", "Documento", "Teléfono"]):
            cell = ttk.Frame(staff)
            cell.grid(row=0, column=i, sticky="ew", padx=8, pady=8)

            ttk.Label(cell, text=label).pack(anchor="w")

            entry = ttk.Entry(cell, width=25)
            entry.pack(fill="x", pady=4)

            self.staff_fields[label] = entry
            staff.columnconfigure(i, weight=1)

        ttk.Label(staff, text="Rol").grid(
            row=1, column=0, sticky="w", padx=8, pady=5
        )

        self.staff_role = ttk.Combobox(
            staff,
            state="readonly",
            values=["Veterinario"],
            width=22
        )
        self.staff_role.grid(
            row=2, column=0, sticky="w", padx=8, pady=5
        )
        self.staff_role.current(0)

        ttk.Button(
            staff,
            text="Registrar personal",
            command=self._registrar_personal
        ).grid(row=2, column=1, sticky="w", padx=8, pady=5)

    def _crear_consultas(self):
        p = self.tab_consultas
        self._section(p, "Consulta, análisis y tratamiento",
                       "El análisis solo ofrece coincidencias; el diagnóstico definitivo lo confirma el veterinario.")
        row = ttk.Frame(p); row.pack(fill="x", pady=5)
        ttk.Label(row, text="Mascota").pack(side="left", padx=(0, 5))
        self.cons_pet = ttk.Combobox(row, state="readonly", width=25); self.cons_pet.pack(side="left", padx=(0, 14))
        ttk.Label(row, text="Veterinario").pack(side="left", padx=(0, 5))
        self.cons_vet = ttk.Combobox(row, state="readonly", width=25); self.cons_vet.pack(side="left")
        self.cons_date = ttk.Entry(row, width=18); self.cons_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.cons_date.pack(side="left", padx=10)
        ttk.Label(p, text="Fecha y hora (AAAA-MM-DD HH:MM)").pack(anchor="w")
        ttk.Label(p, text="Selecciona uno o varios síntomas (Ctrl o Shift para seleccionar varios)").pack(anchor="w", pady=(8, 2))
        self.sym_list = tk.Listbox(p, selectmode="multiple", height=5, exportselection=False)
        self.sym_list.pack(fill="x", pady=(0, 8))
        ttk.Label(p, text="Observaciones de la consulta").pack(anchor="w")
        self.cons_notes = ttk.Entry(p)
        self.cons_notes.pack(fill="x", pady=(3, 8))
        row = self._button_row(p)
        ttk.Button(row, text="Registrar consulta y alertar tratamientos", command=self._registrar_consulta,
                   style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Analizar molestias", command=self._analizar).pack(side="left")
        self.analysis_tree = self._tree(p, ("enfermedad", "porcentaje"), ("Posible enfermedad", "Coincidencia"), 4)
        row = ttk.Frame(p); row.pack(fill="x", pady=8)
        ttk.Label(row, text="Enfermedad para diagnóstico").pack(side="left", padx=(0, 6))
        self.diag_combo = ttk.Combobox(row, state="readonly", width=30); self.diag_combo.pack(side="left", padx=(0, 8))
        self.diag_notes = ttk.Entry(row, width=38); self.diag_notes.insert(0, "Confirmado por el veterinario")
        self.diag_notes.pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Confirmar diagnóstico", command=self._registrar_diagnostico).pack(side="left")
        med = ttk.LabelFrame(p, text="Tratamiento del diagnóstico seleccionado", padding=8)
        med.pack(fill="x", pady=4)
        self.med_fields = {}
        for i, label in enumerate(["Medicamento", "Dosis", "Frecuencia", "Duración días"]):
            cell = ttk.Frame(med); cell.grid(row=0, column=i, sticky="ew", padx=4)
            ttk.Label(cell, text=label).pack(anchor="w")
            e = ttk.Entry(cell, width=20); e.pack(fill="x", pady=3); self.med_fields[label] = e
            med.columnconfigure(i, weight=1)
        self.treat_notes = ttk.Entry(med)
        self.treat_notes.insert(0, "Indicaciones")
        self.treat_notes.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        self.treat_recs = ttk.Entry(med)
        self.treat_recs.insert(0, "Recomendaciones")
        self.treat_recs.grid(row=1, column=2, columnspan=2, sticky="ew", padx=4, pady=4)
        ttk.Button(med, text="Registrar medicamento y tratamiento", command=self._registrar_tratamiento).grid(
            row=2, column=0, columnspan=4, sticky="w", padx=4, pady=4)

    def _crear_citas(self):
        p = self.tab_citas
        self._section(p, "Agenda de citas", "No se permiten dos citas programadas para el mismo veterinario en la misma fecha y hora.")
        row = ttk.Frame(p); row.pack(fill="x", pady=6)
        ttk.Label(row, text="Mascota").pack(side="left")
        self.app_pet = ttk.Combobox(row, state="readonly", width=25); self.app_pet.pack(side="left", padx=6)
        ttk.Label(row, text="Veterinario").pack(side="left")
        self.app_vet = ttk.Combobox(row, state="readonly", width=25); self.app_vet.pack(side="left", padx=6)
        ttk.Label(row, text="Fecha/hora").pack(side="left")
        self.app_date = ttk.Entry(row, width=18); self.app_date.insert(0, datetime.now().strftime("%Y-%m-%d 15:00"))
        self.app_date.pack(side="left", padx=6)
        ttk.Label(p, text="Formato de fecha: AAAA-MM-DD HH:MM").pack(anchor="w")
        row = self._button_row(p)
        ttk.Button(row, text="Programar cita", command=self._programar_cita, style="Accent.TButton").pack(side="left")
        ttk.Label(row, text="   Selecciona una cita para cambiar su estado:").pack(side="left", padx=8)
        self.cita_state = ttk.Combobox(row, state="readonly", values=["atendida", "cancelada"], width=12)
        self.cita_state.pack(side="left")
        ttk.Button(row, text="Actualizar estado", command=self._actualizar_cita).pack(side="left", padx=6)
        self.cita_tree = self._tree(p, ("id", "mascota", "veterinario", "fecha", "estado"),
                                    ("ID", "Mascota", "Veterinario", "Fecha y hora", "Estado"), 15)

    def _crear_catalogo(self):
        p = self.tab_catalogo
        self._section(p, "Catálogo de síntomas y enfermedades", "El catálogo alimenta el análisis de coincidencia.")
        self.sym_fields = self._form(p, ["Nombre del síntoma", "Descripción"])
        row = self._button_row(p)
        ttk.Button(row, text="Agregar síntoma", command=self._agregar_sintoma).pack(side="left")
        self.sym_tree = self._tree(p, ("nombre", "descripcion"), ("Síntoma", "Descripción"), 5)
        self.dis_fields = self._form(p, ["Nombre enfermedad", "Especies (separadas por coma)",
                                        "Síntomas (nombres separados por coma)"])
        row = self._button_row(p)
        ttk.Button(row, text="Agregar enfermedad", command=self._agregar_enfermedad,
                   style="Accent.TButton").pack(side="left")
        self.dis_tree = self._tree(p, ("nombre", "especies", "sintomas"),
                                   ("Enfermedad", "Especies", "Síntomas asociados"), 5)

    def _crear_historial(self):
        p = self.tab_historial
        self._section(p, "Historial médico", "Consultas ordenadas por fecha con síntomas, diagnóstico y tratamiento.")
        row = ttk.Frame(p); row.pack(fill="x", pady=6)
        ttk.Label(row, text="Mascota").pack(side="left")
        self.hist_pet = ttk.Combobox(row, state="readonly", width=35); self.hist_pet.pack(side="left", padx=8)
        ttk.Button(row, text="Consultar historial", command=self._historial, style="Accent.TButton").pack(side="left")
        self.history_text = tk.Text(p, wrap="word", height=25, font=("Consolas", 10), relief="solid", borderwidth=1)
        self.history_text.pack(fill="both", expand=True, pady=8)

    def _msg_error(self, error):
        messagebox.showerror("No se pudo completar", str(error), parent=self)

    def _get_selected(self, combo, objects, label):
        index = combo.current()
        if index < 0 or index >= len(objects):
            raise ValueError(f"Selecciona {label}.")
        return objects[index]

    def _parse_date(self, value):
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Usa el formato de fecha y hora AAAA-MM-DD HH:MM.")

    def _registrar_propietario(self):
        try:
            f = self.owner_fields
            self.clinica.registrar_propietario(f["Nombre propietario"].get(), f["Documento"].get(), f["Teléfono"].get())
            self._refrescar_todo()
            for e in f.values(): e.delete(0, "end")
            messagebox.showinfo("Correcto", "Propietario registrado.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _registrar_personal(self):
        try:
            f = self.staff_fields
            role = self.staff_role.get()
            args = (f["Nombre"].get(), f["Documento"].get(), f["Teléfono"].get())
            if role == "Veterinario":
                self.clinica.registrar_veterinario(*args)
            elif role == "Recepcionista":
                self.clinica.registrar_recepcionista(*args)
            else:
                raise ValueError("Selecciona el rol del personal.")
            for entry in f.values():
                entry.delete(0, "end")
            self._refrescar_todo()
            messagebox.showinfo("Correcto", f"{role} registrado.", parent=self)
        except Exception as exc:
            self._msg_error(exc)

    def _registrar_mascota(self):
        try:
            f = self.pet_fields
            owner = self._get_selected(self.owner_combo, self.clinica.propietarios, "un propietario")
            sexo_txt = f["Sexo (macho/hembra)"].get().strip().lower()
            sexo = {"macho": Sexo.MACHO, "hembra": Sexo.HEMBRA}.get(sexo_txt)
            if sexo is None: raise ValueError("El sexo debe ser macho o hembra.")
            edad = int(f["Edad en años"].get())
            peso = float(f["Peso en kg"].get().replace(",", "."))
            self.clinica.registrar_mascota(f["Nombre mascota"].get(), f["Especie (Perro/Gato)"].get(),
                f["Raza"].get(), edad, sexo, peso, owner)
            self._refrescar_todo()
            messagebox.showinfo("Correcto", "Mascota registrada.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _registrar_consulta(self):
        try:
            pet = self._get_selected(self.cons_pet, self.clinica.mascotas, "una mascota")
            vet = self._get_selected(self.cons_vet, self.clinica.veterinarios, "un veterinario")
            indices = self.sym_list.curselection()
            sintomas = [self.clinica.sintomas[i] for i in indices]
            fecha = self._parse_date(self.cons_date.get())
            consulta, vigentes = self.clinica.registrar_consulta(pet, vet, fecha, sintomas, self.cons_notes.get())
            self.selected_consulta = consulta
            self.last_results = []
            self._clear_tree(self.analysis_tree)
            self.diag_combo.set("")
            self.diag_combo["values"] = []
            self._refrescar_todo()
            if vigentes:
                detalle = "\n".join(f"{d.enfermedad.nombre}: termina {fin:%d/%m/%Y}" for d, fin in vigentes)
                messagebox.showwarning("Tratamiento activo", "La mascota tiene tratamiento(s) vigente(s):\n" + detalle, parent=self)
            else:
                messagebox.showinfo("Consulta registrada", f"Consulta {consulta.id} registrada.\nLa mascota no tiene tratamientos activos.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _analizar(self):
        try:
            consulta = getattr(self, "selected_consulta", None)
            if consulta is None: raise ValueError("Primero registra una consulta.")
            self.last_results = self.clinica.analizar_molestias(consulta)
            self._clear_tree(self.analysis_tree)
            names = []
            for enf, pct in self.last_results:
                self.analysis_tree.insert("", "end", values=(enf.nombre, f"{pct:.2f}%"))
                names.append(enf.nombre)
            self.diag_combo["values"] = names
            if names: self.diag_combo.current(0)
            else: messagebox.showinfo("Análisis", "No se encontraron enfermedades relacionadas.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _registrar_diagnostico(self):
        try:
            consulta = getattr(self, "selected_consulta", None)
            if consulta is None: raise ValueError("Primero registra una consulta.")
            nombre = self.diag_combo.get()
            enfermedad = next((e for e, _ in getattr(self, "last_results", []) if e.nombre == nombre), None)
            if enfermedad is None: raise ValueError("Selecciona una enfermedad de los resultados del análisis.")
            d = self.clinica.registrar_diagnostico(consulta, enfermedad, self.diag_notes.get(), datetime.now())
            messagebox.showinfo("Diagnóstico registrado", f"Diagnóstico confirmado: {d.enfermedad.nombre}", parent=self)
            self._historial_silencioso(consulta.mascota)
        except Exception as exc: self._msg_error(exc)

    def _registrar_tratamiento(self):
        try:
            consulta = getattr(self, "selected_consulta", None)
            if consulta is None or not consulta.tiene_diagnostico():
                raise ValueError("Registra primero el diagnóstico de la consulta.")
            f = self.med_fields
            med = Medicamento(f["Medicamento"].get(), f["Dosis"].get(), f["Frecuencia"].get(),
                              int(f["Duración días"].get()))
            tratamiento = self.clinica.registrar_tratamiento(
                consulta, [med], self.treat_notes.get(), self.treat_recs.get())
            messagebox.showinfo("Tratamiento registrado",
                f"Tratamiento guardado. Vigente hasta {tratamiento.fecha_fin(consulta.diagnostico.fecha):%d/%m/%Y}.",
                parent=self)
            self._historial_silencioso(consulta.mascota)
        except Exception as exc: self._msg_error(exc)

    def _programar_cita(self):
        try:
            pet = self._get_selected(self.app_pet, self.clinica.mascotas, "una mascota")
            vet = self._get_selected(self.app_vet, self.clinica.veterinarios, "un veterinario")
            cita = self.clinica.programar_cita(pet, vet, self._parse_date(self.app_date.get()))
            self._refrescar_todo()
            messagebox.showinfo("Cita programada", f"Cita {cita.id} registrada.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _actualizar_cita(self):
        try:
            selection = self.cita_tree.selection()
            if not selection: raise ValueError("Selecciona una cita.")
            cita_id = self.cita_tree.item(selection[0], "values")[0]
            cita = next(c for c in self.clinica.citas if c.id == cita_id)
            state = self.cita_state.get()
            if state == "cancelada":
                self.clinica.actualizar_estado_cita(cita, EstadoCita.CANCELADA)
            elif state == "atendida":
                consulta = cita.consulta
                if consulta is None:
                    consulta = next((c for c in reversed(self.clinica.consultas)
                                     if c.mascota is cita.mascota and c.veterinario is cita.veterinario), None)
                if consulta is None:
                    raise ValueError("Para marcarla atendida, registra primero una consulta de esa mascota con ese veterinario.")
                self.clinica.actualizar_estado_cita(cita, EstadoCita.ATENDIDA, consulta)
            else: raise ValueError("Selecciona atendida o cancelada.")
            self._refrescar_todo()
            messagebox.showinfo("Correcto", f"Cita {cita.id}: {cita.estado.value}.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _agregar_sintoma(self):
        try:
            f = self.sym_fields
            self.clinica.registrar_sintoma(f["Nombre del síntoma"].get(), f["Descripción"].get())
            self._refrescar_todo()
            messagebox.showinfo("Correcto", "Síntoma agregado.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _agregar_enfermedad(self):
        try:
            f = self.dis_fields
            symptom_names = [x.strip() for x in f["Síntomas (nombres separados por coma)"].get().split(",") if x.strip()]
            symptoms = []
            for name in symptom_names:
                found = next((s for s in self.clinica.sintomas if s.nombre.lower() == name.lower()), None)
                if found is None: raise ValueError(f"El síntoma '{name}' no existe en el catálogo.")
                symptoms.append(found)
            species = [x.strip() for x in f["Especies (separadas por coma)"].get().split(",") if x.strip()]
            self.clinica.registrar_enfermedad(f["Nombre enfermedad"].get(), symptoms, species)
            self._refrescar_todo()
            messagebox.showinfo("Correcto", "Enfermedad agregada.", parent=self)
        except Exception as exc: self._msg_error(exc)

    def _historial(self):
        try:
            pet = self._get_selected(self.hist_pet, self.clinica.mascotas, "una mascota")
            self._historial_silencioso(pet)
        except Exception as exc: self._msg_error(exc)

    def _historial_silencioso(self, mascota):
        self.history_text.delete("1.0", "end")
        self.history_text.insert("end", f"MASCOTA: {mascota.nombre}\nESPECIE: {mascota.especie}\nPROPIETARIO: {mascota.propietario.nombre}\n")
        historial = self.clinica.consultar_historial(mascota)
        if not historial:
            self.history_text.insert("end", "\nEl historial médico está vacío.\n")
            return
        for c in historial:
            self.history_text.insert("end", "\n" + "=" * 72 + "\n")
            self.history_text.insert("end", f"Consulta {c.id} | {c.fecha:%d/%m/%Y %H:%M} | Veterinario: {c.veterinario.nombre}\n")
            self.history_text.insert("end", "Síntomas: " + ", ".join(s.nombre for s in c.sintomas) + "\n")
            self.history_text.insert("end", f"Observaciones: {c.observaciones or 'Sin observaciones'}\n")
            d = c.diagnostico
            if d is None:
                self.history_text.insert("end", "Diagnóstico: pendiente\n")
                continue
            self.history_text.insert("end", f"Diagnóstico: {d.enfermedad.nombre} | {d.fecha:%d/%m/%Y}\n")
            self.history_text.insert("end", f"Observaciones del veterinario: {d.observaciones or 'Sin observaciones'}\n")
            if d.tratamiento:
                for m in d.tratamiento.medicamentos:
                    self.history_text.insert("end", f"Medicamento: {m.nombre} | Dosis: {m.dosis} | Frecuencia: {m.frecuencia} | {m.duracion_dias} días\n")
                self.history_text.insert("end", f"Indicaciones: {d.tratamiento.indicaciones}\nRecomendaciones: {d.tratamiento.recomendaciones}\n")
            else:
                self.history_text.insert("end", "Tratamiento: pendiente\n")

    def _clear_tree(self, tree):
        for item in tree.get_children(): tree.delete(item)

    def _refrescar_todo(self):
        owners = self.clinica.propietarios
        self.owner_combo["values"] = [f"{o.nombre} | {o.documento}" for o in owners]
        if owners and self.owner_combo.current() < 0: self.owner_combo.current(0)
        pets = self.clinica.mascotas
        pet_values = [f"{m.nombre} | {m.propietario.nombre}" for m in pets]
        for combo in (getattr(self, "cons_pet", None), getattr(self, "app_pet", None), getattr(self, "hist_pet", None)):
            if combo is not None:
                old = combo.get()
                combo["values"] = pet_values
                if old in pet_values: combo.set(old)
                elif pet_values: combo.current(0)
                else: combo.set("")
        vets = self.clinica.veterinarios
        vet_values = [f"{v.nombre} | {v.documento}" for v in vets]
        for combo in (getattr(self, "cons_vet", None), getattr(self, "app_vet", None)):
            if combo is not None:
                old = combo.get(); combo["values"] = vet_values
                if old in vet_values: combo.set(old)
                elif vet_values: combo.current(0)
                else: combo.set("")
        if hasattr(self, "sym_list"):
            self.sym_list.delete(0, "end")
            for s in self.clinica.sintomas: self.sym_list.insert("end", s.nombre)
        if hasattr(self, "pet_tree"):
            self._clear_tree(self.pet_tree)
            for m in pets:
                self.pet_tree.insert("", "end", values=(m.nombre, m.especie, m.raza, m.edad,
                    m.sexo.value, m.peso, m.propietario.nombre))
        if hasattr(self, "cita_tree"):
            self._clear_tree(self.cita_tree)
            for c in self.clinica.citas:
                self.cita_tree.insert("", "end", values=(c.id, c.mascota.nombre, c.veterinario.nombre,
                    c.fecha_hora.strftime("%d/%m/%Y %H:%M"), c.estado.value))
        if hasattr(self, "sym_tree"):
            self._clear_tree(self.sym_tree)
            for s in self.clinica.sintomas: self.sym_tree.insert("", "end", values=(s.nombre, s.descripcion))
        if hasattr(self, "dis_tree"):
            self._clear_tree(self.dis_tree)
            for e in self.clinica.enfermedades:
                self.dis_tree.insert("", "end", values=(e.nombre, ", ".join(e.especies),
                    ", ".join(s.nombre for s in e.sintomas)))


def iniciar_interfaz(clinica):
    app = ClinicaApp(clinica)
    app.mainloop()
