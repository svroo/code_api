from fastapi import FastAPI
from pydantic import BaseModel

from Procesamiento import getRecomendations

app = FastAPI()

tipeModification = {
    "clase": 1,
    "metodos": 2,
    "variables": 3,
}


class recomendation(BaseModel):
    typeRecomendation: str
    javaCode: str


class responseModel(BaseModel):
    javaCode: str
    tipeModification: int
    changes: dict


@app.get("/")
async def getHome():
    return {"Index": "hola mundo"}


# @app.post("/getRecomendations", response_model=responseModel)
@app.post("/getRecomendations")
async def recomendations(input: recomendation):
    tipo = input.typeRecomendation
    javaCode = input.javaCode
    # print(input.typeRecomendation)

    classRecomendation = getRecomendations(typeRecomendation=tipo, javaCode=javaCode)

    recomendations = classRecomendation.chatGroq()

    return {
        "javaCode": input.javaCode,
        "tipeModification": tipeModification[input.typeRecomendation.lower()],
        "changes": recomendations,
    }
