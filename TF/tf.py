import pandas as pd
import math
import heapq as hq
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure

calles = pd.read_csv("Lima-calles.csv",encoding='latin-1')

data= pd.read_csv("Lima-intersecciones.csv",encoding='latin-1')#.iloc[0:100]


horas = [0.9] * 6 + [1.3, 1.5, 1.3] + [1] * 7 + [0.9] * 2 + [1.5] * 3 + [1.04] * 3


vs = {}

# Recorrer los datos para generar lista de Adyacencia
# uso un diccionario lo cual no es optimo para la velocidad de ejecucion
# pero era la unica opcion ya que en el dataset faltan algunas calles y
# se reduce significativamente la cantidad de espacios en lso arreglos que usariamos
# al usar un diccionario, que solo almacene la cantidad necesaria de nodos.

for i, row in data.iterrows():
    act = str(row['Item'])
    origen = str(row['ID_Origen_intereccion'])
    origenla = float(row['Latitud_Origen_Interseccion'])
    origenlo = float(row['Longitud_Origen_Interseccion'])
    final = str(row['ID_Final_Interseccion'])
    finalla = float(row['Latitud_Destino_Interseccion'])
    finallo = float(row['Longitud_Destino_Interseccion'])
    cost = float(row['Costo1']) * float(row['Costo2']) / 2.0
    dist = float(row['distancia_Km'])
    
    
    if origen not in vs:
        vs[origen]=[]
    if final not in vs:
        vs[final]=[]
    if act not in vs:
        vs[act]=[]
    
    
    vs[act] += [{'id': origen, 'pos': [origenla, origenlo], 'dist': dist * cost}]
    vs[act] += [{'id': final, 'pos': [finalla, finallo], 'dist': dist * cost}]
    
    vs[origen] += [{'id': act, 'pos': [], 'dist': dist * cost}]
    vs[final] += [{'id': act, 'pos': [], 'dist': dist * cost}]

 

#  El algoritmo que use para buscar el camino mas corto entre 2 nodos
# fue dijkstra. La complejidad de este algoritmo es O(V * 2) donde V es la 
# cantidad de intersecciones del dataset.
def dijkstra(G, s, multiplier):
    n = len(G)
    visited = {}
    path = {}
    cost = {}
    path[s] = '='
    cost[s] = 0
    pqueue = [(0, s)]
    while pqueue:
        g, u = hq.heappop(pqueue)
        if u not in visited:
            visited[u] = True
            for r in G[u]:
                v, w = r['id'], r['dist']
                # aqui se considera el trafico
                w *= multiplier
                if v not in visited:
                    f = g + w
                    c = math.inf if v not in cost else cost[v]
                    if f < c:
                        cost[v] = f
                        path[v] = u
                        hq.heappush(pqueue, (f, v))

    return path, cost


def get_nombre(Item):
    st = data[data['Item'] == Item]['ID_Origen_intereccion','ID_Final_Interseccion'].values
    if len(st):
        return st[0]
    else:
        return 'Sin nombre'

def get_coord(Item):
    out = data[data['Item'] == Item][['Latitud_Origen_Interseccion','Longitud_Origen_Interseccion']].values
    if len(out):
        lat, lon = out[0]
        return [lon, lat]
    else:
        return [0, 0]

def get_item(Item):
    return data[data['Item'] == int(Item)]
 

# cargo una lista de latitudes y longitudes
# para mostrar un mapa
x = []
y = []

for it in vs:
    for c in vs[it]:
        if c['pos']:
          lat, lon = c['pos']
        else: 
            continue
        y += [lat]
        x += [lon]

fig = Figure(figsize=(5,5),dpi=100)
ax = fig.add_subplot(111)

def dibujo(win): 
    ax.scatter(x, y,5)
    win.draw()


def dibujo_ruta(ruta):

    fig = Figure(figsize=(5,5),dpi=100)
    ax = fig.add_subplot(111)
    pos={'x':[],'y':[], 'name':[]}

    exes = []
    ways = []
    for i, i_str in enumerate(ruta):
        item = int(i_str)
        x = data[data['Item'] == item][['Longitud_Origen_Interseccion']]
        y = data[data['Item'] == item][['Latitud_Origen_Interseccion']]
        name = data[data['Item'] == item][['Nombre_Calle']]
        if len(x) and len(y) and len(name):
            pos['x']+= [x.values[0][0]]
            pos['y']+= [y.values[0][0]]
            pos['name']+= [name.values[0][0]]
            x = x.values[0][0]
            y = y.values[0][0]
            name = name.values[0][0]
            plt.scatter(x, y)
            plt.annotate(name, (x,y))
            exes += [x]
            ways += [y]

            print(name, end= "")
            if i < len(ruta) -1:
                print(' -> ', end='')
    
    df=pd.DataFrame(pos)
    for i,row in df.iterrows():
        if i==0:
            pass
        else:
            plt.annotate('',xy=(row['x'],row['y']),xytext=(df.iloc[i-1]['x'],df.iloc[i-1]['y']),
            arrowprops=dict(facecolor='black',width=1,headwidth=5))

    print()


    plt.show()
    


def dijk(a,b, t): 
    time = int(t)
    objetivo = b
    multiplier = horas[time]
    path,cost = dijkstra(vs, objetivo, multiplier)

    camino = []
    inicio = a
    actual = inicio
    while True:
        if actual == '=':
            break
        camino += [actual]
        actual = path[actual]

    camino += [objetivo]

    dibujo_ruta(camino)

def rutas():
    ventana=tk.Tk()
    ventana.title("Datos")
    ventana.geometry( '380x300')
    e1=tk.Label (ventana, text="Item ID Inicio:",bg="green", fg="white")
    e1.pack(padx=5, pady=4,ipadx=5,ipady=5, fill=tk.X)
    entrada1=tk.Entry(ventana)
    entrada1.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
    e2=tk.Label (ventana, text= "Item ID Final:",bg="green" , fg="white" )
    e2.pack(padx=5, pady=4, ipadx=5, ipady=5, fill=tk.X)
    entrada2=tk.Entry(ventana)
    entrada2.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
    e3=tk.Label (ventana, text= "Hora de salida (24h):",bg="green" , fg="white" )
    e3.pack(padx=5, pady=4, ipadx=5, ipady=5, fill=tk.X)
    entrada3=tk.Entry(ventana)
    entrada3.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
    buttona = tk.Button(ventana, text="Dibuja el mapa", \
            command=lambda:dijk(entrada1.get(),entrada2.get(),entrada3.get()))
    buttona.pack(side=tk.TOP)
    ventana.mainloop()

root = tk.Tk()
canvas = FigureCanvasTkAgg(fig, root)
canvas.draw()
canvas.get_tk_widget().pack(pady=10)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack()
button = tk.Button(root, text="Dibuja el mapa", command=lambda: dibujo(canvas))
button.pack()
button2 = tk.Button(root, text="Ruta", command=rutas)
button2.pack()
root.mainloop()
