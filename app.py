from fastapi import FastAPI
from pydantic import BaseModel

from Procesamiento import getRecomendations

app = FastAPI()

# tipeModification = {
#     "clase": 1,
#     "metodos": 2,
#     "variables": 3,
# }


# Ejemplo de entrada
class recomendation(BaseModel):
    # typeRecomendation: str
    javaCode: str


# Ejemplo de retorno de la api
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
    # tipo = input.typeRecomendation
    javaCode = input.javaCode

    if isinstance(javaCode, str) and len(javaCode) >= 1:
        if len(javaCode) >= 1:
            classRecomendation = getRecomendations(javaCode=javaCode)

            recomendations = classRecomendation.chatGroq()
            # print(recomendations)

            dataReturn = {
                "javaCode": input.javaCode,
                # "tipeModification": tipeModification[input.typeRecomendation.lower()],
                "changes": recomendations,
            }

            return dataReturn
        else:
            return "Valor no valido"
    else:
        return None
