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
