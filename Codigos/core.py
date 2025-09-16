import time
import threading
from collections import deque

# Esta clase representa cada proceso con sus nuevos atributos para la planificación.
class Proceso:
    def __init__(self, pid, nombre, tiempo_cpu, instante_llegada):
        self.pid = pid  # Identificador único numérico
        self.nombre = nombre
        self.tiempo_cpu = tiempo_cpu  # Tiempo total requerido en CPU
        self.instante_llegada = instante_llegada
        
        self.tiempo_restante_cpu = self.tiempo_cpu  # Tiempo que aún le falta por ejecutar
        self.estado = "Nuevo"  # Estados: Nuevo, Listo, En Ejecución, Terminado
        
        # Atributos para el algoritmo Round Robin
        self.tiempo_en_cpu_actual = 0

# Es el cerebro de la operación, maneja el tiempo, los procesos,
# la ejecución en hilos y la lógica de los algoritmos de planificación.
class Simulador:
    def __init__(self):
        self.procesos_nuevos = []      # Procesos que aún no han llegado a la simulación
        self.cola_listos = deque()     # Procesos que han llegado y esperan por la CPU (usamos deque para eficiencia)
        self.procesos_terminados = []  # Historial de procesos completados
        self.proceso_en_cpu = None     # Proceso que está usando la CPU actualmente
        
        self.algoritmo_planificacion = "FCFS"
        self.quantum = 2  # Valor por defecto para Round Robin
        
        self.tiempo_simulacion = 0     # Reloj global de la simulación (en unidades de tiempo)
        
        self.ejecutando = False  # Flag para controlar el bucle principal del hilo
        self.pausado = False     # Flag para pausar/reanudar la simulación
        
        # Lock para proteger el acceso a las listas de procesos desde la GUI y el simulador
        self.lock = threading.Lock()
        self.hilo_ejecucion = None

    def configurar_simulacion(self, lista_procesos, algoritmo, quantum=2):
        """Prepara el simulador con los procesos y la configuración inicial."""
        with self.lock:
            # Ordenamos los procesos por su instante de llegada para facilitar la simulación
            self.procesos_nuevos = sorted(lista_procesos, key=lambda p: p.instante_llegada)
            self.algoritmo_planificacion = algoritmo
            self.quantum = quantum
            self.reiniciar_estado() # Resetea el estado para una nueva simulación

    def iniciar_simulacion(self):
        """Inicia el hilo de simulación si no está ya corriendo."""
        if not self.ejecutando:
            self.ejecutando = True
            self.hilo_ejecucion = threading.Thread(target=self.ejecutar_simulacion, daemon=True)
            self.hilo_ejecucion.start()

    def ejecutar_simulacion(self):
        """El bucle principal que corre en el hilo secundario."""
        while self.ejecutando:
            if not self.pausado:
                with self.lock:
                    # 1. Mover procesos de 'Nuevos' a 'Listos' si ya es su tiempo de llegada
                    procesos_llegados = [p for p in self.procesos_nuevos if p.instante_llegada <= self.tiempo_simulacion]
                    for p in procesos_llegados:
                        p.estado = "Listo"
                        self.cola_listos.append(p)
                    self.procesos_nuevos = [p for p in self.procesos_nuevos if p.instante_llegada > self.tiempo_simulacion]
                    
                    # Lógica de preempción para SRTF
                    if self.algoritmo_planificacion == "SRTF" and self.proceso_en_cpu and self.cola_listos:
                        if self.proceso_en_cpu.tiempo_restante_cpu > min(self.cola_listos, key=lambda p: p.tiempo_restante_cpu).tiempo_restante_cpu:
                            proceso_expropiado = self.proceso_en_cpu
                            proceso_expropiado.estado = "Listo"
                            self.cola_listos.append(proceso_expropiado)
                            self.proceso_en_cpu = None

                    # 2. Si la CPU está libre, seleccionar el siguiente proceso
                    if self.proceso_en_cpu is None and self.cola_listos:
                        self.seleccionar_proceso()

                    # 3. Ejecutar el proceso en la CPU
                    if self.proceso_en_cpu:
                        self.proceso_en_cpu.tiempo_restante_cpu -= 1
                        self.proceso_en_cpu.tiempo_en_cpu_actual += 1

                        # Si el proceso termina
                        if self.proceso_en_cpu.tiempo_restante_cpu <= 0:
                            self.proceso_en_cpu.estado = "Terminado"
                            self.procesos_terminados.append(self.proceso_en_cpu)
                            self.proceso_en_cpu = None
                        # Lógica de preempción para Round Robin
                        elif self.algoritmo_planificacion == "Round Robin" and self.proceso_en_cpu.tiempo_en_cpu_actual >= self.quantum:
                            proceso_expropiado = self.proceso_en_cpu
                            proceso_expropiado.estado = "Listo"
                            self.cola_listos.append(proceso_expropiado) # Vuelve al final de la cola
                            self.proceso_en_cpu = None
                
                # Avanza el tiempo y verifica si la simulación ha terminado
                if self.lock.locked():
                    self.tiempo_simulacion += 1
                    
                    # Condición para detener la simulación
                    if not self.proceso_en_cpu and not self.cola_listos and not self.procesos_nuevos:
                        self.ejecutando = False
            
            # Cada unidad de tiempo en la simulación dura 1 segundo en tiempo real
            time.sleep(1)
            
    def seleccionar_proceso(self):
        """Selecciona el siguiente proceso de la cola de listos según el algoritmo."""
        if not self.cola_listos:
            return
            
        if self.algoritmo_planificacion == "FCFS":
            self.proceso_en_cpu = self.cola_listos.popleft()
        elif self.algoritmo_planificacion == "SJF":
            # SJF no expropiativo: ordena la cola y saca el más corto
            self.cola_listos = deque(sorted(list(self.cola_listos), key=lambda p: p.tiempo_cpu))
            self.proceso_en_cpu = self.cola_listos.popleft()
        elif self.algoritmo_planificacion == "SRTF":
            # SRTF expropiativo: ordena por tiempo restante y saca el más corto
            self.cola_listos = deque(sorted(list(self.cola_listos), key=lambda p: p.tiempo_restante_cpu))
            self.proceso_en_cpu = self.cola_listos.popleft()
        elif self.algoritmo_planificacion == "Round Robin":
            self.proceso_en_cpu = self.cola_listos.popleft()
            
        if self.proceso_en_cpu:
            self.proceso_en_cpu.estado = "En Ejecución"
            self.proceso_en_cpu.tiempo_en_cpu_actual = 0 # Resetea el contador de quantum

    def pausar_simulacion(self):
        self.pausado = True

    def reanudar_simulacion(self):
        self.pausado = False

    def reiniciar_estado(self):
        """Limpia el estado del simulador para una nueva ejecución."""
        self.cola_listos.clear()
        self.procesos_terminados.clear()
        self.proceso_en_cpu = None
        self.tiempo_simulacion = 0
        self.ejecutando = False
        self.pausado = False