import speech_recognition as sr
import socket
import os
import time

bufferSize = 1024


r = sr.Recognizer()
print("teodio")

def recibir_Tablero(TCPClientSocket):
    linea = "_______________________________________________________________________________"
    tablero = [["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""],
               ["","","","","",""]]
    for i in range(10):
        for j in range(6):
            
            data = TCPClientSocket.recv(bufferSize)
            resp = data.decode("utf8")
            tablero[i][j] = resp
            print("|" + resp, end="\t")
            time.sleep(0.01)    
        print("\n"+linea)
    return tablero


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    HOST = input("Ingrese la IP del servidor: ") 
    PORT = int(input("Ingrese el puerto del servidor: "))
    TCPClientSocket.connect((HOST, PORT))
    personajes_bajados = []
    tiempo_inicial = time.time()
    barrier = TCPClientSocket.recv(bufferSize)
    string1 = barrier.decode("utf8")
    print(string1)
    end_barrier = TCPClientSocket.recv(bufferSize)
    string2 = end_barrier.decode("utf8")
    print(string2)
    tablero = recibir_Tablero(TCPClientSocket)
    while True:
        print("Espera tu turno")
        data = TCPClientSocket.recv(bufferSize)
        ganador = data.decode("utf8")
        if ganador == "si":
            break
        data = TCPClientSocket.recv(bufferSize)
        print(data.decode("utf8"))
        decision_bajar = input("¿Desea bajar un personaje (s/n): ")
        if decision_bajar == "s":
            personaje_bajado = input("¿Que personaje desea bajar?: ")
            personajes_bajados.append(personaje_bajado)
        res = "n"
        with sr.Microphone() as source:
            while res != "s":
                print("Lo escucho")
                r.adjust_for_ambient_noise(source, duration=0.2)
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio)
                    text = text.lower()
                    print("Usted dijo: {}".format(text))
                    res = input("¿Es correcto? (s/n): ")
                except: 
                    print("No se reconocio")
            TCPClientSocket.sendall(bytes(text, "utf8"))
            data = TCPClientSocket.recv(bufferSize)
            resp = data.decode("utf8")
            print("El personaje "+resp+" tiene esa caracteristica \n")
            linea = "_______________________________________________________________________________"
            for i in range(10):
                for j in range(6):
                    if tablero[i][0] not in personajes_bajados:
                        val = tablero[i][j]
                        print("|",val, end = "\t")
                print("\n"+linea)
    data = TCPClientSocket.recv(bufferSize)
    print(data.decode("utf8"))
    tiempo_final = time.time()
    tiempo_ejecucion = tiempo_final - tiempo_inicial
    print("Duracion de la partida: %.2f segs." % round(tiempo_ejecucion, 2))
    os.system("pause")
