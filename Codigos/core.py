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
            self.instante_llegada = instante_llegada
            

            # Estas variables "privadas" almacenarán los valores reales.
            self._tiempo_cpu_total = 0 
            self.tiempo_restante_cpu = 0
            
            # Asignamos el valor inicial a través de la "property" para que 
            # ambas variables se sincronicen desde el principio.
            self.tiempo_cpu_total = tiempo_cpu  # Esto llamará al método "setter" de abajo
        

    @property
    def tiempo_cpu_total(self):
        """Este es el "getter". Se ejecuta cuando lees 'proceso.tiempo_cpu_total'."""
        return self._tiempo_cpu_total


    @tiempo_cpu_total.setter
    def tiempo_cpu_total(self, value):
        """
        Este es el "setter". Se ejecuta cuando asignas un valor, 
        (ej: 'proceso.tiempo_cpu_total = 5'). Aquí sincronizamos
        'tiempo_restante_cpu' con el nuevo valor.
        """
        self._tiempo_cpu_total = value
        self.tiempo_restante_cpu = value


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

    # En la clase Planificador dentro de core.py

    def ejecutar_simulacion(self):
        """
        Ejecuta la simulación paso a paso como un generador, produciendo ('yield')
        el estado en cada instante de tiempo. Al final, devuelve las estadísticas.
        """
        tiempo_actual = 0
        
        procesos_nuevos = deque(self.procesos_originales)
        cola_listos = deque()
        
        proceso_en_cpu = None
        quantum_timer = 0

        instantes_finalizacion = {}
        
        # Bucle principal de la simulación
        while procesos_nuevos or cola_listos or proceso_en_cpu:

            # 1. Mover procesos de 'nuevos' a 'listos'
            while procesos_nuevos and procesos_nuevos[0].instante_llegada <= tiempo_actual:
                cola_listos.append(procesos_nuevos.popleft())

            # 2. Lógica de desalojo (preemption) para RR y SRTF
            if proceso_en_cpu:
                # Desalojo por Quantum en Round Robin
                if self.algoritmo == "Round Robin" and quantum_timer >= self.quantum:
                    cola_listos.append(proceso_en_cpu)
                    proceso_en_cpu = None
                
                # Desalojo por llegada de proceso más corto en SRTF
                if self.algoritmo == "SRTF" and cola_listos:
                    proceso_mas_corto_en_cola = min(cola_listos, key=lambda p: p.tiempo_restante_cpu)
                    if proceso_en_cpu.tiempo_restante_cpu > proceso_mas_corto_en_cola.tiempo_restante_cpu:
                        cola_listos.append(proceso_en_cpu)
                        proceso_en_cpu = None

            # 3. Seleccionar un nuevo proceso para la CPU si está libre
            if not proceso_en_cpu and cola_listos:
                if self.algoritmo in ["FCFS", "Round Robin"]:
                    proceso_en_cpu = cola_listos.popleft()
                elif self.algoritmo == "SJF":
                    cola_listos = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_cpu_total))
                    proceso_en_cpu = cola_listos.popleft()
                elif self.algoritmo == "SRTF":
                    cola_listos = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_restante_cpu))
                    proceso_en_cpu = cola_listos.popleft()
                quantum_timer = 0

            estados_del_tick = {}
            cola_listos_display = cola_listos
            # ... (código para preparar estados_del_tick se mantiene igual) ...
            if self.algoritmo == "SJF":
                cola_listos_display = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_cpu_total))
            elif self.algoritmo == "SRTF":
                cola_listos_display = deque(sorted(list(cola_listos), key=lambda p: p.tiempo_restante_cpu))
            pids_en_cola = {p.pid: i for i, p in enumerate(cola_listos_display)}
            for p_orig in self.procesos_originales:
                estado_actual = ''
                if p_orig.pid in instantes_finalizacion: estado_actual = ''
                elif tiempo_actual < p_orig.instante_llegada: estado_actual = ''
                elif proceso_en_cpu and p_orig.pid == proceso_en_cpu.pid: estado_actual = 'X'
                elif p_orig.pid in pids_en_cola: estado_actual = str(pids_en_cola[p_orig.pid] + 1)
                else: estado_actual = ' '
                estados_del_tick[p_orig.pid] = estado_actual

            # Calculamos el tiempo total restante de todos los procesos activos
            tiempo_restante_total = (proceso_en_cpu.tiempo_restante_cpu if proceso_en_cpu else 0) + \
                                    sum(p.tiempo_restante_cpu for p in cola_listos) + \
                                    sum(p.tiempo_restante_cpu for p in procesos_nuevos)
            
            # Modificamos el yield para que también entregue el tiempo restante
            yield tiempo_actual, estados_del_tick, tiempo_restante_total           

            
            # 4. Procesar el tick de tiempo en la CPU
            if proceso_en_cpu:
                proceso_en_cpu.tiempo_restante_cpu -= 1
                quantum_timer += 1
                if proceso_en_cpu.tiempo_restante_cpu <= 0:
                    instantes_finalizacion[proceso_en_cpu.pid] = tiempo_actual + 1
                    proceso_en_cpu = None
                    quantum_timer = 0

            # 5. Avanzar el tiempo
            tiempo_actual += 1
            if tiempo_actual > 500: break # Salvaguarda

        # --- Fin del bucle: Calculamos y devolvemos las estadísticas ---
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
        
        # El 'return' en un generador se usa para devolver el valor final
        # cuando la iteración termina.
        return estadisticas_dict

