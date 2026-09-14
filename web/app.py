import pandas as pd
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

cobb500Dataframe = pd.read_csv('data/c500.csv')
alimentoPorDia = cobb500Dataframe['Daily Feed Intake (g)'].tolist()


@app.route("/")
def index():
    return render_template("index.html")


def calcularComidaDia(cantidadPollos, mortalidad, edad, alimentoDia):
    if (edad >= 58) or (edad <= 0):
        return 0
    return ((cantidadPollos - mortalidad) * alimentoDia[edad - 1]) / 1000


def calcularComidaTotal(cantidadPollos, mortalidad, edad, alimentoDia):
    total = []
    for i in range(edad, len(alimentoDia)):
        total.append(round(calcularComidaDia(cantidadPollos, mortalidad, i, alimentoDia), 2))
    return total


# Evento que llega desde el HTML al tocar el botón
@socketio.on("calcular")
def manejar_calculo(data):
    cantidadPollos = int(data["cantidadPollos"])
    mortalidad = int(data["mortalidad"])
    edad = int(data["edad"])

    comidaDia = calcularComidaDia(cantidadPollos, mortalidad, edad, alimentoPorDia)
    comidaPorDia = calcularComidaTotal(cantidadPollos, mortalidad, edad, alimentoPorDia)  # lista
    comidaTotal = round(sum(comidaPorDia), 2)  # si además querés el total sumado

    socketio.emit("resultado_calculo", {
        "comidaDia": comidaDia,
        "comidaPorDia": comidaPorDia,
        "comidaTotal": comidaTotal
    })


if __name__ == "__main__":
    socketio.run(app, debug=True)