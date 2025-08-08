import os
import requests
import json

from departamento import *
from obra import *
from nacionalidad import Nacionalidades

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
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            # No mostrar mensajes de error individuales para mantener la salida limpia
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
        errores_api = 0
        for obj_id in object_ids[:20]:  # Limita a 20 resultados
            try:
                obj_data = self._obtener_datos_api(f"objects/{obj_id}")
                if not obj_data:
                    errores_api += 1
                    continue
                obras.append(Obra.from_json(obj_data))
            except Exception:
                errores_api += 1
                continue
        if errores_api > 0:
            print(f"(Se omitieron {errores_api} obras por problemas de conexión con la API)")
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
            input("Presione Enter para continuar...")
            return
        print(f"Se encontraron {len(obras)} de {total} obras:\n")
        pagina = 0
        while True:
            self._limpiar_pantalla()
            print(f"Obras del departamento {departamento.nombre} (página {pagina+1}/{(len(obras)-1)//10+1})\n")
            for obra in obras[pagina*10:(pagina+1)*10]:
                print(f"ID Obra: {obra.id}")
                print(f"Título: {obra.titulo}")
                print(f"Autor: {obra.artista}")
                print("---")
            print("N: Siguiente página | P: Página anterior | 0: Salir")
            opcion = input("Opción: ").strip().lower()
            if opcion == 'n' and (pagina+1)*10 < len(obras):
                pagina += 1
            elif opcion == 'p' and pagina > 0:
                pagina -= 1
            elif opcion == '0':
                break
            else:
                print("Opción inválida.")
                input("Presione Enter para continuar...")

     #BUSQUEDA POR NACIONALIDADES     
    def obtener_nacionalidades_disponibles(self, obras):
        nacionalidades = set()
        for obra in obras:
            if hasattr(obra, 'nacionalidad') and obra.nacionalidad:
                nacionalidad = obra.nacionalidad.strip().title()
                if nacionalidad:
                    nacionalidades.add(nacionalidad)
        return sorted(nacionalidades)
    

    def obtener_obras_por_nacionalidad(self, nacionalidad):
        search_results = self._obtener_datos_api("search", params={"q": "art"})
        object_ids = search_results.get("objectIDs", []) or []
        obras = []
        errores_api = 0
        for obj_id in object_ids[:20]:  # Limita a 20 resultados
            try:
                obj_data = self._obtener_datos_api(f"objects/{obj_id}")
                if not obj_data:
                    errores_api += 1
                    continue
                if obj_data.get('artistNationality'):
                    obra = Obra.from_json(obj_data)
                    if obra.nacionalidad and nacionalidad.lower() in obra.nacionalidad.lower():
                        obras.append(obra)
            except Exception:
                errores_api += 1
                continue
        if errores_api > 0:
            print(f"(Se omitieron {errores_api} obras por problemas de conexión con la API)")
        return obras
    
    def obtener_obras_por_nacionalidad(self, nacionalidad):
        search_results = self._obtener_datos_api("search", params={"q": "art", "isHighlight": True})
        object_ids = search_results.get("objectIDs", []) or []
        obras = []
        errores_api = 0
        
        for obj_id in object_ids[:30]:  # Aumentamos a 30 para más resultados
            try:
                obj_data = self._obtener_datos_api(f"objects/{obj_id}")
                if not obj_data:
                    errores_api += 1
                    continue
                    
                if obj_data.get('artistNationality'):
                    obra = Obra.from_json(obj_data)
                    if obra.nacionalidad and nacionalidad.lower() in obra.nacionalidad.lower():
                        obras.append(obra)
            except Exception as e:
                errores_api += 1
                continue
                
        if errores_api > 0:
            print(f"(Se omitieron {errores_api} obras por problemas de conexión con la API)")
        return obras

    def buscar_obras_por_nacionalidad(self):
        
        self._limpiar_pantalla()
        print("=" * 55)
        print("   MetroArt - Búsqueda por Nacionalidad del Autor   ")
        print("=" * 55)
        
        items_por_pagina = 15
        pagina_actual = 0
        total_paginas = (len(Nacionalidades) + items_por_pagina - 1) // items_por_pagina
        
        while True:
            inicio = pagina_actual * items_por_pagina
            fin = inicio + items_por_pagina
            nacionalidades_pagina = Nacionalidades[inicio:fin]
            
            print(f"\nNacionalidades disponibles (Página {pagina_actual + 1}/{total_paginas}):\n")
            for idx, nacionalidad in enumerate(nacionalidades_pagina, start=1):
                print(f"{idx:2d}. {nacionalidad}")
            
            print("\nOpciones:")
            print(" [1-15] Seleccionar nacionalidad")
            print(" N - Página siguiente")
            print(" P - Página anterior")
            print(" B - Buscar por texto")
            print(" 0 - Volver al menú")
            
            opcion = input("\nSeleccione una opción: ").strip().lower()
            
            if opcion == '0':
                return
            elif opcion == 'n' and pagina_actual < total_paginas - 1:
                pagina_actual += 1
                self._limpiar_pantalla()
                continue
            elif opcion == 'p' and pagina_actual > 0:
                pagina_actual -= 1
                self._limpiar_pantalla()
                continue
            elif opcion == 'b':
                nacionalidad_buscar = input("Ingrese la nacionalidad a buscar: ").strip()
                if nacionalidad_buscar:
                    self._mostrar_resultados_nacionalidad(nacionalidad_buscar)
                continue
            else:
                try:
                    seleccion = int(opcion) - 1
                    if 0 <= seleccion < len(nacionalidades_pagina):
                        self._mostrar_resultados_nacionalidad(nacionalidades_pagina[seleccion])
                    else:
                        print("¡Número fuera de rango!")
                        input("Presione Enter para continuar...")
                except ValueError:
                    print("¡Opción no válida!")
                    input("Presione Enter para continuar...")
            
            self._limpiar_pantalla()

    def _mostrar_resultados_nacionalidad(self, nacionalidad):
        """Método nuevo que conserva tu sistema de paginación de resultados"""
        print(f"\nBuscando obras de artistas {nacionalidad}...")
        obras = self.obtener_obras_por_nacionalidad(nacionalidad)
        
        if not obras:
            print(f"\nNo se encontraron obras de artistas {nacionalidad}.")
            input("Presione Enter para continuar...")
            return
        
        pagina = 0
        total_paginas = (len(obras) + 4) // 5  # 5 obras por página
        
        while True:
            self._limpiar_pantalla()
            print("=" * 55)
            print(f"Obras de artistas {nacionalidad} (Página {pagina+1}/{total_paginas})")
            print("=" * 55)
            
            for obra in obras[pagina*5 : (pagina+1)*5]:
                print(f"\nID Obra: {obra.id}")
                print(f"Título: {obra.titulo}")
                print(f"Autor: {obra.artista}")
                print(f"Nacionalidad: {obra.nacionalidad}")
                print("-" * 30)
            
            print("\nOpciones:")
            print(" N - Página siguiente" if (pagina+1)*5 < len(obras) else "")
            print(" P - Página anterior" if pagina > 0 else "")
            print(" 0 - Volver al listado de nacionalidades")
            
            opcion = input("\nSelección: ").strip().lower()
            
            if opcion == 'n' and (pagina+1)*5 < len(obras):
                pagina += 1
            elif opcion == 'p' and pagina > 0:
                pagina -= 1
            elif opcion == '0':
                break
            else:
                print("Opción no válida")
                input("Presione Enter para continuar...")
    
    #Busca obras por autor
    def buscar_obras_por_autor(self):
        self._limpiar_pantalla()
        print("=" * 55)
        print("   MetroArt - Búsqueda por Nombre del Autor   ")
        print("=" * 55)
        nombre_autor = input("Ingrese el nombre del autor a buscar: ").strip()
        if not nombre_autor:
            print("Debe ingresar un nombre de autor.")
            input("Presione Enter para continuar...")
            return
        print(f"\nBuscando obras de {nombre_autor}...\n")
        obras = self.obtener_obras_por_autor(nombre_autor)
        if not obras:
            print(f"No se encontraron obras de {nombre_autor}.")
            input("Presione Enter para continuar...")
            return
        print(f"Se encontraron {len(obras)} obras:\n")
        pagina = 0
        while True:
            self._limpiar_pantalla()
            print(f"Obras de {nombre_autor} (página {pagina+1}/{(len(obras)-1)//10+1})\n")
            for obra in obras[pagina*10:(pagina+1)*10]:
                print(f"ID Obra: {obra.id}")
                print(f"Título: {obra.titulo}")
                print(f"Autor: {obra.artista}")
                print("---")
            print("N: Siguiente página | P: Página anterior | 0: Salir")
            opcion = input("Opción: ").strip().lower()
            if opcion == 'n' and (pagina+1)*10 < len(obras):
                pagina += 1
            elif opcion == 'p' and pagina > 0:
                pagina -= 1
            elif opcion == '0':
                break
            else:
                print("Opción inválida.")
                input("Presione Enter para continuar...")
    
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
                    elif buscar_opcion == '2':
                        self.buscar_obras_por_nacionalidad()
                    elif buscar_opcion == '3':
                        self.buscar_obras_por_autor()
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


# Bloque principal para ejecutar la app
if __name__ == "__main__":
    app = MetroArtApp()
    app.run()

