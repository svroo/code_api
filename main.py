import ast
import os
import re

# from dataclasses import dataclass
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from groq import Groq
from pydantic import BaseModel

load_dotenv()  # Cargamos el ambiente para localizar el archivo .env

# Expresión regular para clases de Java
class_pattern = re.compile(
    r"\b(public|private|protected|abstract|final|static)?\s+(class)\s+([A-Z][a-zA-Z0-9_]*)\b"
)

# Expresión regular para métodos de Java
method_pattern = re.compile(
    r"\b(public|private|protected|static|final|abstract|synchronized|native)\s+"  # Modificadores
    r"([A-Za-z0-9_<>?, \t\n\r\f]+)\s+"  # Tipo de retorno (puede ser complejo, ej: List<String>)
    r"([a-z][a-zA-Z0-9_]*)\s*"  # Nombre del método (camelCase)
    r"\(([^)]*)\)"  # Parámetros entre paréntesis
)

APIKEY = os.getenv("MY_KEY")
# APIKEY = "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"
# from Procesamiento import

app = FastAPI()


# Ejemplo de entrada
class Recomendation(BaseModel):
    javaCode: str


# Ejemplo de retorno de la api
class responseModel(BaseModel):
    javaCode: str
    tipeModification: int
    changes: dict


a = {
    "variables": {"x": "", "usrnm": ""},
    "metodos": {"calculo": "", "getUsr": ""},
    "clases": {"datosUsr": ""},
}


# @app.post("/getRecomendations", response_model=responseModel)
@app.post("/")
async def recomendations(recomendation: Recomendation):
    # tipo = input.typeRecomendation

    # return {"message": "Funciona", "javaCode": recomendation.javaCode}

    javaCode = recomendation.javaCode
    # return {"codigo": javaCode}

    if isinstance(javaCode, str) and len(javaCode) >= 1:
        if len(javaCode) >= 1:
            print("el codigo es valido")
            # Si el código es una clase o tiene una clase entonces manda recomendaciones
            if class_pattern.search(javaCode):
                print("el codigo es clase")
                prompt = f"""
                Genera sugerencias de nombres siguiendo buenas prácticas de nomenclatura en Java para el codigo {javaCode} .
                Devuelve un JSON con la estructura:
                Claves principales: "variables", "metodos", "clases".
                Cada clave contiene un objeto con pares "nombre_actual": "nombre_sugerido".

                Reglas:
                Variables y métodos → camelCase.
                Clases → PascalCase.
                No renombrar args en main.
                Nombres claros y descriptivos, no excesivamente largos.
                No expliques nada, solo devuelve el JSON.
                Ejemplo de entrada:
                {a}
                """
                client = Groq(api_key=APIKEY)
                try:
                    completition = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.76,
                        max_completion_tokens=1024,
                        top_p=1,
                        stream=True,
                        stop=None,
                    )

                    response = "".join(
                        chunk.choices[0].delta.content or "" for chunk in completition
                    )
                    # print("Respuesta del modelo", response)

                    # if self.model.startswith("deepseek"):
                    #     response = re.split(pattern=r"</think>", string=response)[1]

                    # response = self.cleanDict(response)

                    # return response
                    if "`" in response:
                        match = re.search(r"```(.*?)```", response, re.DOTALL)
                        # print(match)
                        response = match.group(1).strip()

                    index = None

                    # if ":" in response:
                    # response = response.split("")[1]

                    if "{" in response:
                        index = response.index("{")

                    try:
                        if index is not None:
                            dataReturn = {
                                "javaCode": recomendation.javaCode,
                                # "tipeModification": tipeModification[input.typeRecomendation.lower()],
                                "changes": ast.literal_eval(response),
                            }
                            return dataReturn
                    except Exception as e:
                        dataReturn = {
                            "javaCode": recomendation.javaCode,
                            # "tipeModification": tipeModification[input.typeRecomendation.lower()],
                            "changes": response,
                        }
                        return dataReturn

                except Exception as e:
                    print("Error con: ", e)
                    return None
            else:
                # if para ver si el texto contiene un metodo si lo tiene manda las recomendaciones
                if method_pattern.search(javaCode):
                    print("El codigo contiene un metodo")

                    prompt = f"""
                        Genera sugerencias de nombres siguiendo buenas prácticas de nomenclatura en Java para el codigo {javaCode}. Devuelve un JSON con la estructura:
                        Claves principales: "variables", "metodos", "clases".
                        Cada clave contiene un objeto con pares "nombre_actual": "nombre_sugerido".

                        Reglas:
                        Variables y métodos → camelCase.
                        Clases → PascalCase.
                        No renombrar args en main.
                        Nombres claros y descriptivos, no excesivamente largos.
                        No expliques nada, solo devuelve el JSON.
                        Ejemplo de entrada:
                        {a}
                    """
                    client = Groq(api_key=APIKEY)
                    try:
                        completition = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.76,
                            max_completion_tokens=1024,
                            top_p=1,
                            stream=True,
                            stop=None,
                        )

                        response = "".join(
                            chunk.choices[0].delta.content or ""
                            for chunk in completition
                        )
                        # print("Respuesta del modelo", response)

                        # if self.model.startswith("deepseek"):
                        #     response = re.split(pattern=r"</think>", string=response)[1]

                        # response = self.cleanDict(response)

                        # return response
                        if "`" in response:
                            match = re.search(r"```(.*?)```", response, re.DOTALL)
                            # print(match)
                            response = match.group(1).strip()

                        index = None

                        # if ":" in response:
                        # response = response.split("")[1]

                        if "{" in response:
                            index = response.index("{")

                        try:
                            if index is not None:
                                dataReturn = {
                                    "javaCode": recomendation.javaCode,
                                    # "tipeModification": tipeModification[input.typeRecomendation.lower()],
                                    "changes": ast.literal_eval(response),
                                }
                                return dataReturn
                        except Exception as e:
                            print("Fallo al crear diccionario", e)
                            dataReturn = {
                                "javaCode": recomendation.javaCode,
                                # "tipeModification": tipeModification[input.typeRecomendation.lower()],
                                "changes": response,
                            }
                            return dataReturn
                    except Exception as e:
                        print("Error con: ", e)
                        return {"Fallo": "Fallo en el metodo"}
                else:
                    client = Groq(api_key=APIKEY)
                    prompt = f"""El siguiente código no contiene ni clases ni metodos, retorna un JSON donde la llave sea el valor actual y el valor
                    sea el nuevo nombre siguiendo las siguientes reglas:
                    Reglas:
                        Variables y métodos → camelCase.
                        Clases → PascalCase.
                        No renombrar args en main.
                        Nombres claros y descriptivos, no excesivamente largos.
                        No expliques nada, solo devuelve el JSON.
                    para el siguiente codigo: 
                    {javaCode}
                    """
                    try:
                        completition = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.76,
                            max_completion_tokens=1024,
                            top_p=1,
                            stream=True,
                            stop=None,
                        )

                        response = "".join(
                            chunk.choices[0].delta.content or ""
                            for chunk in completition
                        )

                        return {"Error": response}
                    except Exception as e:
                        print("Error", e)
                        return {"Error": "Codigo no valido"}
        else:
            return {"ERROR": "Valor no valido"}
    else:
        return {"ERROR": "Valor no valido"}
