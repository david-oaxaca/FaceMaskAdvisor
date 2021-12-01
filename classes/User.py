class User:
    def __init__(self, id, institucion, email, nombre, password, giro) -> None:
        self.id = id
        self.institucion = institucion
        self.email = email
        self.nombre = nombre
        self.password = password
        self.giro = giro

    def __repr__(self) -> str:
        return f'<User: {self.nombre}>'
