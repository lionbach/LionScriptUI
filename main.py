from form_manager import WindowsApp
import json

if __name__ == "__main__":
    import sys
    import argparse
    
    """
    Ejemplo de JSON para probar:
    {
        "window_title": "Formulario de Prueba",
        "form_elements": {
            "name1": {
                "type": "title",
                "data": "Título Principal"
            },
            "name2": {
                "type": "subtitle",
                "data": "Subtítulo del formulario"
            },
            "name3": {
                "type": "text",
                "data": "Este es un texto informativo del formulario."
            },
            "name4": {
                "type": "checklistbox",
                "data": ["rojo", "amarillo", "azul"]
            },
            "name5": {
                "type": "checklistbox_multi",
                "data": ["rojo", "amarillo", "azul"]
            },
            "name6": {
                "type": "choice",
                "data": ["rojo", "amarillo", "azul"]
            }
        }
    }

    en powershel ejemplo
    python main.py --% "{\"window_title\":\"titulo\",\"form_elements\":{\"name1\":{\"type\":\"title\",\"data\":\"mensaje del titulo\"},\"name2\":{\"type\":\"subtitle\",\"data\":\"mensaje del subtitulo\"},\"label2\":{\"type\":\"label\",\"data\":\"label X:\"},\"name4\":{\"type\":\"listbox\",\"data\":[\"rojo\",\"amarillo\",\"azul\"]},\"label3\":{\"type\":\"label\",\"data\":\"label X:\"},\"name5\":{\"type\":\"listbox_multiple\",\"data\":[\"rojo\",\"amarillo\",\"azul\"]},\"label4\":{\"type\":\"label\",\"data\":\"label X:\"},\"name6\":{\"type\":\"checkbox\",\"data\":[\"rojo\",\"amarillo\",\"azul\"]},\"label5\":{\"type\":\"label\",\"data\":\"label X:\"},\"name7\":{\"type\":\"radiobox\",\"data\":[\"rojo\",\"amarillo\",\"azul\"]},\"label6\":{\"type\":\"label\",\"data\":\"label X:\"},\"name8\":{\"type\":\"choice\",\"data\":[\"rojo\",\"amarillo\",\"azul\"]},\"name9\":{\"type\":\"buttons\"}}}"

    """
    
    parser = argparse.ArgumentParser(description='Mostrar formulario dinámico')
    parser.add_argument('json_data', nargs='?', help='Datos JSON del formulario')
    parser.add_argument('--file', '-f', help='Archivo JSON con los datos del formulario')
    
    args = parser.parse_args()
    
    # Obtener datos JSON
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            form_data = json.load(f)
    elif args.json_data:
        form_data = json.loads(args.json_data)
    else:
        print("Error: Se debe proporcionar datos JSON o un archivo JSON")
        sys.exit(1)
    
    # ---------- Procesar elementos ----------    
    window = WindowsApp("Form Test 2", size=(800, 600))
    form_elements = form_data.get("form_elements", {})
    for name, element in form_elements.items():
        element_type = element.get("type")
        element_data = element.get("data")
        if element_type == "title":
            window.addTitle(element_data)
        elif element_type == "label":
            window.addLabel(element_data)
        elif element_type == "listbox":
            window.addListbox(name, element_data)
        elif element_type == "listbox_multiple":
            window.addListboxMultiple(name, element_data)
        elif element_type == "choice":
            window.addChoice(name, element_data)
        elif element_type == "checkbox":
            window.addCheckbox(name, element_data)
        elif element_type == "radiobox":
            window.addRadiobox(name, element_data)
        elif element_type == "buttons":
            window.addButtons(["Aceptar", "Cancelar"])

    result = window.show()
    print(json.dumps(result, ensure_ascii=False, indent=2))
