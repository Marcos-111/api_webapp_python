#!/usr/bin/env python
'''
API Personas
---------------------------
Autor: Inove Coding School
Version: 1.0
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas registradas.

Ejecución: Lanzar el programa y abrir en un navegador la siguiente dirección URL
NOTA: Si es la primera vez que se lanza este programa crear la base de datos
entrando a la siguiente URL
http://127.0.0.1:5000/reset

Ingresar a la siguiente URL para ver los endpoints disponibles
http://127.0.0.1:5000/
'''

__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "1.0"


import traceback
import io
import sys
import os
import base64
import json
import sqlite3
from datetime import datetime, timedelta

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect
import matplotlib
matplotlib.use('Agg')   # For multi thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

import persona
from config import config


app = Flask(__name__)

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db = config('db', config_path_name)
server = config('server', config_path_name)

persona.db = db


@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[GET] /personas --> mostrar la tabla de personas (el HTML)</h3>"
        result += "<h3>[GET] /personas/tabla --> mostrar la tabla de personas (el HTML)</h3>"
        result += "<h3>[GET] /personas/json --> mostrar personas en JSON</h3>"
        result += "<h3>[POST] /registro --> enviar el JSON para completar la tabla</h3>"
        result += "<h3>[GET] /registro --> mostrar el HTML con el formulario de registro de persona</h3>"
        result += "<h3>[GET] /comparativa --> mostrar un gráfico que compare cuantas personas hay de cada nacionalidad"
        
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        persona.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/personas")
def personas():
    try:
        return render_template('tabla.html')
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/personas/tabla")
def personas_tabla():
    try:
        
        data = persona.report()
         
        return jsonify(data)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/personas/json")
def personas_JSON():

    try:
        # Mostrar todas las personas en JSON
        result = persona.report()
        return jsonify(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/comparativa")
def comparativa():
    try:
        conn = sqlite3.connect(db['database'])
        c = conn.cursor()

        c.execute('SELECT nationality FROM persona')

                
        query_results = c.fetchall()

    
        conn.close()

        dicc_ok = [x[0] for x in query_results]

        nat_rev = persona.nationality_review(dicc_ok)

        
        fig = plt.figure()
        fig.suptitle('API', fontsize=16)
        ax = fig.add_subplot()


        ax.pie(nat_rev.values(), labels=nat_rev.keys(), 
               autopct='%1.1f%%', shadow=True, startangle=90
               )
        ax.axis('equal')

        
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})



@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        try:
            return render_template('registro.html')
        except:
            return jsonify({'trace': traceback.format_exc()})

    if request.method == 'POST':
        try:
          
            name = str(request.form.get('name'))
            age = str(request.form.get('age'))
            nationality = str(request.form.get('nationality'))
            persona.insert(name, int(age), nationality)
            return Response(status=200)
        except:
            return jsonify({'trace': traceback.format_exc()})


def html_table(data):

    # Tabla HTML, header y formato
    result = '<table border="1">'
    result += '<thead cellpadding="1.0" cellspacing="1.0">'
    result += '<tr>'
    result += '<th>Nombre</th>'
    result += '<th>Edad</th>'
    result += '<th>Nacionalidad</th>'
    result += '</tr>'

    for row in data:
        # Fila de una tabla HTML
        result += '<tr>'
        result += '<td>' + str(row[0]) + '</td>'
        result += '<td>' + int(row[1]) + '</td>'
        result += '<td>' + str(row[2]) + '</td>'
        result += '</tr>'

    # Fin de la tabla HTML
    result += '</thead cellpadding="0" cellspacing="0" >'
    result += '</table>'

    return result



    

if __name__ == '__main__':
    print('Servidor arriba!')

    app.run(host=server['host'],
            port=server['port'],
            debug=True)
