#Importamos el modulo de FastAPI
from fastapi import Depends, HTTPException, FastAPI, Body, Path, Query, status, Request
from fastapi.responses import HTMLResponse, JSONResponse #Importamos la clase "HTMLResponse" para devolver un HTML
from pydantic import BaseModel, Field #Importamos "BaseModel" que me va a permitir crear el esquema
from typing import Any, Coroutine, Optional, List

from starlette.requests import Request
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

#Creamos una instancia de FastAPI creando la variable app
app = FastAPI()
app.title = "Mi Aplicación Movie con FastAPI"
app.version = "0.0.1"

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Credenciales no son validas")

#Crear nuevo modelo que me permita añadir informacion de usuario
class User(BaseModel):
    email: str 
    password: str


class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(ge=1900, le=2021)
    rating: float = Field(ge=0.0, le=10.0) #ge -> mayor igual | le -> menor igual
    category: str = Field(min_length=5, max_length=15)

    #Campos por defecto
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Mi pelicula",
                "overview": "Descripcion de mi pelicula ...",
                "year": 2000,
                "rating": 5.0,
                "category": "Acción"
            }
        }

'''
#Creamos el esquema de datos, creando una clase
class Movie(BaseModel):
    #id: int | None = None
    id: Optional[int] = None
    title: str
    overview: str
    year: int
    rating: float
    category: str
'''

#Creamos el listado de peliculas
movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'
    },

    {
        'id': 2,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'
    }
]

#Creamos nuestro primer EndPoint
@app.get("/", tags=['Home']) #Ruta de Inicio
def message(): #Funcion que se va a ejecutar
    #return {"Hello" : "World"} #Retorna un mensaje, puedes reotrnar cualquier un string, bool, etc
    return HTMLResponse('<h1>Hello World</h1>')



#Ruta que le permita al usuario loguearse
@app.post("/login", tags=["auth"], response_model=dict, status_code=200)
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(content=token, status_code=200)
    return JSONResponse(content={"message": "usuario o contraseña incorrectos"}, status_code=401)


#Ruta que nos va a devolver el listado de unas películas
@app.get("/movies", tags=["Movies"], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)


@app.get("/movies/{id}", tags=["Movies"], response_model=Movie)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
    for item in movies:
        if item['id'] == id:
            return JSONResponse(content=item)
        return JSONResponse(status_code=404, content=[])

'''
#Para indicarle a una ruta que va a requerir de parametros debemos añadir una nueva ruta
#En este caso el parametro que yo espero recibir es el "id"
@app.get("/movies/{id}", tags=["Movies"])
def get_movie(id: int): #Asi accedemos al parametro
    #Filtrado
    for item in movies:
        if item['id'] == id:
            return item
    return []
'''
    

@app.get("/movies/", tags=["movies"], response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
    data = [item for item in movies if item['category'] == category]
    return JSONResponse(content=data)

'''
#Creamos una nueva ruta con @app.get
@app.get("/movies/", tags=["Movies"])
def get_movies_by_category(category: str):
    return [item for item in movies if item['category'] == category] #Filtrado de las peliculas por su categoria
'''
    

#Registro
@app.post("/movies", tags=["Movies"], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict:
    movies.append(movie)
    return JSONResponse(status_code=201, content={"message": "Se registró la película"})

#Modificar una pelicula
@app.put("/movies", tags=["Movies"], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie) -> dict:
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
            return JSONResponse(status_code=200, content={"message": "Se modificó la película"})
        #return[] ## ó tambíen puedes regresar un string(con un mensaje de que no encontro la pelicula) en caso de que no encuntre el id de la pelicula en tu lista

#Eliminacion 
@app.delete("/movies", tags=["Movies"], response_model=dict, status_code=200)
def delete_movie(id: int) -> dict:
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
    return JSONResponse(status_code=200, content={"message": "Se eliminó la película"})