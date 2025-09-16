import sys
from collections import deque
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QComboBox, QSpinBox
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIntValidator

# Se importa la lógica real del simulador desde tu archivo core.py
from core import Simulador, Proceso

# Ventana de dialogo para los errores (sin cambios)
class CustomErrorDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error de Validación")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog { background-color: #1e293b; color: #e2e8f0; border-radius: 12px; }
            QLabel { color: #e2e8f0; font-size: 16px; padding: 10px; qproperty-wordWrap: true; }
            QPushButton { background-color: #ef4444; color: #ffffff; font-weight: bold; border-radius: 8px; padding: 10px 20px; border: none; }
            QPushButton:hover { background-color: #dc2626; }
        """)
        layout = QVBoxLayout(self)
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        self.ok_button = QPushButton("Aceptar")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)
        self.adjustSize()

# Configuramos la venta principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.simulador = Simulador()
        self.procesos_para_simular = []
        self.pid_counter = 1

        self.setWindowTitle("Simulador de Planificación de CPU")
        self.setGeometry(100, 100, 1400, 800)

        # Estilos CSS para la aplicación
        self.setStyleSheet("""
            QMainWindow, QWidget#centralWidget { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
            QFrame#card { background-color: #1e293b; border-radius: 12px; padding: 15px; }
            QLabel { color: #cbd5e1; padding-bottom: 5px; font-size: 14px; }
            QLabel#titleLabel { font-size: 18px; font-weight: bold; color: #e2e8f0; padding-bottom: 10px; }
            QLabel#cpuLabel { font-size: 22px; font-weight: bold; color: #22c55e; }
            QLabel#timeLabel { font-size: 28px; font-weight: bold; color: #e2e8f0; }
            QPushButton { background-color: #22c55e; color: #ffffff; font-weight: bold; border-radius: 8px; padding: 12px; border: none; }
            QPushButton:hover { background-color: #16a34a; }
            QPushButton#controlButton { background-color: #3b82f6; }
            QPushButton#controlButton:hover { background-color: #2563eb; }
            QPushButton#dangerButton { background-color: #ef4444; }
            QPushButton#dangerButton:hover { background-color: #dc2626; }
            QLineEdit, QComboBox, QSpinBox { background-color: #0f172a; color: #e2e8f0; border: 1px solid #334155; padding: 10px; border-radius: 8px; }
            QTableWidget { background-color: transparent; color: #e2e8f0; border: none; }
            QHeaderView::section { background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 10px; border: none; }
        """)

        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        # Layout principal dividido en tres columnas
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.left_column = self.crear_columna_izquierda()
        self.center_column = self.crear_columna_central()
        self.right_column = self.crear_columna_derecha()

        self.main_layout.addLayout(self.left_column, 2)
        self.main_layout.addLayout(self.center_column, 3)
        self.main_layout.addLayout(self.right_column, 2)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_ui)
        self.timer.start(500) # Actualiza la UI cada 500ms

    def _crear_panel_base(self, title):
        panel_frame = QFrame()
        panel_frame.setObjectName("card")
        panel_layout = QVBoxLayout(panel_frame)
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("titleLabel")
            panel_layout.addWidget(title_label)
        return panel_frame, panel_layout

    # --- Columnas de la UI ---
    def crear_columna_izquierda(self):
        layout = QVBoxLayout()
        layout.addWidget(self.crear_panel_configuracion())
        layout.addWidget(self.crear_panel_agregar_proceso())
        layout.addStretch(1)
        return layout

    def crear_columna_central(self):
        layout = QVBoxLayout()
        layout.addWidget(self.crear_panel_estado_simulacion())
        panel_cola_listos, self.tabla_cola_listos = self._crear_tabla(["PID", "Nombre", "Tiempo Restante"], "Cola de Procesos Listos")
        layout.addWidget(panel_cola_listos)
        return layout

    def crear_columna_derecha(self):
        layout = QVBoxLayout()
        panel_procesos_nuevos, self.tabla_procesos_nuevos = self._crear_tabla(["PID", "Nombre", "Tiempo CPU", "Llegada"], "Procesos a Simular")
        panel_procesos_terminados, self.tabla_terminados = self._crear_tabla(["PID", "Nombre", "Tiempo CPU"], "Historial de Procesos")
        layout.addWidget(panel_procesos_nuevos)
        layout.addWidget(panel_procesos_terminados)
        return layout
    
    # --- Paneles específicos ---
    def crear_panel_configuracion(self):
        panel, layout = self._crear_panel_base("Configuración de Simulación")
        
        layout.addWidget(QLabel("Algoritmo de Planificación:"))
        self.combo_algoritmo = QComboBox()
        self.combo_algoritmo.addItems(["FCFS", "SJF", "SRTF", "Round Robin"])
        self.combo_algoritmo.currentTextChanged.connect(self.toggle_quantum_input)
        layout.addWidget(self.combo_algoritmo)
        
        self.label_quantum = QLabel("Quantum de tiempo:")
        self.input_quantum = QSpinBox()
        self.input_quantum.setRange(1, 100)
        self.input_quantum.setValue(2)
        self.label_quantum.hide()
        self.input_quantum.hide()
        layout.addWidget(self.label_quantum)
        layout.addWidget(self.input_quantum)

        self.btn_iniciar = QPushButton("Iniciar Simulación")
        self.btn_iniciar.clicked.connect(self.iniciar_simulacion_ui)
        layout.addWidget(self.btn_iniciar)
        
        self.btn_reiniciar = QPushButton("Reiniciar Simulación")
        self.btn_reiniciar.setObjectName("dangerButton")
        self.btn_reiniciar.clicked.connect(self.reiniciar_simulacion_ui)
        layout.addWidget(self.btn_reiniciar)
        
        return panel
        
    def crear_panel_agregar_proceso(self):
        panel, layout = self._crear_panel_base("Añadir Proceso")
        
        self.nombre_input = QLineEdit(placeholderText="Nombre del proceso")
        self.tiempo_cpu_input = QLineEdit(placeholderText="Tiempo en CPU (unidades)")
        self.tiempo_cpu_input.setValidator(QIntValidator(1, 1000))
        self.llegada_input = QLineEdit(placeholderText="Instante de Llegada (unidades)")
        self.llegada_input.setValidator(QIntValidator(0, 1000))
        
        self.btn_agregar = QPushButton("Agregar Proceso a la Cola")
        self.btn_agregar.clicked.connect(self.agregar_proceso_a_lista)
        
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.tiempo_cpu_input)
        layout.addWidget(self.llegada_input)
        layout.addWidget(self.btn_agregar)

        return panel

    def crear_panel_estado_simulacion(self):
        panel, layout = self._crear_panel_base("Estado de la Simulación")
        layout.setSpacing(10)

        # Panel para el tiempo
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Tiempo Actual:"))
        self.label_tiempo_simulacion = QLabel("0")
        self.label_tiempo_simulacion.setObjectName("timeLabel")
        time_layout.addStretch()
        time_layout.addWidget(self.label_tiempo_simulacion)
        layout.addLayout(time_layout)

        # Panel para la CPU
        cpu_layout = QVBoxLayout()
        cpu_layout.setContentsMargins(0, 10, 0, 0)
        cpu_layout.addWidget(QLabel("PROCESO EN CPU:"))
        self.label_cpu_proceso = QLabel("CPU Ociosa")
        self.label_cpu_proceso.setObjectName("cpuLabel")
        self.label_cpu_proceso.setAlignment(Qt.AlignCenter)
        cpu_layout.addWidget(self.label_cpu_proceso)
        layout.addLayout(cpu_layout)
        
        return panel

    def _crear_tabla(self, headers, title):
        panel, layout = self._crear_panel_base(title)
        table = QTableWidget()
        table.setShowGrid(False) 
        table.verticalHeader().setVisible(False) 
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        return panel, table

    # --- Lógica de la Interfaz ---
    def agregar_proceso_a_lista(self):
        try:
            nombre = self.nombre_input.text().strip()
            tiempo_cpu_str = self.tiempo_cpu_input.text().strip()
            llegada_str = self.llegada_input.text().strip()
            
            if not nombre or not tiempo_cpu_str or not llegada_str:
                CustomErrorDialog("Todos los campos son obligatorios.", self).exec()
                return

            tiempo_cpu = int(tiempo_cpu_str)
            llegada = int(llegada_str)

            if tiempo_cpu <= 0:
                CustomErrorDialog("El tiempo en CPU debe ser un valor positivo.", self).exec()
                return

            nuevo_proceso = Proceso(self.pid_counter, nombre, tiempo_cpu, llegada)
            self.procesos_para_simular.append(nuevo_proceso)
            self.pid_counter += 1
            
            self._actualizar_tabla_procesos_nuevos()
            
            for input_field in [self.nombre_input, self.tiempo_cpu_input, self.llegada_input]:
                input_field.clear()

        except ValueError:
            CustomErrorDialog("Por favor, ingresa valores numéricos válidos.", self).exec()
    
    def iniciar_simulacion_ui(self):
        if not self.procesos_para_simular:
            CustomErrorDialog("Agrega al menos un proceso antes de iniciar.", self).exec()
            return

        algoritmo = self.combo_algoritmo.currentText()
        quantum = self.input_quantum.value()
        
        self.simulador.configurar_simulacion(self.procesos_para_simular, algoritmo, quantum)
        self.simulador.iniciar_simulacion()
        
        # Deshabilitar controles para evitar modificaciones durante la ejecución
        self.btn_iniciar.setEnabled(False)
        self.btn_agregar.setEnabled(False)
        self.combo_algoritmo.setEnabled(False)
        self.input_quantum.setEnabled(False)
        
    def reiniciar_simulacion_ui(self):
        self.simulador.reiniciar_estado()
        self.procesos_para_simular = []
        self.pid_counter = 1
        
        # Limpiar todas las tablas
        self.tabla_procesos_nuevos.setRowCount(0)
        self.tabla_cola_listos.setRowCount(0)
        self.tabla_terminados.setRowCount(0)
        
        # Restablecer etiquetas
        self.label_tiempo_simulacion.setText("0")
        self.label_cpu_proceso.setText("CPU Ociosa")
        
        # Habilitar controles
        self.btn_iniciar.setEnabled(True)
        self.btn_agregar.setEnabled(True)
        self.combo_algoritmo.setEnabled(True)
        self.input_quantum.setEnabled(True)
        
    def toggle_quantum_input(self, text):
        is_rr = (text == "Round Robin")
        self.label_quantum.setVisible(is_rr)
        self.input_quantum.setVisible(is_rr)

    def actualizar_ui(self):
        with self.simulador.lock:
            # Actualizar tiempo
            self.label_tiempo_simulacion.setText(str(self.simulador.tiempo_simulacion))
            
            # Actualizar Proceso en CPU
            if self.simulador.proceso_en_cpu:
                p = self.simulador.proceso_en_cpu
                self.label_cpu_proceso.setText(f"P{p.pid} - {p.nombre} (Restante: {p.tiempo_restante_cpu})")
            else:
                self.label_cpu_proceso.setText("CPU Ociosa")
            
            # Actualizar tablas
            self._actualizar_tabla(self.tabla_cola_listos, self.simulador.cola_listos, lambda p: [f"P{p.pid}", p.nombre, p.tiempo_restante_cpu])
            self. _actualizar_tabla(self.tabla_terminados, self.simulador.procesos_terminados, lambda p: [f"P{p.pid}", p.nombre, p.tiempo_cpu])

    def _actualizar_tabla_procesos_nuevos(self):
        self._actualizar_tabla(self.tabla_procesos_nuevos, self.procesos_para_simular, lambda p: [f"P{p.pid}", p.nombre, p.tiempo_cpu, p.instante_llegada])

    def _actualizar_tabla(self, table, data, row_formatter):
        table.setRowCount(0)
        for item in data:
            row_data = row_formatter(item)
            row = table.rowCount()
            table.insertRow(row)
            for col, text in enumerate(row_data):
                table_item = QTableWidgetItem(str(text))
                table_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, table_item)
    
    def closeEvent(self, event):
        self.simulador.ejecutando = False
        super().closeEvent(event)