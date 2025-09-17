from collections import deque
import copy

class Proceso:
    """
    Representa un proceso con los atributos necesarios para la planificación.
    Es una estructura de datos simple.
    """
    def __init__(self, pid, nombre, tiempo_cpu, instante_llegada):
        self.pid = pid
        self.nombre = nombre
        self.tiempo_cpu_total = tiempo_cpu  # Tiempo de ráfaga original
        self.instante_llegada = instante_llegada
        
        # Atributos que cambiarán durante la simulación
        self.tiempo_restante_cpu = self.tiempo_cpu_total

class Planificador:
    """
    Calcula el cronograma completo de ejecución de los procesos
    basado en el algoritmo de planificación seleccionado.
    """
    def __init__(self, procesos, algoritmo, quantum=2):
        # Usamos una copia profunda para no modificar los objetos originales de la GUI
        self.procesos_originales = sorted([copy.deepcopy(p) for p in procesos], key=lambda p: p.instante_llegada)
        self.algoritmo = algoritmo
        self.quantum = quantum

    def ejecutar_simulacion(self):
        """
        Ejecuta la simulación completa y devuelve el cronograma, la duración total,
        y las estadísticas de rendimiento de cada proceso.
        """
        tiempo_actual = 0
        
        procesos_nuevos = deque(self.procesos_originales)
        cola_listos = deque()
        
        proceso_en_cpu = None
        quantum_timer = 0

        cronograma = {p.pid: [] for p in self.procesos_originales}
        instantes_finalizacion = {}
        
        while procesos_nuevos or cola_listos or proceso_en_cpu:

            while procesos_nuevos and procesos_nuevos[0].instante_llegada <= tiempo_actual:
                cola_listos.append(procesos_nuevos.popleft())

            if proceso_en_cpu:
                if self.algoritmo == "Round Robin" and quantum_timer >= self.quantum:
                    cola_listos.append(proceso_en_cpu)
                    proceso_en_cpu = None
                
                if self.algoritmo == "SRTF" and cola_listos:
                    proceso_mas_corto_en_cola = min(cola_listos, key=lambda p: p.tiempo_restante_cpu)
                    if proceso_en_cpu.tiempo_restante_cpu > proceso_mas_corto_en_cola.tiempo_restante_cpu:
                        cola_listos.append(proceso_en_cpu)
                        proceso_en_cpu = None

            if not proceso_en_cpu and cola_listos:
                if self.algoritmo in ["FCFS", "Round Robin"]:
                    proceso_en_cpu = cola_listos.popleft()
                elif self.algoritmo == "SJF":
                    # For SJF (non-preemptive), sort the ready queue only when choosing a new process
                    cola_listos = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_cpu_total))
                    proceso_en_cpu = cola_listos.popleft()
                elif self.algoritmo == "SRTF":
                    # For SRTF, sort the ready queue to always pick the one with the least remaining time
                    cola_listos = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_restante_cpu))
                    proceso_en_cpu = cola_listos.popleft()
                quantum_timer = 0
            
            # Lógica para mostrar las posiciones en la cola (1, 2, 3...)
            # Para la visualización, necesitamos ordenar la cola de listos según las reglas del algoritmo actual.
            
            cola_listos_display = cola_listos
            if self.algoritmo == "SJF":
                # Para SJF, la cola de visualización se ordena por el tiempo total de CPU
                cola_listos_display = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_cpu_total))
            elif self.algoritmo == "SRTF":
                # Para SRTF, la cola de visualización se ordena por el tiempo restante de CPU
                cola_listos_display = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_restante_cpu))

            pids_en_cola = {p.pid: i for i, p in enumerate(cola_listos_display)}
            
            for p_orig in self.procesos_originales:
                estado_actual = ''
                if p_orig.pid in instantes_finalizacion: estado_actual = '' 
                elif tiempo_actual < p_orig.instante_llegada: estado_actual = '' 
                elif proceso_en_cpu and p_orig.pid == proceso_en_cpu.pid: estado_actual = 'X' 
                elif p_orig.pid in pids_en_cola: estado_actual = str(pids_en_cola[p_orig.pid] + 1)
                else: estado_actual = ' ' 
                cronograma[p_orig.pid].append(estado_actual)

            if proceso_en_cpu:
                proceso_en_cpu.tiempo_restante_cpu -= 1
                quantum_timer += 1
                if proceso_en_cpu.tiempo_restante_cpu <= 0:
                    instantes_finalizacion[proceso_en_cpu.pid] = tiempo_actual + 1
                    proceso_en_cpu = None
                    quantum_timer = 0

            tiempo_actual += 1
            if tiempo_actual > 500: break # Salvaguarda para evitar bucles infinitos
                
        duracion_total = tiempo_actual -1 

        estadisticas_dict = {}
        for p in self.procesos_originales:
            ti = p.instante_llegada
            t = p.tiempo_cpu_total
            tf = instantes_finalizacion.get(p.pid, 0)
            T = tf - ti
            Te = T - t
            I = round(t / T, 4) if T > 0 else 0
            
            estadisticas_dict[p.pid] = {
                "proceso": f"{p.nombre} (P{p.pid})", "ti": ti, "t": t,
                "tf": tf, "T": T, "Te": Te, "I": I
            }

        return cronograma, duracion_total, estadisticas_dict

