# Aca probar lo que devuelve el server


import requests

#print(requests.get('http://127.0.0.1:8000/pelicula/2').json())
print(requests.get('http://127.0.0.1:8000/peliculas/?nombre=Oppenheimer').json())