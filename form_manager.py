import wx

# ============================================================
# Constantes de configuración
# ============================================================
MAX_CONTAINER_WIDTH = 600
MAX_ELEMENT_WIDTH = 600
PADDING = 10

# Tipos que son solo texto (no devuelven valor en el resultado)
_TEXT_TYPES = {"title", "label"}


# ============================================================
# Funciones de extracción de valores (registro modular)
# ============================================================

def _extract_listbox(widget):
    """Extrae la selección de un ListBox simple → string."""
    sel = widget.GetSelection()
    return widget.GetString(sel) if sel != wx.NOT_FOUND else ""


def _extract_listbox_multiple(widget):
    """Extrae las selecciones de un ListBox múltiple → list[string]."""
    return [widget.GetString(i) for i in widget.GetSelections()]


def _extract_choice(widget):
    """Extrae la selección de un Choice → string."""
    sel = widget.GetSelection()
    return widget.GetString(sel) if sel != wx.NOT_FOUND else ""


def _extract_checkbox(widget_list):
    """Extrae los checkboxes marcados → list[string]."""
    return [cb.GetLabel() for cb in widget_list if cb.IsChecked()]


def _extract_radiobox(widget):
    """Extrae la selección del RadioBox → string."""
    sel = widget.GetSelection()
    return widget.GetString(sel) if sel != wx.NOT_FOUND else ""


# Mapeo kind → función extractora
# Para agregar un nuevo tipo, basta con definir su función y registrarla aquí.
_VALUE_EXTRACTORS = {
    "listbox":          _extract_listbox,
    "listbox_multiple": _extract_listbox_multiple,
    "choice":           _extract_choice,
    "checkbox":         _extract_checkbox,
    "radiobox":         _extract_radiobox,
}


# ============================================================
# Funciones internas para crear widgets
# ============================================================

def _add_titulo(parent, sizer, texto):
    """Texto centrado, fuente grande y bold, con wrap."""
    label = wx.StaticText(parent, label=texto, style=wx.ALIGN_CENTER)
    label._original_label = texto
    font = label.GetFont()
    font.SetPointSize(14)
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    label.SetFont(font)
    sizer.Add(label, 0, wx.EXPAND | wx.ALL, PADDING)
    return label


def _add_label(parent, sizer, texto):
    """Texto alineado a la izquierda con wrap."""
    label = wx.StaticText(parent, label=texto)
    label._original_label = texto
    sizer.Add(label, 0, wx.EXPAND | wx.ALL, PADDING)
    return label


def _add_listbox(parent, sizer, opciones, multiple=False):
    """ListBox centrado, ancho máximo configurable. Ajustado para mostrar todos los items."""
    style = wx.LB_MULTIPLE if multiple else 0
    lb = wx.ListBox(parent, choices=opciones, style=style)
    
    # Calcular altura para mostrar todos los elementos sin scroll
    count = lb.GetCount()
    if count > 0:
        line_height = lb.GetCharHeight()
        total_height = (line_height * count) + 8
        lb.SetMinSize(wx.Size(-1, total_height))

    lb.SetMaxSize(wx.Size(MAX_ELEMENT_WIDTH, -1))
    sizer.Add(lb, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, PADDING)
    return lb


def _add_choice(parent, sizer, opciones):
    """Choice centrado, ancho máximo configurable."""
    ch = wx.Choice(parent, choices=opciones)
    ch.SetMaxSize(wx.Size(MAX_ELEMENT_WIDTH, -1))
    ch.SetSelection(0)
    sizer.Add(ch, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, PADDING)
    return ch


def _add_botones(parent, sizer, textos):
    """Botones centrados, uno al lado del otro. Retorna dict {label: btn}."""
    btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
    buttons = {}
    for texto in textos:
        btn = wx.Button(parent, label=texto)
        btn_sizer.Add(btn, 0, wx.ALL, 5)
        buttons[texto] = btn
    sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, PADDING)
    return buttons


def _add_checkbox(parent, sizer, opciones):
    """Grupo de checkboxes, centrado. Retorna lista de CheckBox widgets."""
    box = wx.StaticBox(parent)
    box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
    checkboxes = []
    for texto in opciones:
        cb = wx.CheckBox(parent, label=texto)
        box_sizer.Add(cb, 0, wx.ALL, 3)
        checkboxes.append(cb)
    sizer.Add(box_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, PADDING)
    return checkboxes


def _add_radiobox(parent, sizer, opciones):
    """RadioBox (selección única), centrado."""
    rb = wx.RadioBox(parent, label="", choices=opciones,
                     majorDimension=1, style=wx.RA_SPECIFY_COLS)
    rb.SetMaxSize(wx.Size(MAX_ELEMENT_WIDTH, -1))
    sizer.Add(rb, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, PADDING)
    return rb


# ============================================================
# Frame interno (el usuario no lo usa directamente)
# ============================================================

class _MainFrame(wx.Frame):
    """Ventana que construye el layout a partir de una lista de elementos."""

    def __init__(self, title, size, elements):
        super().__init__(None, title=title, size=size)

        self._result_status = "close"  # default si se cierra con X
        self._widgets = {}  # {name: (kind, widget)}
        self._form_results = {} # Almacén persistente de los datos extraídos

        # --- ScrolledWindow ---
        scroll = wx.ScrolledWindow(self)
        scroll.SetScrollRate(0, 10)

        outer_sizer = wx.BoxSizer(wx.VERTICAL)

        # Panel interno con ancho máximo
        inner_panel = wx.Panel(scroll)
        inner_panel.SetMaxSize(wx.Size(MAX_CONTAINER_WIDTH, -1))
        inner_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Crear cada elemento registrado ---
        for kind, name, data in elements:
            widget = None
            if kind == "title":
                widget = _add_titulo(inner_panel, inner_sizer, data)
            elif kind == "label":
                widget = _add_label(inner_panel, inner_sizer, data)
            elif kind == "listbox":
                widget = _add_listbox(inner_panel, inner_sizer, data, multiple=False)
            elif kind == "listbox_multiple":
                widget = _add_listbox(inner_panel, inner_sizer, data, multiple=True)
            elif kind == "choice":
                widget = _add_choice(inner_panel, inner_sizer, data)
            elif kind == "buttons":
                buttons = _add_botones(inner_panel, inner_sizer, data)
                self._bind_buttons(buttons)
            elif kind == "checkbox":
                widget = _add_checkbox(inner_panel, inner_sizer, data)
            elif kind == "radiobox":
                widget = _add_radiobox(inner_panel, inner_sizer, data)

            # Almacenar referencia al widget (solo si tiene name y no es tipo texto)
            if name and kind not in _TEXT_TYPES and kind != "buttons":
                self._widgets[name] = (kind, widget)

        inner_panel.SetSizer(inner_sizer)

        # Centrar el panel interno
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.AddStretchSpacer(1)
        h_sizer.Add(inner_panel, 0, wx.EXPAND)
        h_sizer.AddStretchSpacer(1)

        outer_sizer.Add(h_sizer, 0, wx.EXPAND)
        scroll.SetSizer(outer_sizer)

        # Referencias para resize
        self._scroll = scroll
        self._inner_panel = inner_panel

        self.Bind(wx.EVT_SIZE, self._on_resize)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Centre()
        wx.CallAfter(self._update_layout)

    def _bind_buttons(self, buttons):
        """Bindea los botones Aceptar/Cancelar al cierre con status."""
        for label, btn in buttons.items():
            if label.lower() == "aceptar":
                btn.Bind(wx.EVT_BUTTON, self._on_accept)
            elif label.lower() == "cancelar":
                btn.Bind(wx.EVT_BUTTON, self._on_cancel)

    def _collect_data(self):
        """Extrae los datos de los widgets y los guarda en self._form_results."""
        self._form_results = {}
        for name, (kind, widget) in self._widgets.items():
            extractor = _VALUE_EXTRACTORS.get(kind)
            if extractor:
                self._form_results[name] = extractor(widget)

    def _on_accept(self, evt):
        self._result_status = "ok"
        self._collect_data()  # << IMPORTANTE: Extraer ANTES de que se destruyan los widgets
        self.Close()

    def _on_cancel(self, evt):
        self._result_status = "cancel"
        self.Close()

    def _on_close(self, evt):
        self.Destroy()

    def _on_resize(self, evt):
        evt.Skip()
        self._update_layout()

    def _update_layout(self):
        scroll = self._scroll
        inner_panel = self._inner_panel

        scroll_width = scroll.GetClientSize().width
        actual_width = min(scroll_width, MAX_CONTAINER_WIDTH)
        inner_panel.SetMinSize(wx.Size(actual_width, -1))
        inner_panel.SetMaxSize(wx.Size(actual_width, -1))

        for child in inner_panel.GetChildren():
            if isinstance(child, wx.StaticText) and hasattr(child, '_original_label'):
                child.SetLabel(child._original_label)
                child.Wrap(actual_width - PADDING * 2)

        scroll.Layout()
        scroll.FitInside()

    def get_result(self):
        """Retorna el dict de resultado usando los datos ya recolectados."""
        return {
            "status": self._result_status,
            "form_elements": self._form_results if self._result_status == "ok" else {}
        }


# ============================================================
# Clase pública — API builder
# ============================================================

class WindowsApp:
    """
    Builder para crear ventanas wxPython de forma declarativa.

    Uso:
        window = WindowsApp("Mi Formulario", size=(800, 600))
        window.addTitle("Título")
        window.addLabel("Texto descriptivo")
        window.addListbox("campo1", ["A", "B", "C"])
        result = window.show()
        print(result)
    """

    def __init__(self, title="Ventana", size=(800, 600)):
        self._title = title
        self._size = size
        self._elements = []  # [(kind, name, data)]

    # -- Métodos para elementos de texto (sin name, no devuelven valor) --

    def addTitle(self, text):
        """Agrega un título centrado con fuente grande."""
        self._elements.append(("title", None, text))

    def addLabel(self, text):
        """Agrega una etiqueta de texto alineada a la izquierda."""
        self._elements.append(("label", None, text))

    # -- Métodos para elementos de entrada (requieren name) --

    def addListbox(self, name, choices):
        """Agrega un ListBox de selección simple."""
        self._elements.append(("listbox", name, list(choices)))

    def addListboxMultiple(self, name, choices):
        """Agrega un ListBox de selección múltiple."""
        self._elements.append(("listbox_multiple", name, list(choices)))

    def addChoice(self, name, choices):
        """Agrega un dropdown/choice."""
        self._elements.append(("choice", name, list(choices)))

    def addCheckbox(self, name, options):
        """Agrega un grupo de checkboxes (selección múltiple independiente)."""
        self._elements.append(("checkbox", name, list(options)))

    def addRadiobox(self, name, options):
        """Agrega un grupo de radio buttons (selección única)."""
        self._elements.append(("radiobox", name, list(options)))

    # -- Botones (sin name, controlan el status) --

    def addButtons(self, labels):
        """Agrega una fila de botones centrados."""
        self._elements.append(("buttons", None, list(labels)))

    # -- Mostrar ventana y retornar resultado --

    def show(self):
        """Crea la aplicación, construye la ventana, ejecuta el loop y retorna el resultado."""
        app = wx.App()
        frame = _MainFrame(self._title, self._size, self._elements)
        frame.Show()
        app.MainLoop()
        return frame.get_result()


# ============================================================
# Punto de entrada — ejemplo de uso
# ============================================================

if __name__ == "__main__":
    import json

    window = WindowsApp("Form Test 2", size=(800, 600))

    window.addTitle(
        "Este es un título de ejemplo centrado que puede ser largo y hacer wrap"
    )

    window.addLabel(
        "Esta es una etiqueta alineada a la izquierda. Puede contener texto "
        "largo que hará wrap automáticamente cuando supere el ancho del contenedor."
    )

    window.addListbox("listbox_simple", [
        "Opción A", "Opción B", "Opción C", "Opción D",
        "Esta es una opción con texto largo que puede necesitar scroll."
    ])

    window.addLabel("Seleccione múltiples elementos de la lista:")

    window.addListboxMultiple("listbox_multi", [
        "Elemento 1", "Elemento 2", "Elemento 3",
        "Elemento 4", "Elemento 5"
    ])

    window.addLabel("Elija una opción del desplegable:")

    window.addChoice("choice_color", [
        "Primera", "Segunda", "Tercera",
        "Esta es una opción con texto largo."
    ])

    window.addLabel("Marque las opciones que apliquen:")

    window.addCheckbox("checkbox_opts", [
        "Opcion 1", "Opcion 2", "Opcion 3", "Opcion 4", "Opcion 500.000.000"
    ])

    window.addRadiobox("radio_opts", [
        "Opcion 1", "Opcion 2", "Opcion 3", "Opcion 4", "Opcion 500.000.000"
    ])

    window.addButtons(["Aceptar", "Cancelar"])

    result = window.show()
    print(json.dumps(result, ensure_ascii=False, indent=2))