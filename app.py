from flask import Flask, render_template, request, redirect, url_for, flash;
from flask_mysqldb import MySQL

app = Flask(__name__)

# Conexion a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'face_mask_advisor'
mysql = MySQL(app)

# Inicialización de la sesión
app.secret_key = 'mysecretkey'

# Routing
@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/registro')
def Registro():
    return render_template('Registro.html')

@app.route('/inicio')
def Inicio():
    return render_template('MenuInicio.html')

@app.route('/charts')
def Charts():
    return render_template('MenuEstadisticas.html')

@app.route('/test')
def Test():
    return render_template('MenuRealizarPrueba.html')

@app.route('/user_account')
def User_account():
    return render_template('MenuCuenta.html')

@app.route('/help')
def Account():
    return render_template('MenuAyuda.html')

@app.route('/advices')
def Advices():
    return render_template('MenuAvisosRecientes.html')

@app.route('/add_advice')
def Add_advice():
    return render_template('AnadirAviso.html')

@app.route('/logout')
def Logout():
    return 'Cerrar sesion'

# Session and Queries methods
@app.route('/login', methods=['POST'])
def Login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT correo_admin, pass_admin FROM institucion WHERE correo_admin = %s', [email])
        data = cur.fetchall()
        #print(data)
        if data[0][1] == password:
            flash('Registro exitoso')
            return redirect(url_for('Inicio'))
        
    flash('Registro fallido')
    return redirect(url_for('Index'))



@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        institucion = request.form['institucion']
        email = request.form['email']
        nombre = request.form['nombre']
        password = request.form['password']
        giro = request.form['giro']

        cur = mysql.connection.cursor()
        cur.execute('''
        INSERT INTO institucion
        (nombre_institucion, correo_admin, nombre_admin, pass_admin, giro_institucion)
        VALUES (%s, %s, %s, %s, %s)
        ''', 
        (institucion, email, nombre, password, giro))

        mysql.connection.commit()

        flash('Cuenta dada de alta exitosamente')
    return redirect(url_for('Inicio'))


@app.route('/edit_user/<id>')
def get_user(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM institucion WHERE id = %s', (id))
    data = mysql.fetchall()

@app.route('/update_user/<id>', methods=['POST'])
def update_user(id):
    if request.method == 'POST':
        institucion = request.form['institucion']
        email = request.form['email']
        nombre = request.form['nombre']
        password = request.form['password']
        giro = request.form['giro']
        cur = mysql.connection.cursor()
        cur.execute('''
        UPDATE institucion 
        SET nombre_institucion = %s,
            correo_admin = %s,
            nombre_admin = %s,
            pass_admin = %s,
            giro_institucion = %s
        WHERE id_institucion = %s
        ''', (institucion, email, nombre, password, giro, id))
        mysql.connection.commit()
        flash('Datos actualizados exitosamente')

    return redirect(url_for('Index'))


@app.route('/consulta', methods=['POST'])
def read_data():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM institucion WHERE correo_admin = %s', email)
        data = cur.fetchall()
        print(data)
    return render_template('MenuCuenta.html', contacts = data )

@app.route('/delete/<string:id>')
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM institucion WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Cuenta eliminada :(')
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(port = 3000, debug = True)