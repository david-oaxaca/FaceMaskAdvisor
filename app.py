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

# Conexion a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
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
        #print(id_usuario)
        user_data = get_user(id_usuario)
        # print(user_data)
        user = User(user_data[0][0], user_data[0][1], user_data[0][2], user_data[0][3], user_data[0][4], user_data[0][5], user_data[0][6], user_data[0][7])
        g.user = user

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
        password = request.form['password']
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