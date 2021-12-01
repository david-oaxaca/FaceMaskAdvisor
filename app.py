# Imports
from flask import (
    Flask, 
    g,
    abort,
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    session
 )
from flask_mysqldb import MySQL
from classes.User import User

app = Flask(__name__)

# Conexion a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'face_mask_advisor'
mysql = MySQL(app)

# Inicialización de la sesión
app.secret_key = 'FaceMaskAdvisor_mysecretkey'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        id_usuario = int(session['user_id'])
        user_data = get_user(id_usuario)
        user = User(user_data[0][0], user_data[0][1], user_data[0][2], user_data[0][3], user_data[0][4], user_data[0][5])
        g.user = user

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Routing
@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/registro')
def Registro():
    return render_template('Registro.html')

@app.route('/inicio')
def Inicio():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('MenuInicio.html')

@app.route('/charts')
def Charts():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('MenuEstadisticas.html')

@app.route('/test')
def Test():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('MenuRealizarPrueba.html')

@app.route('/user_account')
def User_account():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('MenuCuenta.html')

@app.route('/help')
def Account():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('MenuAyuda.html')

@app.route('/advices')
def Advices():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('MenuAvisosRecientes.html')

@app.route('/add_advice')
def Add_advice():
    if not g.user:
        return redirect(url_for('Index'))
    else:
        return render_template('AnadirAviso.html')

# Session and Queries methods
@app.route('/login', methods=['POST'])
def Login():
        try:
            if request.method == 'POST':
                session.pop('user_id', None)
                email = request.form['email']
                password = request.form['password']
                cur = mysql.connection.cursor()
                cur.execute('SELECT id_institucion, correo_admin, pass_admin FROM institucion WHERE correo_admin = %s', [email])
                data = cur.fetchall()
                
                if data[0][2] == password:
                    session['user_id'] = data[0][0]
                    flash('Registro exitoso', 'alert-success ')
                    return redirect(url_for('Inicio'))
                else:
                    flash('Registro fallido', 'alert-danger')
                    return redirect(url_for('Index'))    
        except Exception:
            print(Exception)
            flash('Registro fallido', 'alert-danger')
            return redirect(url_for('Index'))
            

@app.route('/logout')
def Logout():
    session.pop('user_id', None)
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

        flash('Cuenta dada de alta exitosamente', 'alert-primary')
    return redirect(url_for('Inicio'))

def get_user(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM institucion WHERE id_institucion = %s', (id,))
    data = cur.fetchall()
    return data


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