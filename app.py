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
    session,
    jsonify
 )
from flask_mail import Mail, Message
from flask.json import dump
from flask_mysqldb import MySQL
from classes.User import User
from flask_cors import CORS

import torch
from torch import nn
from torchvision.models import googlenet
import numpy as np
from torchvision.transforms import Compose, Resize, CenterCrop, ToPILImage, ToTensor, Grayscale

import time
import datetime
from PIL import Image
import base64
import io
import secrets

import hashlib

count = 0

model = nn.Sequential(
    googlenet(pretrained=True),
    nn.Linear(1000, 1),
    nn.Sigmoid()
)
model.load_state_dict(torch.load('./model_new.pth'))
model.eval()

app = Flask(__name__)

CORS(app)

# Parametros para el envio de correo
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Conexion a la base de datos
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'face_mask_advisor'
mysql = MySQL(app)

# Inicialización de la sesión
app.secret_key = 'FaceMaskAdvisor_mysecretkey'
id_inst = -1

@app.before_request
def before_request():
    g.user = None
    global id_inst

    if 'user_id' in session:
        id_usuario = int(session['user_id'])
        id_inst = id_usuario
        data_count = count_users()
        if data_count[0][0] > 0:
            user_data = get_user(id_usuario)
            user = User(user_data[0][0], user_data[0][1], user_data[0][2], user_data[0][3], user_data[0][4], user_data[0][5], user_data[0][6], user_data[0][7])
            g.user = user
        else:
            g.user = None

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response 

# Routing
@app.route('/')
def Index():
    session.pop('user_id', None)
    return render_template('index.html')

@app.route('/registro')
def Registro():
    return render_template('Registro.html')

@app.route('/password_recovery')
def Password_recovery():
    return render_template('PasswordRecovery.html')

@app.route('/password_change')
def Password_change():
    return render_template('PasswordChange.html')

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
                password = hashlib.md5(request.form['password'].encode()).hexdigest()
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
    global id_inst
    id_inst = -1
    session.pop('user_id', None)
    return redirect(url_for('Index'))

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        institucion = request.form['institucion']
        email = request.form['email']
        nombre = request.form['nombre']
        apellido_pat = request.form['apellido_pat']
        apellido_mat = request.form['apellido_mat']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        giro = request.form['giro']

        cur = mysql.connection.cursor()
        cur.execute('''
        INSERT INTO institucion
        (nombre_institucion, correo_admin, nombre_admin, apellido_pat_admin, apellido_mat_admin, pass_admin, giro_institucion)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', 
        (institucion, email, nombre, apellido_pat, apellido_mat, password, giro))

        mysql.connection.commit()

        flash('Cuenta dada de alta exitosamente', 'alert-primary')
    return redirect(url_for('Inicio'))

def get_user(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM institucion WHERE id_institucion = %s', (id,))
        data = cur.fetchall()
        return data
    except Exception as e:
        return redirect(url_for('Index'))

def count_users():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(id_institucion) FROM institucion')
        data = cur.fetchall()
        return data
    except Exception as e:
        return redirect(url_for('Index'))

@app.route('/update_user/<id>', methods=['POST'])
def update_user(id):
    if request.method == 'POST':
        institucion = request.form['institucion']
        email = request.form['email']
        nombre = request.form['nombre']
        apellido_pat = request.form['apellido_pat']
        apellido_mat = request.form['apellido_mat']
        password = request.form['password']
        giro = request.form['giro']
        cur = mysql.connection.cursor()
        cur.execute('''
        UPDATE institucion 
        SET nombre_institucion = %s,
            correo_admin = %s,
            nombre_admin = %s,
            apellido_pat_admin = %s,
            apellido_mat_admin = %s,
            pass_admin = %s,
            giro_institucion = %s
        WHERE id_institucion = %s
        ''', (institucion, email, nombre, apellido_pat, apellido_mat, password, giro, id))
        mysql.connection.commit()
        flash('Datos actualizados exitosamente')

    return redirect(url_for('Index'))

# Password Recovery methods
@app.route('/send_mail', methods=['POST'])
def Send_mail():
    try:
        if request.method == 'POST':
            email = request.form['email']
            cur = mysql.connection.cursor()
            cur.execute('SELECT id_institucion FROM institucion WHERE correo_admin = %s', [email])
            data = cur.fetchall()
            
            if data[0][0] != None:
                # We get the datestamp and the caducity for the secret key
                secret_key = secrets.token_hex(16)
                current_datetime = datetime.datetime.now()
                hours = 12
                caducity_hours = datetime.timedelta(hours = hours)
                caducity_datetime = current_datetime + caducity_hours

                cur.execute('''
                INSERT INTO recovery_key
                (id_institucion, secret_key, creation_date, caducity, used)
                VALUES (%s, %s, %s, %s, %s)
                ''', 
                (data[0][0], secret_key, current_datetime, caducity_datetime, 0))
                mysql.connection.commit()


                msg = Message('Password Recovery', sender = 'FaceMaskAdvisor@gmail.com', recipients = [email])

                msg.body = "Introduce la siguiente clave secreta para que puedas recuperar tu contrasseña: " + secret_key
                mail.send(msg)
                flash('Correo enviado', 'alert-success')
                return redirect(url_for('Password_change')) 
            else:
                flash('No existe tal correo', 'alert-danger')
                return redirect(url_for('Password_recovery'))
    except Exception as e:
        print(e)
        flash('Algo salio mal', 'alert-danger')
        return redirect(url_for('Password_recovery'))

@app.route('/change_password', methods=['POST'])
def Change_password():
    try:
        if request.method == 'POST':
            secret_key = request.form['secret_key']
            password = hashlib.md5(request.form['password'].encode()).hexdigest()
            current_datetime = datetime.datetime.now()
            cur = mysql.connection.cursor()
            cur.execute('SELECT id_recovery_key, id_institucion, caducity, used FROM recovery_key WHERE secret_key = %s', [secret_key])
            data = cur.fetchall()
            
            if data[0][2] > current_datetime and data[0][3] == 0:
                cur.execute('''
                UPDATE institucion 
                SET pass_admin = %s
                WHERE id_institucion = %s
                ''', (password, data[0][1]))
                mysql.connection.commit()

                cur.execute('''
                UPDATE recovery_key 
                SET used = %s
                WHERE id_recovery_key = %s
                ''', (1, data[0][0]))
                mysql.connection.commit()

                flash('Contraseña cambiada', 'alert-success')
                return redirect(url_for('Index')) 
            else:
                flash('La llave secreta ha sido usada o caduco', 'alert-danger')
                return redirect(url_for('Password_recovery'))
    except Exception as e:
        print(e)
        flash('Algo salio mal', 'alert-danger')
        return redirect(url_for('Password_recovery'))

# Account data recovery
@app.route('/consulta', methods=['POST'])
def read_data():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM institucion WHERE correo_admin = %s', email)
        data = cur.fetchall()
        print(data)
    return render_template('MenuCuenta.html', contacts = data )

# Image analysis and chart generation functions
def insert_analysis(probability):
    global id_inst

    date_time = datetime.datetime.now()
    state = -1
    if probability < 0.4:
        state = 1 
    elif 0.4 <= probability <= 0.7:
        state = 2
    elif probability > 0.7:
        state = 3

    id_usuario = id_inst

    try:
        cur = mysql.connection.cursor()
        cur.execute('''
        INSERT INTO analisis
        (fecha_analisis, id_estado, id_institucion)
        VALUES (%s, %s, %s)
        ''', 
        (date_time, state, id_usuario))

        mysql.connection.commit()
        print(f'Registro: [tiempo: {date_time} : state: {state} : id: {id_usuario}]')
    except Exception:
        print(Exception)

@app.route('/get-date-analyses', methods=['POST'])
def get_date_analyses():
    global id_inst
    data_total = [[],[],[]]

    if request.method == 'POST':
        inst = id_inst
        fechas = request.json
        # print(fechas)

        try:
            cur = mysql.connection.cursor()            
            for i in range(len(fechas)):
                cur.execute('''
                SELECT 
                SUM(case when id_estado = 1 then 1 else 0 end), 
                SUM(case when id_estado = 2 then 1 else 0 end), 
                SUM(case when id_estado = 3 then 1 else 0 end)   
                FROM analisis 
                where DATE(fecha_analisis) = %s and id_institucion = %s
                ''', 
                (fechas[i], inst))

                data = cur.fetchall()
                data_total[0].append(data[0][0])
                data_total[1].append(data[0][1])   
                data_total[2].append(data[0][2])               

        except Exception:
            print(Exception) 

    return jsonify(data_total)


@app.route('/get-daily-analyses', methods=['POST'])
def get_daily_analyses():
    global id_inst
    data_total = [[],[],[]]

    if request.method == 'POST':
        inst = id_inst
        fechas = request.json
       
        fecha_f = datetime.datetime.now()
        fecha_f = fecha_f.replace(hour=23, minute=59, second=59)
        fechas.append(fecha_f)

        try:
            cur = mysql.connection.cursor()            
            for i in range(len(fechas)-1):
                cur.execute('''
                SELECT 
                SUM(case when id_estado = 1 then 1 else 0 end), 
                SUM(case when id_estado = 2 then 1 else 0 end), 
                SUM(case when id_estado = 3 then 1 else 0 end)   
                FROM analisis 
                where fecha_analisis >= %s and fecha_analisis <= %s and id_institucion = %s
                ''', 
                (fechas[i], fechas[i+1], inst))

                data = cur.fetchall()
                data_total[0].append(data[0][0])
                data_total[1].append(data[0][1])   
                data_total[2].append(data[0][2])  
          

        except Exception:
            print(Exception) 

    return jsonify(data_total)


@app.route('/clasificar', methods=['POST'])
def clasificar():
    global count
    global model
    start = time.time()
    data = request.json['photo']
    imgstr = base64.decodebytes(data.split(',')[1].encode())
    img = Image.open(io.BytesIO(imgstr)).convert('RGB')
    
    # transforms = Compose([Grayscale(num_output_channels=3), Resize(256), CenterCrop(224)])
    # img.save(f'test.png')

    transforms = Compose([Grayscale(num_output_channels=3), Resize(256), CenterCrop(224), ToTensor()])
    message = ''
    with torch.no_grad():
        img = transforms(img).float().unsqueeze(0) * 255
        pred = model.forward(img)
        if pred.item() > 0.5:
            message = 'Felicidades! sabes usar un cubrebocas'
        else:
            message = 'Lo estas usando mal >:c'
    end = time.time()
    print(f'{end - start} seconds')

    # Guardamos la prediccion en la base de datos
    insert_analysis(pred.item())
    return jsonify({'message': message, 'prob': pred.item()})

if __name__ == '__main__':
    app.run(port = 5000, debug = True)