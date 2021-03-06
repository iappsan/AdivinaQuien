import socket
import os
import sys
import threading
import time
from random import randint

HOST = input("Ingrese la IP del servidor: ") 
PORT = int(input("Ingrese el puerto del servidor: "))
num_Conexiones = int(input("Ingrese la cantidad de conexiones: "))
listaConexiones = []
bufferSize = 1024

tablero = [["pedro  ","negro  ","delgada ","doctor     ","hombre","adulto"],
           ["laura  ","castaño","delgada ","presidente ","mujer ","viejo "],
           ["marta  ","castaño","robusta ","maestro    ","mujer ","viejo "],
           ["juan   ","azul   ","atletica","programador","hombre","joven "],
           ["carlos ","rojo   ","atletica","bombero    ","hombre","adulto"],
           ["andrea ","rosa   ","delgada ","contador   ","mujer ","viejo "],
           ["brenda ","negro  ","delgada ","enfermera  ","mujer ","joven "],
           ["oscar  ","castaño","robusta ","policia    ","hombre","adulto"],
           ["manuel ","azul   ","delgada ","astronauta ","hombre","joven "],
           ["daniela","rojo   ","robusta ","cocinero   ","mujer ","adulto"]]

pregunta = ""
jugador_ganador = False
ganador = ""


def imprimir_tablero(Client_conn):
    for i in range(10):
        for j in range(6):
            Client_conn.send(bytes(tablero[i][j], "utf8"))
            time.sleep(0.03)


def servirPorSiempre(socketTcp, listaconexiones):
    barrier = threading.Barrier(int(num_Conexiones)) 
    lock = threading.Lock()
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print(f"Conectado a {client_addr}")
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr, barrier, lock])
            thread_read.start()
            gestion_conexiones(listaConexiones)
    except Exception as e:
        print(e)


def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1: #Revisamos si la conexion sigue activa
            listaconexiones.remove(conn)
    # print("hilos activos:", threading.active_count())
    # print("enum", threading.enumerate())
    # print("conexiones: ", len(listaconexiones))
    # print(listaconexiones)


def jugador_activo(Client_conn, tablero, n):
    global pregunta, jugador_ganador, ganador
    Client_conn.send(bytes("Es tu turno", "utf8"))

    data = Client_conn.recv(bufferSize)
    pregunta = data.decode("utf8")
    respuesta_Correcta = "no"

    for i in range(6):
        if pregunta == tablero[n][i].lower().strip():
            respuesta_Correcta = "si"
    Client_conn.send(bytes(respuesta_Correcta, "utf8"))

    if tablero[n][0].lower().strip() == pregunta:
        jugador_ganador = True
        ganador = threading.current_thread().name


def recibir_datos(Client_conn, addr, barrier, lock):
    cur_thread = threading.current_thread()
    jugador_actual = threading.current_thread().name
    print(f"Recibiendo datos del cliente {addr} en el {cur_thread.name}")
    print(f"Jugador {jugador_actual} esperando en la barrera con {barrier.n_waiting} hilos más")
    jugadores_Faltantes = int(num_Conexiones) - (barrier.n_waiting + 1)
    mensaje = f"Faltan {jugadores_Faltantes} jugadores para comenzar"
    Client_conn.send(bytes(mensaje, "utf8"))
    jugador = barrier.wait()
    print(f"Jugador actual {jugador_actual} esta despues de la barrera", jugador)
    time.sleep(1)
    Client_conn.send(bytes("Todos los jugadores se han conectado", "utf8"))
    n = randint(0, 9)
    personaje_asignado = tablero[n][0]
    print(f"Se le asigno a {jugador_actual} {personaje_asignado}")
    imprimir_tablero(Client_conn)
    while True:
        lock.acquire()
        print(f"Turno de {jugador_actual}")
        if jugador_ganador:
            print(f"Gano el jugador {ganador}")
            Client_conn.send(bytes("si", "utf8"))
            if ganador == jugador_actual:
                Client_conn.send(bytes("Ganaste la partida !", "utf8"))
            else:
                Client_conn.send(bytes(f"Perdiste la partida, el ganador fue: {ganador}", "utf8"))
            lock.release()
            break
        else:
            print("Nadie gana aun")
            Client_conn.send(bytes("no", "utf8"))
        jugador_activo(Client_conn, tablero, n)
        lock.release()
        time.sleep(0.1)
    Client_conn.close()




serveraddr = (HOST, int(PORT))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(num_Conexiones))
    print("El servidor TCP está disponible y en espera de solicitudes")
    servirPorSiempre(TCPServerSocket, listaConexiones)
