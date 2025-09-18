# Simulador de Planificación de Procesos — Manual técnico

**Proyecto:** PR2-SO — Segundo Proyecto de Sistemas Operativos (Grupo #7, Sección B)

---

# Requisitos técnicos

**Lenguaje usado:**
Python 3.10 o superior (probado también en Python 3.11, 3.12 y 3.13).

**Entorno de Desarrollo:**
Cualquier IDE o editor compatible con Python. Recomendado: **PyCharm**, **Visual Studio Code** o directamente ejecución con terminal. La GUI utiliza PySide6, por lo que es recomendable un entorno con soporte gráfico.

**Python Development Kit:**
Se requiere tener instalado Python y `pip` para gestionar dependencias.

**Bibliotecas utilizadas:**

* **PySide6**: Base para la construcción de la GUI con Qt (QMainWindow, QWidget, QTableWidget, QDialog, QPushButton, QVBoxLayout, etc.).
* **shiboken6**: Dependencia necesaria para PySide6.
* **collections (deque)**: Uso en la simulación de colas de procesos.
* **copy (deepcopy)**: Para clonar procesos al inicio de la simulación.
* **sys**: Usado en `main.py` para inicializar la aplicación Qt.

**Clases personalizadas (módulos del proyecto):**

* `core.Proceso`: Modelo que representa a un proceso (PID, nombre, llegada, ráfaga de CPU).
* `core.Planificador`: Implementa los algoritmos de planificación (FCFS, SJF, SRTF, Round Robin).
* `gui.CustomErrorDialog`: Cuadro de diálogo para mostrar errores.
* `gui.EditProcessDialog`: Diálogo para editar un proceso.
* `gui.MainWindow`: Ventana principal que controla el flujo de la aplicación (agregar procesos, seleccionar algoritmo, ejecutar simulación, mostrar cronograma y estadísticas).

**Estructura de carpetas:**

```
PR2-SO/
├─ Codigos/
│  ├─ core.py        # Lógica central (Proceso, Planificador)
│  ├─ gui.py         # Interfaz gráfica (MainWindow, diálogos)
│  └─ main.py        # Punto de entrada a la aplicación
├─ requirements.txt  # Dependencias del proyecto
```

**Sistema Operativo:**
Multiplataforma: Windows, Linux o macOS (requiere entorno gráfico para abrir la GUI).

**Recursos externos:**
Ninguno. Todo se maneja dentro del programa. El usuario interactúa con la interfaz gráfica para ingresar procesos y configurar el algoritmo.

---

# Explicación de cada archivo y sus funciones

## `core.py`

Este archivo contiene la lógica principal del simulador.

### Clase `Proceso`

* Representa un proceso del sistema.
* Atributos: `pid`, `nombre`, `tiempo_cpu_total`, `instante_llegada`, `tiempo_restante_cpu`.
* Función: sirve como modelo de datos, no contiene lógica compleja.

### Clase `Planificador`

* Encargada de ejecutar la simulación según el algoritmo seleccionado.
* Constructor recibe: lista de procesos, algoritmo (`FCFS`, `SJF`, `SRTF`, `Round Robin`) y quantum (si aplica).
* Método `ejecutar_simulacion()`: genera el cronograma, duración total y estadísticas por proceso.
* Implementa:

  * **FCFS:** First-Come, First-Served, no expropiativo.
  * **SJF:** Shortest Job First, no expropiativo.
  * **SRTF:** Shortest Remaining Time First, expropiativo.
  * **Round Robin:** Expropiativo, con quantum configurable.
* Calcula estadísticas: `ti` (llegada), `t` (CPU total), `tf` (finalización), `T` (turnaround), `Te` (espera), `I` (uso relativo de CPU).

---

## `gui.py`

Este archivo define la interfaz gráfica de la aplicación usando PySide6.

### Clase `CustomErrorDialog`

* Ventana emergente para mostrar mensajes de error.

### Clase `EditProcessDialog`

* Permite modificar los datos de un proceso ya agregado.
* Devuelve los datos editados en formato diccionario.

### Clase `MainWindow`

* Ventana principal de la aplicación.
* Paneles:

  * **Configuración:** elegir algoritmo y quantum.
  * **Agregar proceso:** formulario para introducir procesos.
  * **Procesos agregados:** tabla con los procesos, permite editar/eliminar.
  * **Cronograma:** tabla donde se muestra la ejecución por instantes.
  * **Estadísticas:** tabla con métricas de cada proceso.
* Métodos clave:

  * `agregar_proceso_a_lista()`: añade un proceso nuevo.
  * `iniciar_simulacion_ui()`: ejecuta la simulación con el planificador.
  * `mostrar_cronograma()`: pinta en la tabla los estados por instante.
  * `mostrar_estadisticas()`: muestra métricas finales.
  * `reiniciar_simulacion_ui()`: limpia todos los datos para empezar de nuevo.

---

## `main.py`

Archivo de inicio de la aplicación.

* Importa `QApplication` y `MainWindow`.
* Crea la instancia de la app y abre la ventana principal.
* Permite ejecutar la aplicación con:

```bash
python Codigos/main.py
```

---

# Requisitos técnicos

A continuación los **requerimientos técnicos** del proyecto, presentados en el formato que solicitaste.

**Lenguaje usado:**
Python

**Entorno de desarrollo:**
Cualquier IDE/Editor que soporte Python (recomendados: PyCharm, Visual Studio Code, Thonny). El proyecto también funciona en entornos ligeros o en la terminal. Se recomienda usar un IDE con soporte para diseño de ventanas (inspección de widgets) si se edita la GUI.

**Versión de Python (interpreter):**
Python **3.10** — **3.13** (probado con 3.13). Se recomienda usar al menos **3.10** para compatibilidad con las construcciones del código.

**Entorno virtual:**
Se recomienda usar un entorno virtual (venv, virtualenv, conda) para instalar dependencias localmente y evitar conflictos con otras instalaciones de Python.

**Bibliotecas / Librerías utilizadas:**

* `PySide6` (Qt for Python) — construcción y manejo de la GUI (ventanas, widgets, validadores, layouts). Versión utilizada en desarrollo: **6.9.2** (instalable con `pip install PySide6==6.9.2`).
* Módulos estándar de Python usados en el proyecto:

  * `collections` (ej. `deque`) — manejo eficiente de colas para la simulación.
  * `copy` — copias profundas de listas/objetos cuando es necesario clonar el estado de los procesos.
  * `sys` — para recoger `argv` y lanzar la app (en `main.py` / `gui.py`).
* No hay dependencias binarias externas aparte de PySide6.

**Clases/módulos personalizados (paquete del proyecto):**

* `Codigos/core.py` → lógica del simulador (clases `Proceso`, `Planificador`).
* `Codigos/gui.py` → interfaz de usuario (ventana principal `MainWindow`, diálogos y formularios).
* `Codigos/main.py` → punto de entrada que crea la aplicación Qt y abre la ventana principal.

**Sistema operativo (SO):**
Funciona en **Windows**, **Linux** y **macOS** siempre que exista una instalación válida de Python y PySide6. En Linux puede requerirse instalar paquetes adicionales del sistema si aparecen errores del plugin de plataforma Qt.

**Recursos externos / Archivos de entrada y salida:**

* El proyecto no requiere archivos externos obligatorios para ejecutarse (la GUI permite crear procesos desde la interfaz). Si se agregan importadores/exportadores, entonces se necesita el archivo de entrada correspondiente.

**Recomendaciones de instalación rápida:**

1. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows (cmd)
   ```
2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   # o si falla con codificación:
   pip install PySide6==6.9.2
   ```
3. Ejecutar la aplicación:

   ```bash
   python Codigos/main.py
   ```

**Notas de compatibilidad / problemas comunes:**

* Si aparece `ModuleNotFoundError: No module named 'PySide6'`, instala PySide6 en el entorno activo.
* En Linux/macOS: si Qt reclama problemas con la plataforma (`qt.qpa.plugin`), instala las dependencias del sistema (por ejemplo `libxcb` en algunas distros) o usa una versión de PySide6 compatible con tu SO.
* Si el `requirements.txt` tiene problemas de codificación, vuelve a guardarlo en UTF-8 o instala manualmente PySide6.

---

# Explicación detallada por archivo Python (qué hace cada archivo y qué funciones/métodos cumple)

> Aquí se detalla, archivo por archivo, las responsabilidades principales, clases y funciones públicas y privadas (métodos) que implementa cada uno. La explicación describe los parámetros esperados, lo que hace cada método y qué devuelve o efectos secundarios produce.

## `Codigos/core.py` — Lógica del simulador

**Resumen general:**
Contiene las estructuras de datos y la lógica para simular algoritmos de planificación de CPU (scheduling). Se definen los procesos como objetos y el `Planificador` que ejecuta la simulación y calcula cronograma y métricas.

### Clase `Proceso`

**Constructor:** `__init__(self, pid, nombre, tiempo_cpu, instante_llegada)`

* Parámetros:

  * `pid` (int): identificador único del proceso.
  * `nombre` (str): nombre legible del proceso (ej. "P1" o "Proceso A").
  * `tiempo_cpu` (int): ráfaga total de CPU que requiere el proceso (tiempo total de ejecución).
  * `instante_llegada` (int): instante discreto en el que el proceso llega al sistema (ej. 0, 1, 2...).
* Efectos / Atributos principales creados:

  * `tiempo_cpu_total` (int): guarda el valor original de la ráfaga.
  * `instante_llegada` (int): como se recibió.
  * `tiempo_restante_cpu` (int): inicializado con `tiempo_cpu_total`; decrementa durante la simulación.
* No devuelve nada. Es una simple estructura de datos; no implementa comportamiento complejo.

### Clase `Planificador`

**Constructor:** `Planificador(self, procesos, algoritmo, quantum=2)`

* Parámetros:

  * `procesos` (lista de `Proceso`): lista de procesos a simular. El planificador hace internamente copias para no mutar la lista original.
  * `algoritmo` (str): nombre del algoritmo a usar. Valores esperados: `'FCFS'`, `'SJF'`, `'SRTF'`, `'Round Robin'`.
  * `quantum` (int, opcional): usado por Round Robin; valor por defecto `2`.
* Efecto: prepara estructuras internas y conserva una copia de los procesos originales para cálculo de métricas.

**Método principal:** `ejecutar_simulacion(self)`

* Descripción: corre la simulación por instantes discretos aplicando la lógica del algoritmo elegido; produce un cronograma por instante y calcula estadísticas por proceso.
* Flujo general interno (resumen técnico):

  1. Ordena los procesos por instante de llegada y los coloca en una cola de entrada.
  2. Mantiene un `tiempo_actual` que avanza de 0 hasta que todos los procesos hayan finalizado.
  3. Usa una `cola_listos` (`deque`) para representar la cola de procesos listos para ejecutar.
  4. Según `algoritmo`: selecciona el próximo proceso a ejecutar (política FCFS/SJF/SRTF o Round Robin con `quantum`).
  5. Actualiza `tiempo_restante_cpu` del proceso en ejecución, registra en el `cronograma` que ese proceso usó la CPU en ese instante (marca `'X'`), y, si corresponde, actualiza la cola (preempciones o rotación por quantum).
  6. Cuando un proceso completa su `tiempo_restante_cpu == 0`, registra su `instante_finalizacion`.
  7. Continúa hasta que no queden procesos en entrada, cola ni CPU ocupada.
* Valores devueltos: `cronograma, duracion_total, estadisticas_dict`.

  * `cronograma`: estructura (diccionario) que mapea `pid` → lista de longitud igual a la duración de la simulación; cada elemento representa el estado del proceso en ese instante (`'X'` para ejecutando, cadena vacía o indicador de posición en cola según implementación interna).
  * `duracion_total`: número entero de instantes simulados (longitud de la timeline).
  * `estadisticas_dict`: diccionario `pid` → dict con claves `proceso`, `ti`, `t`, `tf`, `T`, `Te`, `I`:

    * `ti`: instante de llegada.
    * `t`: tiempo total de CPU (ráfaga original).
    * `tf`: instante de finalización.
    * `T`: turnaround = `tf - ti`.
    * `Te`: tiempo de espera = `T - t`.
    * `I`: `t / T` (proporción de tiempo activo dentro del turnaround), redondeada.

**Casos particulares y comportamiento por algoritmo:**

* **FCFS**: no preemptivo. Cuando la CPU toma un proceso lo ejecuta hasta acabar.
* **SJF**: selección no preemptiva del proceso con menor `tiempo_cpu_total` al momento de elegir.
* **SRTF**: preemptivo: si llega un proceso con menor `tiempo_restante_cpu` que el actual, se preempciona.
* **Round Robin**: asigna la CPU por intervalos (`quantum`); al agotarse el quantum el proceso se reencola si no terminó.

**Complejidad:**

* La simulación avanza por instantes; en el peor caso la complejidad está acotada por `O(D * log P)` o `O(D * P)` según la implementación interna para seleccionar procesos, donde `D` es la duración total simulada y `P` el número de procesos. Para escalas didácticas (decenas de procesos, pocos cientos de instantes) el rendimiento es suficiente.

**Validaciones internas:**

* Se usan copias de los objetos para no modificar la lista original de entrada.
* El método evita bucles infinitos limitando la duración máxima (protección contra errores en algunos escenarios). Si la implementación tiene un límite (por ejemplo `tiempo_actual > 500`), revisa y ajusta según necesites simular escenarios más largos.

---

## `Codigos/gui.py` — Interfaz gráfica (GUI)

**Resumen general:**
Este archivo contiene la ventana principal y varios diálogos auxiliares. Gestiona la interacción con el usuario: creación y edición de procesos, selección de algoritmo y quantum, inicio de la simulación y despliegue del cronograma y las estadísticas calculadas por `core.Planificador`.

### Clase `CustomErrorDialog(QDialog)`

* **Responsabilidad:** mostrar mensajes de error o validación al usuario con estilo.
* **Métodos relevantes:**

  * `__init__(self, message, parent=None)`: crea el diálogo con el `message` que se mostrará; no devuelve nada.
* Uso: llamado cuando las entradas del usuario no son válidas (ej. campos vacíos, valores no numéricos, quantum no válido, etc.).

### Clase `EditProcessDialog(QDialog)`

* **Responsabilidad:** formulario modal que permite editar los datos de un proceso ya creado.
* **Métodos relevantes:**

  * `__init__(self, proceso, parent=None)`: inicializa el diálogo con los valores actuales del proceso (nombre, llegada, tiempo CPU) para que el usuario los modifique.
  * `get_data(self)`: al cerrar con aceptar, devuelve un `dict` con las claves `"nombre"`, `"llegada"` y `"tiempo_cpu"` con los valores actualizados. Uso típico: `data = dialog.get_data()`.

### Clase `MainWindow(QMainWindow)`

* **Responsabilidad:** controla la aplicación; contiene widgets, tablas y botones; gestiona la lista interna de procesos y coordina la ejecución de la simulación con `Planificador`.

**Atributos internos importantes:**

* `procesos_para_simular` (lista de `Proceso`): lista mutable que contiene los procesos añadidos desde la GUI.
* `pid_counter` (int): generador de PIDs (se incrementa cada vez que se crea un proceso nuevo).
* Widgets claves: `combo_algoritmo` (selector de algoritmo), `input_quantum` (QSpinBox para RR), `tabla_procesos_nuevos` (QTableWidget con los procesos definidos), `tabla_cronograma`, `tabla_estadisticas`, y campos de entrada (`nombre_input`, `llegada_input`, `tiempo_cpu_input`).

**Métodos principales y explicación por método:**

* `__init__(self)`: construye toda la interfaz y conecta señales (botones, combos) con sus manejadores.

* `_crear_panel_base(self, title)`: utilidad interna que crea un marco/panel con título y estilo; usado por los paneles hijos para mantener consistencia visual.

* `crear_panel_controles(self)`: (o `crear_panel_configuracion`, según versión) crea el layout para seleccionar algoritmo, mostrar/ocultar `input_quantum` cuando se selecciona Round Robin y botones globales (Iniciar Simulación, Reiniciar, etc.).

  * **Efecto:** conecta la selección de algoritmo para disparar `toggle_quantum_input`.

* `crear_panel_configuracion(self)`: crea y arma los widgets específicos de configuración (combo de algoritmo, label/entrada de quantum, etc.).

* `crear_panel_agregar_proceso(self)`: crea los widgets del formulario para agregar un proceso (Nombre, Llegada, Tiempo CPU) y el botón `Agregar Proceso`.

  * **Validaciones realizadas:** campos numéricos validados con `QIntValidator` o `QSpinBox`; se verifica que la llegada y tiempo sean enteros positivos; se asegura que el nombre sea no vacío o se genera uno por defecto.

* `crear_panel_procesos_agregados(self)`: crea la tabla que muestra los procesos añadidos y botones para editar/eliminar por fila.

* `crear_panel_cronograma(self)`: crea la tabla donde se volcará el cronograma resultado de la simulación.

* `crear_panel_estadisticas(self)`: crea la tabla donde se mostrarán las métricas por proceso (ti, t, tf, T, Te, I).

* `agregar_proceso_a_lista(self)`: **manejador** del botón "Agregar Proceso".

  * Lee los valores de `nombre_input`, `llegada_input` y `tiempo_cpu_input`.
  * Valida entradas (enteros, rangos, no negativos) y muestra `CustomErrorDialog` si falla.
  * Crea `Proceso(self.pid_counter, nombre, tiempo_cpu, llegada)` y lo añade a `procesos_para_simular`.
  * Incrementa `pid_counter` y actualiza la tabla de procesos agregados llamando a `_actualizar_tabla_procesos_nuevos()`.

* `iniciar_simulacion_ui(self)`: **manejador** del botón "Iniciar Simulación".

  * Verifica que exista al menos un proceso en `procesos_para_simular`.
  * Lee opción de algoritmo y quantum (si aplica).
  * Instancia `Planificador(procesos_para_simular, algoritmo, quantum)` y llama `ejecutar_simulacion()`.
  * Recibe `cronograma, duracion_total, estadisticas` y llama a `mostrar_cronograma()` y `mostrar_estadisticas()` para renderizar tablas.

* `mostrar_cronograma(self, cronograma, duracion_total)`: renderiza la tabla de cronograma en la GUI.

  * Columnas: instantes `0..duracion_total-1`.
  * Filas: procesos (ordenados por PID o el orden que decida la interfaz).
  * Marca con `'X'` los instantes que cada proceso ejecutó, puede colorear celdas o ajustar fuente para mayor claridad.

* `mostrar_estadisticas(self, estadisticas)`: rellena la tabla de estadísticas con los campos `proceso, ti, t, tf, T, Te, I` para cada proceso.

* `reiniciar_simulacion_ui(self)`: limpia la lista `procesos_para_simular`, reinicia `pid_counter` y borra las tablas de cronograma y estadísticas para empezar de cero.

* `_actualizar_tabla_procesos_nuevos(self)`: función auxiliar que recarga `tabla_procesos_nuevos` con los procesos actuales de `procesos_para_simular`. Incluye columnas para `PID`, `Nombre`, `Llegada`, `Tiempo CPU` y acciones (Editar / Eliminar).

* `eliminar_proceso_ui(self, pid)`: quita el proceso con `pid` de `procesos_para_simular` y llama a `_actualizar_tabla_procesos_nuevos()`.

* `editar_proceso_ui(self, pid)`: abre `EditProcessDialog` para el proceso identificado; si el usuario acepta los cambios, actualiza el objeto `Proceso` y la tabla.

* `toggle_quantum_input(self, text)`: muestra u oculta el `input_quantum` de la GUI dependiendo de si el algoritmo seleccionado es `Round Robin`.

**Validaciones y UX en la GUI:**

* La GUI valida entradas en el frontend (QIntValidator, checkeo de valores) antes de construir objetos `Proceso`.
* Los errores de usuario se comunican con `CustomErrorDialog`.
* La interfaz prioriza claridad: tablas con encabezados fijos, scroll si la duración es amplia, y ocultación de `quantum` cuando no aplica.

---

## `Codigos/main.py` — Punto de entrada

**Responsabilidad:** inicializar la aplicación Qt y abrir la ventana principal.

**Contenido y comportamiento:**

* Importa `QApplication` y `MainWindow`.
* Crea la instancia `app = QApplication(sys.argv)`.
* Instancia `window = MainWindow()` y la muestra con `window.show()`.
* Llama a `sys.exit(app.exec())` para iniciar el loop de eventos de Qt.

**Notas:**

* No contiene lógica de la simulación; su única función es ejecutar la GUI. Esto facilita usar `core.py` desde scripts o tests sin inicializar la GUI.

---

# Notas finales y recomendaciones de mantenimiento

* Documenta cualquier cambio interno en `core.Planificador` (si agregas nuevos algoritmos o métricas, actualiza el README y los tests).
* Si vas a ampliar la GUI con importación/exportación, añade `Codigos/io.py` (o un paquete `utils/`) para separar la lógica de E/S y mantener la GUI limpia.
* Añade pruebas unitarias (`tests/`) que instancien `Planificador` con escenarios controlados y verifiquen que `estadisticas_dict` coincide con resultados esperados.


