#!/bin/bash

# Detect OS to select jq executable
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    JQ="../extras/jq-win.exe"
else
    JQ="../extras/jq-linux"
    chmod +x "$JQ" 2>/dev/null
fi


# Estructura para cargar lista de aplicaciones
# "id|nombre|tipo_de_instalacion|parametros_de_instalacion"
#
# nombre: Nombre que se vera en la seleccion de las aplicaciones
#
# tipo de instalacion: apt, flatpak, deb o custom.
#   Si es custom el tipo de instalacion, se debera crear una funcion que ejecute la instalacion.
#
# parametros de instalacion: nombre de los paquetes apt o flatpak a instalar, url para descargar el .deb o nombre de la funcion custom.

APPS_DATA=(
"antigravity|Antigravity|deb|"
"audacity|Audacity|apt|audacity"
"bitwarden|Bitwarden||"
"btop|btop||"
"cmatrix|cmatrix|apt|cmatrix"
"dbeaver|DBeaver|deb|"
"discord|Discord|flatpak|"
"docker|Docker|custom|install_docker"
"fastfetch|fastfetch|apt|fastfetch"
"free_download_manager|Free download manager|deb|"
"gimp|GIMP|apt|gimp"
"git|Git|custom|install_git"
"google_chrome|Google Chrome|deb|google-chrome-stable"
"google_cloud_cli|Google cloud cli|custom|google-cloud-sdk"
"google_cloud_sql_proxy|Google cloud sql proxy|custom|google-cloud-sdk-sql-proxy"
"handbrake|HandBrake||handbrake"
"htop|htop|apt|htop"
"inkscape|Inkscape|apt|inkscape"
"jq|jq|apt|jq"
"kolourpaint|kolourpaint|apt|kolourpaint breeze-icon-theme"
"mysql|MySQL|custom|install_mysql"
"obs_studio|OBS Studio|deb|obs-studio"
"onlyoffice|OnlyOffice|deb|onlyoffice-desktopeditors"
"openforticlient|Openforticlient|apt|openforticlient"
"postgresql|PostgreSQL|apt|postgresql"
"postman|Postman|custom|install_postman"
"shotcut|Shotcut|apt|shotcut"
"slack|Slack||slack"
"virt_manager|Virt-manager|apt|virt-manager"
"virtualbox|VirtualBox|apt|virtualbox"
"visual_studio_code|Visual Studio Code|deb|https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"
"vlc_media_player|VLC media player|apt|vlc"
"zoom|Zoom|deb|"
)

arr_apps_list=""

for app in "${APPS_DATA[@]}"; do
  IFS='|' read -r id name type args <<< "$app"
  if [[ -z "$arr_apps_list" ]]; then
    arr_apps_list="\"$name\""
  else
    arr_apps_list+=", \"$name\""
  fi
done

# --- Configuración json del Formulario ---
JSON_INPUT=$(cat <<EOF
{
    "window_title": "Instalador de aplicaciones",
    "form_elements": {
        "header": {
            "type": "title",
            "data": "Instalador de aplicaciones"
        },
        "info": {
            "type": "label",
            "data": "Seleccione los programas que desea instalar:"
        },
        "programs_to_install": {
            "type": "checkbox",
            "data": [$arr_apps_list]
        },
        "actions": {
            "type": "buttons",
            "data": ["Aceptar", "Cancelar"]
        }
    }
}
EOF
)

# Validamos el json y salimos si da error
"$JQ" -e . <<< "$JSON_INPUT" > /dev/null || exit 1

RESULT=$(python main.py "$JSON_INPUT")

if [ $? -ne 0 ]; then
    echo "Error ejecutando el formulario."
    exit 1
fi

STATUS=$(echo "$RESULT" | "$JQ" -r '.status // "error"')

if [ "$STATUS" == "ok" ]; then

   # Extraemos la lista limpiando los retornos de carro (\r) de Windows
    mapfile -t SELECTED_APPS_ARRAY < <(
    echo "$RESULT" | "$JQ" -r '.form_elements.programs_to_install[]' | tr -d '\r'
    )

    for selected_name in "${SELECTED_APPS_ARRAY[@]}"; do
        for app in "${APPS_DATA[@]}"; do
            IFS='|' read -r id nombre instalacion argumentos <<< "$app"
            if [[ "$nombre" == "$selected_name" ]]; then
                echo "id:$id - nombre:$nombre - instalacion:$instalacion - argumentos:$argumentos"
                break
            fi
        done
    done

    echo -e "Proceso completado con éxito."
else
    echo -e "\nAcción cancelada o ventana cerrada (Status: $STATUS)."
fi
