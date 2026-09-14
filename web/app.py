import os
import pandas as pd
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '..', 'data', 'c500.csv')
cobb500Dataframe = pd.read_csv(CSV_PATH)

alimentoPorDia = cobb500Dataframe['Daily Feed Intake (g)'].tolist()

@app.route("/")
def index():
    return render_template("index.html")

def calcularComidaDia(cantidadPollos, mortalidad, edad, alimentoDia):
    if (edad >= 58) or (edad <= 0):
        return 0
    if cantidadPollos < mortalidad:
        return 0
    
    return ((cantidadPollos - mortalidad) * alimentoDia[edad - 1]) / 1000

def calcularComidaTotal(cantidadPollos, mortalidad, edad, alimentoDia):
    total = []
    if cantidadPollos < mortalidad:
        return 0

    for i in range(edad, len(alimentoDia)):
        total.append(round(calcularComidaDia(cantidadPollos, mortalidad, i, alimentoDia), 2))
    return total

@socketio.on("calcular")
def manejar_calculo(data):
    cantidadPollos = int(data["cantidadPollos"])
    mortalidad = int(data["mortalidad"])
    edad = int(data["edad"])

    comidaDia = calcularComidaDia(cantidadPollos, mortalidad, edad, alimentoPorDia)
    comidaPorDia = calcularComidaTotal(cantidadPollos, mortalidad, edad, alimentoPorDia)
    comidaTotal = round(sum(comidaPorDia), 2)

    socketio.emit("resultado_calculo", {
        "comidaDia": comidaDia,
        "comidaPorDia": comidaPorDia,
        "comidaTotal": comidaTotal,
        "edad": edad
    })

if __name__ == "__main__":
    socketio.run(app, debug=True)