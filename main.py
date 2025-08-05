import os
import requests
import json

from departamento import *
from obra import *

class MetroArtApp:

    # Aplicación para explorar obras del Museo Metropolitano de Nueva York (Met).

    API_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

    def _limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _mostrar_menu(self, title, options):
        self._limpiar_pantalla()
        print("=" * 35)
        print(f"   {title}   ")
        print("=" * 35)
        for key, value in options.items():
            print(f"{key}. {value}")
        print("=" * 35)
        return input("Seleccione una opción: ")

    def _obtener_datos_api(self, endpoint, params=None):

        # Realiza una solicitud GET a la API del Met.

        url = f"{self.API_URL}/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API ({endpoint}): {e}")
            return {}
        except json.JSONDecodeError:
            print(f"Error al decodificar la respuesta JSON de {endpoint}.")
            return {}

    def obtener_departamentos(self):

        #Obtiene la lista de departamentos disponibles desde la API.

        data = self._obtener_datos_api("departments")
        departamentos_json = data.get("departments", [])
        return [Departamento.from_json(dep) for dep in departamentos_json]

    def obtener_obras_por_departamento(self, departamento_id):

         # Busca obras asociadas a un departamento específico.
         
        params = {"departmentId": departamento_id, "q": "art"}
        search_results = self._obtener_datos_api("search", params=params)

        object_ids = search_results.get("objectIDs", []) or []
        obras = []

        for obj_id in object_ids[:10]:
            obj_data = self._obtener_datos_api(f"objects/{obj_id}")
            if obj_data:
                obras.append(Obra.from_json(obj_data))

        return obras, search_results.get("total", 0)

    def buscar_obras_por_departamento(self):
        self._limpiar_pantalla()
        print("=" * 47)
        print("   MetroArt - Búsqueda por Departamento de Obra   ")
        print("=" * 47)

        departamentos = self.obtener_departamentos()

        if not departamentos:
            print("No se pudieron cargar los departamentos.")
            input("Presione Enter para continuar...")
            return

        for idx, dep in enumerate(departamentos):
            print(f"{idx + 1}. {dep.nombre} (ID: {dep.id})")

        while True:
            try:
                opcion = input("\nSeleccione el número del departamento o '0' para volver: ")
                if opcion == '0':
                    return
                indice = int(opcion) - 1
                if 0 <= indice < len(departamentos):
                    departamento = departamentos[indice]
                    break
                else:
                    print("Número fuera de rango.")
            except ValueError:
                print("Entrada inválida. Intente de nuevo.")

        print(f"\nBuscando obras en el departamento: {departamento.nombre}...\n")
        obras, total = self.obtener_obras_por_departamento(departamento.id)

        if not obras:
            print("No se encontraron obras.")
        else:
            print(f"Se encontraron {len(obras)} de {total} obras (mostrando hasta 10):\n")
            for obra in obras:
                print(f"ID Obra: {obra.id}")
                print(f"Título: {obra.titulo}")
                print(f"Autor: {obra.artista}")
                print("---")
            if total > len(obras):
                print(f"... Se omitieron {total - len(obras)} obras restantes.")

        input("\nPresione Enter para continuar...")

    def run(self):
        while True:
            main_options = {
                '1': "Búsqueda de obras",
                '2': "Mostrar detalles de una obra",
                '0': "Salir"
            }
            opcion = self._mostrar_menu("MetroArt - Menú Principal", main_options)

            if opcion == '1':
                while True:
                    search_options = {
                        '1': "Ver lista de obras por Departamento",
                        '2': "Ver lista de obras por Nacionalidad del autor",
                        '3': "Ver lista de obras por nombre del autor",
                        '0': "Volver al menú principal"
                    }
                    buscar_opcion = self._mostrar_menu("MetroArt - Búsqueda de Obras", search_options)

                    if buscar_opcion == '1':
                        self.buscar_obras_por_departamento()
                    elif buscar_opcion in ['2', '3']:
                        self._limpiar_pantalla()
                        print("=" * 35)
                        print("         FALTA DESARROLLAR         ")
                        print("=" * 35)
                        input("Presione Enter para continuar...")
                    elif buscar_opcion == '0':
                        break
                    else:
                        print("Opción no válida. Intente de nuevo.")
                        input("Presione Enter para continuar...")
            elif opcion == '2':
                self._limpiar_pantalla()
                print("=" * 39)
                print("     MetroArt - Detalles de Obra     ")
                print("=" * 39)
                print("FALTA DESARROLLAR")
                input("Presione Enter para continuar...")
            elif opcion == '0':
                self._limpiar_pantalla()
                print("Saliendo del sistema MetroArt. ¡Hasta luego!")
                break
            else:
                print("Opción no válida. Intente de nuevo.")
                input("Presione Enter para continuar...")

if __name__ == "__main__":
    app = MetroArtApp()
    app.run()