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
respuesta = ""
band_ganador = False
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
            print("Conectado a", client_addr)
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr, barrier, lock])
            thread_read.start()
            gestion_conexiones(listaConexiones)
    except Exception as e:
        print(e)


def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    # print("hilos activos:", threading.active_count())
    # print("enum", threading.enumerate())
    # print("conexiones: ", len(listaconexiones))
    # print(listaconexiones)


def jugador_activo(Client_conn, tablero, n):
    global pregunta, respuesta, band_ganador, ganador
    Client_conn.send(bytes("Es tu turno", "utf8"))

    data = Client_conn.recv(bufferSize)
    pregunta = data.decode("utf8")
    band = "no"

    for i in range(6):
        if pregunta == tablero[n][i].lower().strip():
            band = "si"
    respuesta = band
    Client_conn.send(bytes(band, "utf8"))

    if tablero[n][0].lower().strip() == pregunta:
        band_ganador = True
        ganador = threading.current_thread().name


def recibir_datos(Client_conn, addr, barrier, lock):
    cur_thread = threading.current_thread()
    print("Recibiendo datos del cliente {} en el {}".format(addr, cur_thread.name))
    print(threading.current_thread().name,"Esperando en la barrera con {} hilos más".format(barrier.n_waiting))
    mensaje = "Faltan {} jugadores para comenzar".format(int(num_Conexiones) - (barrier.n_waiting + 1))
    Client_conn.send(bytes(mensaje, "utf8"))
    jugador = barrier.wait()
    print(threading.current_thread().name, "Después de la barrera", jugador)
    time.sleep(1)
    Client_conn.send(bytes("Todos los jugadores se han conectado", "utf8"))
    n = randint(0, 9)
    print("Se le asigno a {} {}".format(threading.current_thread().name, tablero[n][0]))
    imprimir_tablero(Client_conn)
    while True:
        lock.acquire()
        print("Turno de " + threading.current_thread().name)
        if band_ganador:
            print("gano " + ganador)
            Client_conn.send(bytes("si", "utf8"))
            if ganador == threading.current_thread().name:
                Client_conn.send(bytes("Ganaste la partida !", "utf8"))
            else:
                Client_conn.send(bytes("Perdiste la partida, el ganador fue: " + ganador, "utf8"))
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
