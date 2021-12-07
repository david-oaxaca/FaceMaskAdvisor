class User:
    def __init__(self, id, institucion, email, nombre, apellido_pat, apellido_mat, password, giro) -> None:
        self.id = id
        self.institucion = institucion
        self.email = email
        self.nombre = nombre
        self.apellido_pat = apellido_pat
        self.apellido_mat = apellido_mat
        self.password = password
        self.giro = giro

    def __repr__(self) -> str:
        return f'<User: {self.nombre}>'
