# PR2-SO
Segundo Proyecto de Sistemas Operativos, Grupo #7, Sección "B"
# Simulador de Planificación de Procesos — Manual técnico

**Proyecto:** PR2-SO — Segundo Proyecto de Sistemas Operativos (Grupo #7, Sección B)

> Este documento es un manual técnico completo del proyecto incluido en la carpeta `PR2-SO`. Contiene instrucciones de instalación y ejecución, descripción detallada de cada módulo y clase, explicación de los algoritmos implementados, ejemplos de uso, y recomendaciones para ampliar o depurar el programa.

---

# Índice

1. Descripción general
2. Requisitos e instalación
3. Estructura del proyecto
4. Uso rápido (arranque)
5. Explicación detallada de los módulos

   * `core.py` (lógica / simulador)
   * `gui.py` (interfaz gráfica)
   * `main.py` (punto de entrada)
6. Formato de salida: cronograma y estadísticas
7. Ejemplos de uso (vía GUI y por código)
8. Posibles errores y solución de problemas
9. Extensiones recomendadas
10. Información adicional y licencia

---

# 1. Descripción general

Este proyecto implementa un simulador didáctico de planificación de procesos (scheduling) con interfaz gráfica. Permite crear procesos (PID, nombre, instante de llegada y tiempo de CPU), seleccionar un algoritmo de planificación (FCFS, SJF, SRTF, Round Robin), ejecutar la simulación y visualizar:

* Un **cronograma** (tabla con una columna por instante de tiempo y filas por proceso) que muestra en cada instante si un proceso está ejecutando, en cola, o ya finalizó.
* Una tabla de **estadísticas** por proceso: instante de llegada, tiempo de CPU, tiempo de finalización, tiempo de retorno, tiempo de espera y un índice de utilización relativo.

El objetivo es permitir experimentar con distintos algoritmos de planificación y observar sus efectos en métricas clave.

---

# 2. Requisitos e instalación

## Requisitos de software

* **Python**: se recomienda Python **3.10+** (el proyecto se probó con versiones recientes; los bytecode indican uso en 3.13). Recomendación práctica: usar Python 3.10, 3.11, 3.12 o 3.13.
* **Pip** para instalar dependencias.

## Dependencias del proyecto

El fichero `requirements.txt` del proyecto contiene (versiones usadas en desarrollo):

```
PySide6==6.9.2
PySide6_Addons==6.9.2
PySide6_Essentials==6.9.2
shiboken6==6.9.2
```

> **Nota**: el fichero `requirements.txt` puede estar en codificación UTF-16 (dependiendo de cómo se guardó). Si `pip install -r requirements.txt` falla por codificación, instale directamente las dependencias con `pip install PySide6==6.9.2 shiboken6==6.9.2`.

## Instalación paso a paso (recomendado)

1. Clona o extrae el proyecto en una carpeta local.
2. Crea un entorno virtual y actívalo:

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate
```

3. Actualiza `pip` (opcional):

```bash
pip install --upgrade pip
```

4. Instala dependencias:

```bash
pip install -r requirements.txt
# Si hay problemas con la codificación del archivo:
pip install PySide6==6.9.2 PySide6_Addons==6.9.2 PySide6_Essentials==6.9.2 shiboken6==6.9.2
```

---

# 3. Estructura del proyecto

Resumen de los archivos/directorios principales:

```
PR2-SO/
├─ Codigos/
│  ├─ core.py        # Lógica central: clases Proceso y Planificador
│  ├─ gui.py         # Interfaz gráfica (MainWindow, diálogos)
│  └─ main.py        # Punto de entrada (lanza la aplicación Qt)
├─ requirements.txt  # Dependencias (PySide6 ...)
├─ README.md         # README original breve
└─ .git/             # metadatos del repo
```

---

# 4. Uso rápido (arranque)

Con el entorno virtual activado y las dependencias instaladas, desde la carpeta `PR2-SO` ejecuta:

```bash
python Codigos/main.py
```

Esto abrirá la ventana principal donde podrás:

1. Seleccionar el algoritmo de planificación.
2. (Si eliges Round Robin) ajustar el `quantum` (tiempo de ráfaga por turno).
3. Añadir procesos con `Nombre`, `Llegada` (instante entero, e.g. 0,1,2...) y `Tiempo en CPU` (ráfaga en unidades de tiempo).
4. Iniciar la simulación y visualizar cronograma y estadísticas.

---

# 5. Explicación detallada de los módulos

A continuación se documenta con detalle cada archivo y las clases / métodos importantes.

## 5.1 `core.py` — Lógica y simulador

Contiene la lógica del simulador y las estructuras que representan procesos y la planificación.

### Clase `Proceso`

**Descripción:** representa un proceso en el sistema.

**Constructor:** `Proceso(pid, nombre, tiempo_cpu, instante_llegada)`

**Atributos principales:**

* `pid` (int): identificador único del proceso.
* `nombre` (str): nombre descriptivo (p. ej. "P1" o "Proceso 1").
* `tiempo_cpu_total` (int): ráfaga original (tiempo total de CPU requerido por el proceso).
* `instante_llegada` (int): instante en el que el proceso llega al sistema.
* `tiempo_restante_cpu` (int): tiempo restante de CPU (inicialmente igual a `tiempo_cpu_total`, se decrementa durante la simulación).

> Comentario: En la GUI se crean objetos `Proceso` y se pasan al planificador. La clase es una estructura de datos simple y no contiene lógica de planificación.

### Clase `Planificador`

**Descripción:** ejecuta la simulación de planificación según el algoritmo elegido. Se encarga de generar el cronograma por instante y calcular estadísticas por proceso.

**Constructor:** `Planificador(procesos, algoritmo, quantum=2)`

* `procesos`: lista de objetos `Proceso` (se hace una copia profunda y se ordenan por `instante_llegada` internamente).
* `algoritmo`: cadena con el algoritmo elegido — soportados: `"FCFS"`, `"SJF"`, `"SRTF"`, `"Round Robin"`.
* `quantum`: entero usado por `Round Robin` (valor por defecto `2`).

**Método principal:** `ejecutar_simulacion()`

Devuelve una tupla con `(cronograma, duracion_total, estadisticas_dict)`.

#### Funcionamiento general (resumen técnico):

* Se mantiene un reloj `tiempo_actual` que avanza por unidades discretas.
* `procesos_nuevos`: `deque` con procesos ordenados por llegada que aún no han entrado a la cola de listos.
* `cola_listos`: `deque` que representa la cola de listos (ready queue).
* `proceso_en_cpu`: referencia al proceso que está ejecutando en el instante.
* `quantum_timer`: contador auxiliar para RR: cuando alcanza `quantum`, el proceso se vuelve a encolar.
* `cronograma`: diccionario `pid -> lista` donde cada posición de la lista representa el estado del proceso en un instante de tiempo (por ejemplo `'X'` significa ejecutando en ese instante, un número como `'1'`, `'2'` indica posición en la cola, `''` o `' '` para estados vacíos o finalizados).
* `instantes_finalizacion`: diccionario `pid -> tiempo_de_finalizacion` cuando un proceso termina.

#### Implementación de algoritmos

* **FCFS (First-Come, First-Served):** no preemptivo. Cuando la CPU está libre, se extrae el primer proceso de `cola_listos` (`deque.popleft()`) y se ejecuta hasta su finalización.

* **SJF (Shortest Job First) — no preemptivo:** al seleccionar un proceso para ejecutar, la cola se ordena por `tiempo_cpu_total` y se escoge el más corto. No preempciona procesos en ejecución.

* **SRTF (Shortest Remaining Time First) — preemptivo:** se compara el `tiempo_restante_cpu` del proceso en CPU con el de los que están en cola; si llega uno con menor tiempo restante, se preempciona (se reencola el actual y se ejecuta el más corto).

* **Round Robin (RR) — preemptivo por quantum:** el planificador lleva un contador `quantum_timer`; si alcanza `quantum`, el proceso en CPU se reencola al final de `cola_listos` y la CPU pasa al siguiente.

#### Cálculo de estadísticas

Para cada proceso `p` se calculan (nombres usados en la salida):

* `ti`: instante de llegada (`instante_llegada`).
* `t`: tiempo CPU total (`tiempo_cpu_total`).
* `tf`: instante de finalización (cuando se termina de ejecutar por última vez).
* `T`: tiempo de retorno / turnaround = `tf - ti`.
* `Te`: tiempo de espera = `T - t`.
* `I`: `t / T` (proporción del tiempo de retorno durante el cual el proceso estuvo ocupando CPU). Se redondea a 4 decimales. *Interpreta `I` como "porcentaje/proporción de uso activo dentro del turnaround".*

La función `ejecutar_simulacion()` devuelve los datos listos para que la GUI los muestre.

---

## 5.2 `gui.py` — Interfaz gráfica (Qt / PySide6)

Este módulo define toda la interfaz: diálogo de errores, diálogo de edición de un proceso y la ventana principal (`MainWindow`).

### Clases principales

#### `CustomErrorDialog(QDialog)`

Diálogo sencillo para mostrar mensajes de error al usuario (validaciones, inputs inválidos, etc.).

#### `EditProcessDialog(QDialog)`

Formulario que se utiliza para editar los datos de un proceso existente. Expone `get_data()` que devuelve un `dict` con los campos actualizados: `{"nombre":..., "llegada":..., "tiempo_cpu":...}`.

#### `MainWindow(QMainWindow)` — descripción general

**Responsabilidad:** crear y organizar los paneles de la aplicación, capturar entradas del usuario, mantener la lista de procesos, instanciar el `Planificador` y mostrar resultados.

**Atributos clave (internos):**

* `procesos_para_simular` (lista): almacena los objetos `Proceso` añadidos desde la UI.
* `pid_counter` (int): contador incremental para asignar PIDs a los procesos nuevos (inicia en 1 y se incrementa con cada adición).
* Widgets principales: `combo_algoritmo`, `input_quantum`, `tabla_procesos_nuevos`, `tabla_cronograma`, `tabla_estadisticas`, campos de entrada (`nombre_input`, `llegada_input`, `tiempo_cpu_input`).

**Paneles y métodos de interés:**

* `_crear_panel_base(title)`: plantilla para crear paneles con estilo (tarjetas).
* `crear_panel_configuracion()`: panel con selector de algoritmo (`FCFS`, `SJF`, `SRTF`, `Round Robin`) y `quantum` (SpinBox oculto, visible solo para RR).
* `crear_panel_agregar_proceso()`: formulario con campos `Nombre`, `Llegada` y `Tiempo en CPU`, y botón `Agregar Proceso`.
* `crear_panel_procesos_agregados()`: tabla que muestra los procesos añadidos y botones para `Editar` / `Eliminar` por fila.
* `crear_panel_cronograma()` y `crear_panel_estadisticas()`: paneles que contienen las tablas donde se muestran los resultados.

**Acciones del usuario implementadas:**

* `agregar_proceso_a_lista()`: valida las entradas, crea una instancia `Proceso(self.pid_counter, nombre, tiempo_cpu, llegada)`, la agrega a `procesos_para_simular`, incrementa `pid_counter`, y actualiza la tabla.
* `iniciar_simulacion_ui()`: valida que haya procesos, crea `Planificador(procesos_para_simular, algoritmo, quantum)`, llama a `ejecutar_simulacion()` y pasa los resultados a `mostrar_cronograma()` y `mostrar_estadisticas()`.
* `mostrar_cronograma(cronograma, duracion_total)`: pinta la tabla con el cronograma. Columnas = instantes de tiempo, filas = procesos (ordenados por PID). Los estados pueden ser:

  * `'X'` → proceso en ejecución en ese instante.
  * `"1"`, `"2"`, ... → posición en la cola de listos en ese instante (si aplica).
  * `''` o `' '` → vacío / no aplicable.
* `mostrar_estadisticas(estadisticas)`: rellena la tabla de estadísticas por proceso con `proceso, ti, t, tf, T, Te, I`.
* `reiniciar_simulacion_ui()`: limpia `procesos_para_simular`, reinicia `pid_counter` a 1 y borra tablas y resultados.
* `editar_proceso_ui(pid)` y `eliminar_proceso_ui(pid)`: permiten modificar o quitar procesos ya agregados.

**Validaciones y UX:**

* Los campos `Llegada` y `Tiempo en CPU` están validados para aceptar solo enteros dentro de rangos establecidos.
* Si hay errores en entradas, se muestra `CustomErrorDialog` con el mensaje correspondiente.

---

## 5.3 `main.py`

Archivo mínimo que crea la aplicación Qt y lanza la ventana principal:

```python
from PySide6.QtWidgets import QApplication
from gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

---

# 6. Formato de salida: cronograma y estadísticas

## Cronograma

* Tipo: `dict` donde cada clave es el `pid` y el valor es una lista. Cada elemento en la lista corresponde a un instante de tiempo (columna en la tabla) y contiene:

  * `'X'` si el proceso estuvo ejecutando en ese instante.
  * Un número en cadena (`"1"`, "2", ...) que indica la posición del proceso en la cola de listos durante ese instante (si la implementación rellena esa información).
  * `''` o `' '` para indicar ausencia de actividad.

**Duración total**: entero con la cantidad de instantes simulados (variable `duracion_total`).

## Estadísticas por proceso

Cada entrada es un diccionario con claves: `proceso` (texto descriptivo), `ti`, `t`, `tf`, `T`, `Te`, `I`.

* `ti` = instante de llegada.
* `t` = tiempo en CPU.
* `tf` = instante de finalización.
* `T` = turnaround = `tf - ti`.
* `Te` = tiempo de espera = `T - t`.
* `I` = `t / T` (proporción del turnaround en ejecución activa).

---

# 7. Ejemplos de uso

## 7.1 Uso por GUI

1. Ejecuta `python Codigos/main.py`.
2. En "Configuración" elige por ejemplo `Round Robin` y ajusta `Quantum = 2`.
3. Agrega procesos:

   * Nombre: P1, Llegada: 0, Tiempo en CPU: 5
   * Nombre: P2, Llegada: 1, Tiempo en CPU: 3
   * Nombre: P3, Llegada: 2, Tiempo en CPU: 6
4. Pulsa `Iniciar Simulación`.

La tabla de cronograma mostrará en cada columna (instante de tiempo) qué proceso se ejecutó o quién estaba en la cola. La tabla de estadísticas muestra los tiempos calculados.

## 7.2 Uso programático (sin GUI)

Puedes usar las clases en `core.py` desde un script Python para hacer tests automáticos o análisis por lotes.

```python
from core import Proceso, Planificador

p1 = Proceso(1, 'P1', 5, 0)
p2 = Proceso(2, 'P2', 3, 1)
p3 = Proceso(3, 'P3', 6, 2)

plan = Planificador([p1,p2,p3], algoritmo='Round Robin', quantum=2)
cronograma, duracion_total, estadisticas = plan.ejecutar_simulacion()

print('Duración total:', duracion_total)
print('Cronograma:', cronograma)
print('Estadísticas:')
for pid, data in estadisticas.items():
    print(pid, data)
```

---

# 8. Posibles errores y solución de problemas

### Error: `ModuleNotFoundError: No module named 'PySide6'`

Instala las dependencias: `pip install -r requirements.txt` o instala PySide6 manualmente: `pip install PySide6==6.9.2`.

### Problemas con `requirements.txt` (codificación UTF-16)

Si `pip` se queja al leer el archivo (error de codificación), abre `requirements.txt` en un editor y vuelve a guardarlo en UTF-8, o usa la línea de instalación manual indicada arriba.

### La ventana no aparece o falla al iniciar la aplicación (Qt plugin errors)

* En Linux, puede faltar la plataforma Qt (paquetes del sistema). Instala las dependencias Qt de tu distribución o prueba con un entorno virtual y la versión correcta de PySide.
* Revisa el `stderr` para ver mensajes sobre `Qt platform` y busca soluciones específicas a tu SO.

### Otros consejos de depuración

* Añade `print()` en `core.py` dentro del bucle de simulación para trazar `tiempo_actual`, `cola_listos` y `proceso_en_cpu` si necesitas entender por qué un proceso no termina.
* Si el cronograma muestra demasiadas columnas o bucles, hay una protección (`if tiempo_actual > 500: break`) para evitar bucles infinitos; puedes ajustar ese valor para pruebas más largas.

---

# 9. Extensiones recomendadas

Ideas para mejorar o ampliar el proyecto:

* Exportar cronograma y estadísticas a CSV o PDF.
* Añadir visualizaciones gráficas (barras de tiempo) usando `matplotlib` o exportar a imagen.
* Permitir parámetros adicionales por proceso (prioridad, E/S simulada) y agregar algoritmos con prioridades.
* Implementar métricas agregadas (promedio de tiempo de espera, promedio de turnaround, utilización CPU global).
* Añadir tests unitarios que creen escenarios concretos y verifiquen resultados (por ejemplo, comparar la salida del planificador contra un resultado esperado conocido).

---

# 10. Información adicional y licencia

* Autor / Grupo: **Grupo #7, Sección "B"** (según README original del repositorio).
* Licencia: puedes añadir tu licencia preferida (por defecto no incluida). Una opción habitual es MIT.

---

# Apéndice: Glosario de variables y conceptos

* **PID**: identificador único de proceso.
* **Instante de llegada (ti)**: momento en que el proceso entra al sistema.
* **Tiempo en CPU (t)**: ráfaga total necesaria por el proceso.
* **Tiempo de finalización (tf)**: instante en que el proceso terminó su ejecución completa.
* **Turnaround (T)**: `tf - ti`.
* **Tiempo de espera (Te)**: `T - t`.
* **Quantum**: tiempo máximo de CPU otorgado por turno en Round Robin.

---

Si quieres, puedo:

* Generar una **versión PDF** de este manual técnico.
* Añadir ejemplos concretos con imágenes (capturas de la GUI) si me proporcionas capturas.
* Crear tests unitarios de referencia para los algoritmos (archivos `tests/test_*`).

¡Listo! Revisa el documento y dime si quieres que lo adapte a otro formato (PDF, DOCX), que incluya diagramas o ejemplos más detallados para un algoritmo en particular.
