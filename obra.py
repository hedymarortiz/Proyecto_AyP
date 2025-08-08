class Obra:
    """ Representa una obra de arte."""

    def __init__(self, object_id, titulo, artista, nacionalidad):
        self.id = object_id
        self.titulo = titulo
        self.artista = artista
        self.nacionalidad = nacionalidad

    @staticmethod
    def from_json(data):
        return Obra(
            data.get('objectID', 'N/A'),
            data.get('title', 'Sin título'),
            data.get('artistDisplayName', 'Desconocido'),
            data.get('artistNationality', 'Desconocida')
        )


class DetalleObra:
    """Representa los detalles completos de una obra del museo."""

    def __init__(self, object_id, titulo, artista, nacionalidad,
                 nacimiento, muerte, clasificacion, anio_creacion, url_imagen):
        self.id = object_id
        self.titulo = titulo
        self.artista = artista
        self.nacionalidad = nacionalidad
        self.nacimiento = nacimiento
        self.muerte = muerte
        self.clasificacion = clasificacion
        self.anio_creacion = anio_creacion
        self.url_imagen = url_imagen

    @staticmethod
    def from_json(data):
        """Crea un DetalleObra a partir del JSON de la API."""
        def get(d, k, default="N/D"):
            v = d.get(k)
            return v if (v is not None and str(v).strip() != "") else default

        url_img = get(data, "primaryImage", "")
        if not url_img:
            url_img = get(data, "primaryImageSmall", "")

        return DetalleObra(
            get(data, "objectID", "N/A"),
            get(data, "title", "Sin título"),
            get(data, "artistDisplayName", "Desconocido"),
            get(data, "artistNationality", "Desconocida"),
            get(data, "artistBeginDate", "N/D"),
            get(data, "artistEndDate", "N/D"),
            get(data, "classification", "N/D"),
            get(data, "objectDate", "N/D"),
            url_img
        )

