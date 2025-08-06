class Obra:
    # Representa una obra de arte.
    
    def __init__(self, object_id, titulo, artista, nacionalidad):
        self.id = object_id
        self.titulo = titulo
        self.artista = artista
        self.nacionalidad = nacionalidad

    
    def from_json(data):
        return Obra(
            data.get('objectID', 'N/A'),
            data.get('title', 'Sin título'),
            data.get('artistDisplayName', 'Desconocido')
        )
    

