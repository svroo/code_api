import ast
import os
import re
from dataclasses import dataclass

from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from groq import Groq
from pydantic import BaseModel

load_dotenv()  # Cargamos el ambiente para localizar el archivo .env

APIKEY = os.getenv("MY_KEY")
# from Procesamiento import


class getRecomendations:
    """Clase para obtener las recomendaciones para las clases, metodos y variables.

    Parms:
        javaCode (str): Código java del que se quiere obtener un mejor nombramiento.
    """

    # typeRecomendation: str = "clase"
    javaCode: str = None
    # model: str = "qwen-2.5-coder-32b"
    model: str = "llama3-8b-8192"

    def getPrompt(self) -> str:
        """Función que realiza el prompt para el LLM de acuerdo a los parametros de entrada

        Returns:
            str: Si los valores no son None, retorna el prompt para el LLM.
        """
        code = self.javaCode if self.javaCode is not None else None
        # typeRecomendation = (
        #     self.typeRecomendation if self.typeRecomendation is not None else None
        # )

        a = {
            "variables": {"x": "", "usrnm": ""},
            "metodos": {"calculo": "", "getUsr": ""},
            "clases": {"datosUsr": ""},
        }
        if code is not None:  # and typeRecomendation is not None:
            prompt = f"""
            Quiero que generes sugerencias de nombres siguiendo buenas prácticas de nomenclatura en Java.
            Para el siguiente código, {self.javaCode}
            El formato de salida debe ser un JSON donde:
            - La llave principal sea el tipo de elemento que se va a modificar: "variables", "métodos", "clases".
            - El valor de cada llave principal sea otro JSON con pares clave-valor, donde:
            - La clave sea el nombre actual del elemento.
            - El valor sea la sugerencia de un nuevo nombre siguiendo buenas prácticas de legibilidad, significado y estilo.

            Reglas específicas:
            - Usa `camelCase` para variables y métodos.
            - Usa `PascalCase` para clases.
            - Evita modificar el nombre del parámetro `args` en `public static void main(String[] args)`, ya que es una convención en Java.
            - Genera nombres que sean lo suficientemente descriptivos sin ser excesivamente largos.

            Ejemplo de entrada:
            ```json
            {a}
            No expliques nada simplemente retorna la respuesta.
            """
            return prompt
        #             if typeRecomendation.lower() == "clase":
        #                 prompt = (
        #                     f"Dame un diccionario de python donde las claves sean los nombres actuales\
        # de la {typeRecomendation} en el código: {code}, y los valores sean son los nombres más descriptivos. No \
        # expliques nada, que los nombres sigan la convención CammelCase y en ingles."
        #                 )
        #                 return prompt

        #             if typeRecomendation.lower() == "metodos":
        #                 prompt = (
        #                     f"Dame un diccionario de python donde las claves sean los nombres actuales\
        # de los {typeRecomendation} escritos por el usuario en el código: {code}, ignora los metodos propios\
        #     del lenguaje java, los valores sean los nombres más descriptivos. No \
        # expliques nada, que los nombres sigan la convención CammelCase y en ingles."
        #                 )
        #                 return prompt

        #             if typeRecomendation.lower() == "variables":
        #                 prompt = (
        #                     f"Dame un diccionario de python donde las claves sean los nombres actuales\
        # de las {typeRecomendation} escritos por el usuario en el código: {code}, ignora las variables que se usan en\
        #     los ciclos, ignora los metodos propios de java, los valores sean los nombres más descriptivos. No \
        # expliques nada, que los nombres sigan la convención CammelCase y en ingles."
        #                 )
        # return prompt

        return None

    def cleanDict(self, item: str) -> dict:
        """Función para transformar la respuesta del modelo que viene en formato markdown a un
        diccionario de python con el que se pueda trabajar posteriormente.

        Args:
            item (str): Respuesta del modelo en formato str de python, dentro contiene un
            diccionario en formato markdown

        Returns:
            dict: Diccionario donde la llave es el nombre de la clase, metodo ó variables del
            código y el valor nuevo es el que el modelo propuso.
        """

        # r = re.sub(r"```|python|\n", "", item)
        # r = r.split(":")
        match = re.search(r"```(.*?)```", item, re.DOTALL)
        # print("Post sub: ", match.group(1).strip())
        r = match.group(1).strip()

        if (
            "=" in r
        ):  # if para comprobar si la respuesta proviene de deepseek retorna valor distinto a los demas
            r = r.split("=")[-1]

        flag = True if "{" in r else None

        if flag is not None:
            flag = True if "}" in item else None

            if flag is not None:
                return ast.literal_eval(
                    r
                )  # esto transforma una cadena a un tipo de dato python

            else:
                item = [item] + ["}"]
                return ast.literal_eval(" ".join(item))

    def chatGroq(self):
        # print(f"Valores:\n{self.javaCode}\n{self.typeRecomendation}")
        client = Groq(api_key=APIKEY)
        prompt = self.getPrompt()

        try:
            completition = client.chat.completions.create(
                model=self.model,
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
            print("Respuesta del modelo", response)

            if self.model.startswith("deepseek"):
                response = re.split(pattern=r"</think>", string=response)[1]

            # response = self.cleanDict(response)

            # return response
            match = re.search(r"```(.*?)```", response, re.DOTALL)
            r = match.group(1).strip()
            index = None

            if "{" in r:
                index = r.index("{")

            # print("after group", r)

            if index is not None:
                return ast.literal_eval(r[index:])

            return None

        except Exception as e:
            print("Error con: ", e)
            return None


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


# @app.get("/")
# async def getHome():
#     return {"Index": "hola mundo"}


# @app.post("/getRecomendations", response_model=responseModel)
@app.post("/getRecomendations")
async def recomendations(recomendation: recomendation):
    # tipo = input.typeRecomendation
    javaCode = recomendation.javaCode

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
