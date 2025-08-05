class Departamento:
    def __init__(self, department_id, display_name):
        self.id = department_id
        self.nombre = display_name

    
    def from_json(data):
        return Departamento(data["departmentId"], data["displayName"])