from fastapi import FastAPI
from enum import Enum
from datetime import date
from fastapi import HTTPException

from pydantic import BaseModel

# Crear la app
app = FastAPI()

# Ejecutar con uvicorn main:app --reload
# Ver en http://127.0.0.1:8000/docs
 

# Clases para definir las Peliculas

class Genero(Enum):
    TERROR = 'terror'
    ACCION = 'accion'
    DRAMA = 'drama'
    COMEDIA = 'comedia'
    AVENTURA = 'aventura'
    CIENCIA_FICCION = 'ciencia_ficcion'
    MUSICAL = 'musical'


class Pelicula(BaseModel):
    id: int
    nombre: str
    duracion: int
    fecha_lanzamiento: date
    genero: Genero


# Crear Diccionario de Peliculas para tener en la BD
# FastAPI convierte de Pydantic tipos, a JSON, lo que esta GOD

peliculas = {
    0: Pelicula(id=0, nombre='Joker 2', duracion=138, fecha_lanzamiento=date(2024, 8, 4), genero=Genero.MUSICAL),
    1: Pelicula(id=1, nombre='GoodFellas', duracion=155, fecha_lanzamiento=date(1990, 1, 20), genero=Genero.ACCION),
    2: Pelicula(id=2, nombre='Oppenheimer', duracion=180, fecha_lanzamiento=date(2023, 7, 21), genero=Genero.DRAMA),
}

# Para poder hacer querys tipo, /peliculas?duracion=120
# Permite varios tipos
Selection = dict[
    str, int | str | date | Genero | None
]

# FastAPI, se encarga del JSON
# Pydantic tipos, dict[int, Pelicula]
# Get al Raiz
@app.get('/')
def get_pelis() -> dict[str, dict[int, Pelicula]]:
    return {'peliculas' : peliculas}


# Devolver pelicula, pasando id
@app.get('/pelicula/{pelicula_id}')
def get_pelicula_id(pelicula_id: int) -> Pelicula:
    # Sino existe, pues 404
    if pelicula_id not in peliculas:
        raise HTTPException(
            status_code=404, detail=f'Pelicula con id: {pelicula_id} no existe :( '
            )
    return peliculas[pelicula_id]



### NO FUNCIONA, fuck, fuck fuck

# Obtener una peli segun su parametro, None = None (es para que sea opcional)
@app.get('/peliculas/')
def get_peliculas_por_parametro(
    nombre: str | None = None, 
    duracion: int | None = None,  
    fecha_lanzamiento: date | None = None,  
    genero: Genero | None = None
) -> dict[str, Selection]:
    def comprobar_parametro_pelicula(pelicula: Pelicula) -> bool: 
        return all(
            (
                nombre is None or pelicula.nombre == nombre,
                duracion is None or pelicula.duracion == duracion,
                fecha_lanzamiento is None or pelicula.fecha_lanzamiento == fecha_lanzamiento,
                genero is None or pelicula.genero == genero,
            )
        )
        
    resultado = [pelicula for pelicula in peliculas.values() if comprobar_parametro_pelicula(pelicula)]

    if not resultado:
        raise HTTPException(status_code=404, detail="No se encontraron peliculas para el parametro.")

    return {
        "query": {"nombre": nombre, "duracion": duracion, "fecha_lanzamiento": fecha_lanzamiento, "genero": genero},
    }

# Añadir una pelicula
## Ah?? no se guarda permanentemente xD
@app.post("/")
def añadir_peli(pelicula: Pelicula) -> dict[str, Pelicula]:
    if pelicula.id in peliculas:
        HTTPException(status_code=400, detail=f'Pelicula con {pelicula.id} ya existe.')

    peliculas[pelicula.id] = pelicula
    return {'añadir': pelicula}

# Actualizar datos de una pelicula
@app.put('/actualizar/{pelicula_id}')
def actualizar(
    id: int,
    nombre: str | None = None, 
    duracion: int | None = None,  
    fecha_lanzamiento: date | None = None,  
    ):
    if id not in peliculas:
        HTTPException(status_code=404, detail=f'Pelicula con id: {id} ya existe.')
    
    if all(data is None for data in (nombre, duracion, fecha_lanzamiento)):
        raise HTTPException(status_code=400, detail='No se han proporcionado parametros.')

    pelicula = peliculas[id]

    # Actualizar los nuevos datos, a la que ya existe
    if nombre is not None:
        pelicula.nombre = nombre
    
    if duracion is not None:
        pelicula.duracion = duracion

    if fecha_lanzamiento is not None:
        pelicula.fecha_lanzamiento = fecha_lanzamiento

    return {'actualizar': pelicula}


# Borrar, funciona
@app.delete("/borrar/{pelicula_id}")
def añadir_peli(pelicula_id: int) -> dict[str, Pelicula]:
    if pelicula_id not in peliculas:
        HTTPException(status_code=404, detail=f'Pelicula con id: {pelicula_id} no existe.')

    # Borrar y guardar para mostrar
    pelicula = peliculas.pop(pelicula_id)
    return {'borrar': pelicula}