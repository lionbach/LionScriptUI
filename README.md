# LionScriptUI

Una biblioteca ligera y modular basada en **wxPython** para generar formularios dinámicos y elegantes de forma declarativa mediante archivos JSON.

## 🚀 Características

- **Formularios Dinámicos**: Crea ventanas complejas con pocas líneas de código.
- **Soporte JSON**: Genera interfaces completas pasando un objeto JSON como argumento.
- **Layout Responsivo**: Contenedores con scroll automático y ajuste de ancho inteligente.
- **Tipos de Elementos**:
  - Títulos y etiquetas con ajuste de texto.
  - Listas de selección simple y múltiple (`ListBox`).
  - Menús desplegables (`Choice`).
  - Grupos de opciones (`RadioBox`).
  - Casillas de verificación (`CheckBox`).
  - Botones de acción (Aceptar/Cancelar).

## 🛠️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd LionScriptUI
   ```

2. **Configurar el entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Uso

Puedes ejecutar el script `main.py` pasando un JSON directamente o un archivo:

```bash
# Usando un string JSON
python main.py "{\"window_title\":\"Test\",\"form_elements\":{\"t1\":{\"type\":\"title\",\"data\":\"Hola\"}}}"

# Usando un archivo JSON
python main.py --file mi_formulario.json
```

## 📂 Estructura del Proyecto

- `form_manager.py`: La lógica central de la interfaz y el motor de renderizado.
- `main.py`: Punto de entrada CLI para procesar datos JSON.
- `requirements.txt`: Dependencias del proyecto (wxPython).
- `examples/`: Scripts de demostración y utilidades.
- `extras/`: Herramientas adicionales como binarios de `jq`.

## 📝 Notas de Desarrollo

- Los títulos y etiquetas no devuelven valores en el JSON de salida.
- El estado `status` en el resultado puede ser `ok`, `cancel`, `close` o `error`.
- Diseñado para ser fácilmente extensible con nuevos tipos de widgets.

---
*Desarrollado por Lionbach.*
