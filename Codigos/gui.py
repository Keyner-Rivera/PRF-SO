import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QComboBox, QSpinBox, QScrollArea,
    QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QColor, QFont

# Importamos las clases necesarias del módulo de lógica
from core import Proceso, Planificador

class CustomErrorDialog(QDialog):
    """Un diálogo de error personalizado y estilizado."""
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error de Validación")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog { background-color: #1e293b; border-radius: 12px; }
            QLabel { color: #e2e8f0; font-size: 16px; padding: 20px; }
            QPushButton { background-color: #ef4444; color: #ffffff; font-weight: bold; border-radius: 8px; padding: 10px 20px; border: none; outline: none; }
            QPushButton:hover { background-color: #dc2626; }
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message), alignment=Qt.AlignCenter)
        ok_button = QPushButton("Aceptar")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        self.adjustSize()
        



class EditProcessDialog(QDialog):
    """Un diálogo para editar los detalles de un proceso existente."""
    def __init__(self, proceso, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Proceso {proceso.pid}")
        self.setModal(True)
        self.setFixedWidth(350) # Hacemos la ventana más ancha
        self.setStyleSheet("""
            QDialog { background-color: #1e293b; border-radius: 12px; }
            QLabel, QLineEdit { color: #e2e8f0; font-size: 14px; }
            QLineEdit { background-color: #0f172a; border: 1px solid #334155; padding: 8px; border-radius: 6px; }
            QPushButton { background-color: #22c55e; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 10px 20px; border: none; outline: none; }
            QPushButton:hover { background-color: #16a34a; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Nombre del Proceso:"))
        self.nombre_input = QLineEdit(proceso.nombre)
        layout.addWidget(self.nombre_input)

        layout.addWidget(QLabel("Instante de Llegada:"))
        self.llegada_input = QLineEdit(str(proceso.instante_llegada))
        self.llegada_input.setValidator(QIntValidator(0, 1000)) # Validamos que sea un número
        layout.addWidget(self.llegada_input)

        layout.addWidget(QLabel("Tiempo en CPU:"))
        self.tiempo_cpu_input = QLineEdit(str(proceso.tiempo_cpu_total))
        self.tiempo_cpu_input.setValidator(QIntValidator(1, 1000)) # Validamos que sea un número
        layout.addWidget(self.tiempo_cpu_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        """Devuelve los datos actualizados del formulario."""
        return {
            "nombre": self.nombre_input.text().strip(),
            "llegada": int(self.llegada_input.text()),
            "tiempo_cpu": int(self.tiempo_cpu_input.text())
        }

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    def __init__(self):
        super().__init__()
        self.procesos_para_simular = []
        self.pid_counter = 1

        self.setWindowTitle("Simulador de Planificación de CPU - Vista de Cronograma")
        self.setGeometry(50, 50, 1800, 900)
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
            QFrame#card { background-color: #1e293b; border-radius: 12px; padding: 15px; }
            QLabel { color: #cbd5e1; font-size: 13px; }
            QLabel#titleLabel { font-size: 16px; font-weight: bold; color: #e2e8f0; padding-bottom: 8px; }
            QPushButton { background-color: #22c55e; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 10px; border: none; outline: none; }
            QPushButton:hover { background-color: #16a34a; }
            QPushButton#dangerButton { background-color: #ef4444; }
            QPushButton#dangerButton:hover { background-color: #dc2626; }
            QLineEdit, QComboBox, QSpinBox { background-color: #0f172a; color: #e2e8f0; border: 1px solid #334155; padding: 8px; border-radius: 6px; font-size: 13px;}
            QTableWidget { background-color: #1e293b; color: #e2e8f0; border: none; }
            QHeaderView::section { background-color: #334155; color: #94a3b8; font-weight: bold; padding: 8px; border: none; }
            QHeaderView::section:vertical { background-color: #1e293b; border: none; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20); self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.controles_layout = self.crear_panel_controles()
        right_column_widget = QWidget()
        right_column_layout = QVBoxLayout(right_column_widget)
        right_column_layout.setContentsMargins(0, 0, 0, 0); right_column_layout.setSpacing(20)

        self.cronograma_panel, self.tabla_cronograma, self.cronograma_title_label = self.crear_panel_cronograma()
        self.estadisticas_panel, self.tabla_estadisticas = self.crear_panel_estadisticas()

        right_column_layout.addWidget(self.cronograma_panel, 3)
        right_column_layout.addWidget(self.estadisticas_panel, 2)
        self.main_layout.addLayout(self.controles_layout, 3)
        self.main_layout.addWidget(right_column_widget, 5)

        # Temporizador para la animación
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._avanzar_simulacion_paso)
        
        # Variable para almacenar el generador de la simulación
        self.simulation_generator = None




    def _crear_panel_base(self, title):
        panel_frame = QFrame(); panel_frame.setObjectName("card")
        panel_layout = QVBoxLayout(panel_frame)
        title_label = QLabel(title); title_label.setObjectName("titleLabel")
        panel_layout.addWidget(title_label)
        return panel_frame, panel_layout, title_label

    def crear_panel_controles(self):
        controles_main_layout = QVBoxLayout()
        top_panels_layout = QHBoxLayout()
        config_panel = self.crear_panel_configuracion()
        add_process_panel = self.crear_panel_agregar_proceso()
        top_panels_layout.addWidget(config_panel); top_panels_layout.addWidget(add_process_panel)
        controles_main_layout.addLayout(top_panels_layout)
        processes_list_panel = self.crear_panel_procesos_agregados()
        controles_main_layout.addWidget(processes_list_panel)
        controles_main_layout.addStretch(1)
        return controles_main_layout

    def crear_panel_configuracion(self):
        panel, layout, _ = self._crear_panel_base("Configuración")
        layout.addWidget(QLabel("Algoritmo de Planificación:"))
        self.combo_algoritmo = QComboBox(); self.combo_algoritmo.addItems(["FCFS", "SJF", "SRTF", "Round Robin"])
        self.combo_algoritmo.currentTextChanged.connect(self.toggle_quantum_input)
        layout.addWidget(self.combo_algoritmo)
        self.label_quantum = QLabel("Quantum de tiempo:"); self.input_quantum = QSpinBox()
        self.input_quantum.setRange(1, 100); self.input_quantum.setValue(2)
        self.label_quantum.hide(); self.input_quantum.hide()
        layout.addWidget(self.label_quantum); layout.addWidget(self.input_quantum)
        self.btn_iniciar = QPushButton("Iniciar Simulación"); self.btn_iniciar.clicked.connect(self.iniciar_simulacion_ui)
        layout.addWidget(self.btn_iniciar)
        self.btn_reiniciar = QPushButton("Reiniciar"); self.btn_reiniciar.setObjectName("dangerButton"); self.btn_reiniciar.clicked.connect(self.reiniciar_simulacion_ui)
        layout.addWidget(self.btn_reiniciar)
        return panel

    def crear_panel_agregar_proceso(self):
        panel, layout, _ = self._crear_panel_base("Añadir Proceso")
        self.nombre_input = QLineEdit(placeholderText="Nombre del proceso")
        self.llegada_input = QLineEdit(placeholderText="Instante de Llegada"); self.llegada_input.setValidator(QIntValidator(0, 1000))
        self.tiempo_cpu_input = QLineEdit(placeholderText="Tiempo en CPU"); self.tiempo_cpu_input.setValidator(QIntValidator(1, 1000))
        self.btn_agregar = QPushButton("Agregar Proceso"); self.btn_agregar.clicked.connect(self.agregar_proceso_a_lista)
        layout.addWidget(self.nombre_input); layout.addWidget(self.llegada_input); layout.addWidget(self.tiempo_cpu_input); layout.addWidget(self.btn_agregar)
        return panel

    def crear_panel_procesos_agregados(self):
        panel, layout, _ = self._crear_panel_base("Procesos a Simular")
        self.tabla_procesos_nuevos = QTableWidget()
        self.tabla_procesos_nuevos.setColumnCount(6); self.tabla_procesos_nuevos.setHorizontalHeaderLabels(["PID", "Nombre", "Llegada", "CPU", "", ""])
        header = self.tabla_procesos_nuevos.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents); header.setSectionResizeMode(4, QHeaderView.ResizeToContents); header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabla_procesos_nuevos.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_procesos_nuevos)
        return panel

    def crear_panel_cronograma(self):
        panel, layout, title_label = self._crear_panel_base("Cronograma de Ejecución")
        self.tabla_cronograma = QTableWidget()
        self.tabla_cronograma.setShowGrid(True); self.tabla_cronograma.setStyleSheet("QTableWidget { gridline-color: #334155; }")
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True); scroll_area.setWidget(self.tabla_cronograma)
        layout.addWidget(scroll_area)
        return panel, self.tabla_cronograma, title_label

    def crear_panel_estadisticas(self):
        panel, layout, _ = self._crear_panel_base("Historial y Métricas Finales")
        self.tabla_estadisticas = QTableWidget()
        headers = ["Proceso", "Llegada (ti)", "CPU (t)", "Finalización (tf)", "Retorno (T)", "Espera (Te)", "Índice (I=t/T)"]
        self.tabla_estadisticas.setColumnCount(len(headers)); self.tabla_estadisticas.setHorizontalHeaderLabels(headers)
        self.tabla_estadisticas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_estadisticas.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla_estadisticas)
        return panel, self.tabla_estadisticas

    def agregar_proceso_a_lista(self):
        try:
            nombre = self.nombre_input.text().strip() or f"Proceso {self.pid_counter}"
            tiempo_cpu = int(self.tiempo_cpu_input.text()); llegada = int(self.llegada_input.text())
            if tiempo_cpu <= 0:
                CustomErrorDialog("El tiempo en CPU debe ser mayor que cero.", self).exec(); return
            self.procesos_para_simular.append(Proceso(self.pid_counter, nombre, tiempo_cpu, llegada))
            self.pid_counter += 1
            self._actualizar_tabla_procesos_nuevos()
            self.nombre_input.clear(); self.tiempo_cpu_input.clear(); self.llegada_input.clear()
        except ValueError:
            CustomErrorDialog("Los campos 'Llegada' y 'Tiempo en CPU' deben ser números válidos.", self).exec()
    
    def iniciar_simulacion_ui(self):
        if not self.procesos_para_simular:
            CustomErrorDialog("Agrega al menos un proceso antes de iniciar.", self).exec()
            return
        
        # Deshabilitar botones para evitar conflictos durante la animación
        self.btn_iniciar.setEnabled(False)
        self.btn_reiniciar.setEnabled(True)
        self.btn_agregar.setEnabled(False)

        algoritmo = self.combo_algoritmo.currentText()
        self.cronograma_title_label.setText(f"Cronograma de Ejecución ({algoritmo}) - Ejecutando...")
        
        # Preparamos la tabla del cronograma
        self.tabla_cronograma.clear()
        procesos_ordenados = sorted(self.procesos_para_simular, key=lambda p: p.pid)
        self.tabla_cronograma.setRowCount(len(procesos_ordenados))
        self.tabla_cronograma.setVerticalHeaderLabels([f"{p.nombre} (P{p.pid})" for p in procesos_ordenados])
        self.tabla_cronograma.setColumnCount(50) # Un número inicial de columnas
        self.tabla_cronograma.setHorizontalHeaderLabels([str(i) for i in range(50)])

        # Creamos el planificador y OBTENEMOS EL GENERADOR
        planificador = Planificador(self.procesos_para_simular, algoritmo, self.input_quantum.value())
        self.simulation_generator = planificador.ejecutar_simulacion()
        
        # Limpiamos tablas anteriores
        self.tabla_estadisticas.setRowCount(0)

        # Iniciamos el temporizador para que se ejecute cada 1 segundo (1000 ms)
        self.animation_timer.start(1000)


    def _avanzar_simulacion_paso(self):
        try:
            # Pedimos el siguiente estado al generador
            tiempo_actual, estados_del_tick = next(self.simulation_generator)
            
            # Si necesitamos más columnas en la tabla, las añadimos
            if tiempo_actual >= self.tabla_cronograma.columnCount():
                self.tabla_cronograma.setColumnCount(tiempo_actual + 10)
                # Actualizamos las cabeceras para las nuevas columnas
                self.tabla_cronograma.setHorizontalHeaderLabels([str(i) for i in range(self.tabla_cronograma.columnCount())])


            procesos_ordenados = sorted(self.procesos_para_simular, key=lambda p: p.pid)
            
            # Rellenamos la columna para el tiempo_actual
            for r, p in enumerate(procesos_ordenados):
                estado = estados_del_tick.get(p.pid, "")
                item = QTableWidgetItem(str(estado))
                item.setTextAlignment(Qt.AlignCenter)

                if estado == 'X':
                    item.setBackground(QColor("#22c55e"))
                    item.setForeground(QColor("#ffffff"))
                elif estado.isdigit():
                    item.setBackground(QColor("#f97316"))
                
                self.tabla_cronograma.setItem(r, tiempo_actual, item)
            
            # Hacemos scroll para que la columna actual sea visible
            self.tabla_cronograma.scrollToItem(self.tabla_cronograma.item(0, tiempo_actual))

        except StopIteration as e:
            # El generador se ha agotado (la simulación terminó)
            self.animation_timer.stop()
            self.cronograma_title_label.setText(f"Cronograma de Ejecución ({self.combo_algoritmo.currentText()}) - Finalizado")
            
            # El valor de 'return' del generador está en e.value
            estadisticas_dict = e.value
            if estadisticas_dict:
                 estadisticas_ordenadas = [estadisticas_dict[p.pid] for p in self.procesos_para_simular if p.pid in estadisticas_dict]
                 self.mostrar_estadisticas(estadisticas_ordenadas)
            
            # Volvemos a habilitar los botones
            self.btn_iniciar.setEnabled(True)
            self.btn_reiniciar.setEnabled(True)
            self.btn_agregar.setEnabled(True)


    def mostrar_cronograma(self, cronograma, duracion_total):
        self.tabla_cronograma.clearContents()
        columnas = max(duracion_total + 1, 30)
        self.tabla_cronograma.setColumnCount(columnas)
        self.tabla_cronograma.setHorizontalHeaderLabels([str(i) for i in range(columnas)])
        procesos_ordenados = sorted(self.procesos_para_simular, key=lambda p: p.pid)
        self.tabla_cronograma.setRowCount(len(procesos_ordenados))
        self.tabla_cronograma.setVerticalHeaderLabels([f"{p.nombre} (P{p.pid})" for p in procesos_ordenados])
        for r, p in enumerate(procesos_ordenados):
            for c, estado in enumerate(cronograma.get(p.pid, [])):
                if c >= columnas: break
                item = QTableWidgetItem(str(estado)); item.setTextAlignment(Qt.AlignCenter)
                if estado == 'X': item.setBackground(QColor("#22c55e")); item.setForeground(QColor("#ffffff"))
                elif estado.isdigit(): item.setBackground(QColor("#f97316"))
                self.tabla_cronograma.setItem(r, c, item)
        self.tabla_cronograma.resizeColumnsToContents()
        
    def mostrar_estadisticas(self, estadisticas):
        self.tabla_estadisticas.setRowCount(0)
        if not estadisticas: return
        self.tabla_estadisticas.setRowCount(len(estadisticas))
        total_indices = 0
        for r, data in enumerate(estadisticas):
            self.tabla_estadisticas.setItem(r, 0, QTableWidgetItem(data["proceso"]))
            self.tabla_estadisticas.setItem(r, 1, QTableWidgetItem(str(data["ti"])))
            self.tabla_estadisticas.setItem(r, 2, QTableWidgetItem(str(data["t"])))
            self.tabla_estadisticas.setItem(r, 3, QTableWidgetItem(str(data["tf"])))
            self.tabla_estadisticas.setItem(r, 4, QTableWidgetItem(str(data["T"])))
            self.tabla_estadisticas.setItem(r, 5, QTableWidgetItem(str(data["Te"])))
            self.tabla_estadisticas.setItem(r, 6, QTableWidgetItem(f'{data["I"]:.2f}')) # <-- Cambio a 2 decimales
            total_indices += data["I"]
        if estadisticas:
            promedio = total_indices / len(estadisticas)
            avg_row = self.tabla_estadisticas.rowCount()
            self.tabla_estadisticas.insertRow(avg_row)
            self.tabla_estadisticas.setSpan(avg_row, 0, 1, 6)
            bold_font = QFont(); bold_font.setBold(True)
            label_item = QTableWidgetItem("Promedio Índice de Servicio (I)"); label_item.setTextAlignment(Qt.AlignCenter); label_item.setFont(bold_font)
            promedio_item = QTableWidgetItem(f"{promedio:.2f}"); promedio_item.setTextAlignment(Qt.AlignCenter); promedio_item.setFont(bold_font) # <-- Cambio a 2 decimales
            self.tabla_estadisticas.setItem(avg_row, 0, label_item)
            self.tabla_estadisticas.setItem(avg_row, 6, promedio_item)

    def reiniciar_simulacion_ui(self):
        self.animation_timer.stop() # Detenemos el timer por si acaso
        self.procesos_para_simular.clear()
        self.pid_counter = 1
        self.procesos_para_simular.clear(); self.pid_counter = 1
        for table in [self.tabla_procesos_nuevos, self.tabla_cronograma, self.tabla_estadisticas]:
            table.setRowCount(0)
        self.tabla_cronograma.setColumnCount(0); self.btn_iniciar.setEnabled(True)
        self.cronograma_title_label.setText("Cronograma de Ejecución")
        # Reactivamos TODOS los botones para dejar la UI en su estado inicial.
        self.btn_iniciar.setEnabled(True)
        self.btn_agregar.setEnabled(True)  # <-- Esta línea faltaba y causaba el bug #2
        self.btn_reiniciar.setEnabled(True)

    def _actualizar_tabla_procesos_nuevos(self):
        self.tabla_procesos_nuevos.setRowCount(0)
        # Estilo para los botones de icono
        btn_style = "QPushButton { font-size: 18px; color: #ffffff; padding: 5px; max-width: 40px; border-radius: 4px; background-color: #3b82f6; } QPushButton:hover { background-color: #2563eb; }"
        for p in self.procesos_para_simular:
            row = self.tabla_procesos_nuevos.rowCount(); self.tabla_procesos_nuevos.insertRow(row)
            self.tabla_procesos_nuevos.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.tabla_procesos_nuevos.setItem(row, 1, QTableWidgetItem(p.nombre))
            self.tabla_procesos_nuevos.setItem(row, 2, QTableWidgetItem(str(p.instante_llegada)))
            self.tabla_procesos_nuevos.setItem(row, 3, QTableWidgetItem(str(p.tiempo_cpu_total)))
            
            btn_editar = QPushButton("✎"); btn_editar.setStyleSheet(btn_style) # <-- Icono minimalista
            btn_eliminar = QPushButton("✕"); btn_eliminar.setStyleSheet(btn_style.replace("#3b82f6", "#ef4444").replace("#2563eb", "#dc2626")) # <-- Icono minimalista
            
            pid = p.pid
            btn_editar.clicked.connect(lambda ch, p_id=pid: self.editar_proceso_ui(p_id))
            btn_eliminar.clicked.connect(lambda ch, p_id=pid: self.eliminar_proceso_ui(p_id))
            
            self.tabla_procesos_nuevos.setCellWidget(row, 4, btn_editar)
            self.tabla_procesos_nuevos.setCellWidget(row, 5, btn_eliminar)
    
    def eliminar_proceso_ui(self, pid):
        self.procesos_para_simular = [p for p in self.procesos_para_simular if p.pid != pid]
        self._actualizar_tabla_procesos_nuevos()

    def editar_proceso_ui(self, pid):
        proceso = next((p for p in self.procesos_para_simular if p.pid == pid), None)
        if not proceso: return
        dialog = EditProcessDialog(proceso, self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            proceso.nombre = data["nombre"] or f"Proceso {proceso.pid}"
            proceso.instante_llegada = data["llegada"]
            proceso.tiempo_cpu_total = data["tiempo_cpu"]
            self._actualizar_tabla_procesos_nuevos()

    def toggle_quantum_input(self, text):
        is_rr = (text == "Round Robin")
        self.label_quantum.setVisible(is_rr); self.input_quantum.setVisible(is_rr)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
