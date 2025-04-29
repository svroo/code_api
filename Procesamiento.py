# IMPORTAMOS LIBRERIAS A UTILIZAR
import ast
import os
import re
from dataclasses import dataclass

from dotenv import dotenv_values, load_dotenv
from groq import Groq

load_dotenv()  # Cargamos el ambiente para localizar el archivo .env

APIKEY = os.getenv("MY_KEY")


@dataclass(slots=True)
class getRecomendations:
    """Clase para obtener las recomendaciones para las clases, metodos y variables.

    Parms:
        typeRecomendation (str): Tipo de nombre que se quiere. Default 'Clase'.
        javaCode (str): Código java del que se quiere obtener un mejor nombramiento.
    """

    typeRecomendation: str = "clase"
    javaCode: str = None
    # model: str = "qwen-2.5-coder-32b"
    model: str = "llama3-8b-8192"

    def getPrompt(self) -> str:
        """Función que realiza el prompt para el LLM de acuerdo a los parametros de entrada

        Returns:
            str: Si los valores no son None, retorna el prompt para el LLM.
        """
        code = self.javaCode if self.javaCode is not None else None
        typeRecomendation = (
            self.typeRecomendation if self.typeRecomendation is not None else None
        )

        if code is not None and typeRecomendation is not None:
            if typeRecomendation.lower() == "clase":
                prompt = (
                    f"Dame un diccionario de python donde las claves sean los nombres actuales\
de la {typeRecomendation} en el código: {code}, y los valores sean son los nombres más descriptivos. No \
expliques nada, que los nombres sigan la convención CammelCase y en ingles."
                )
                return prompt

            if typeRecomendation.lower() == "metodos":
                prompt = (
                    f"Dame un diccionario de python donde las claves sean los nombres actuales\
de los {typeRecomendation} escritos por el usuario en el código: {code}, y los valores sean los nombres más descriptivos. No \
expliques nada, que los nombres sigan la convención CammelCase y en ingles."
                )
                return prompt

            if typeRecomendation.lower() == "variables":
                prompt = (
                    f"Dame un diccionario de python donde las claves sean los nombres actuales\
de las {typeRecomendation} escritos por el usuario en el código: {code}, y los valores sean los nombres más descriptivos. No \
expliques nada, que los nombres sigan la convención CammelCase y en ingles."
                )
                return prompt

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

        r = re.sub(r"```|python|\n", "", item)

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
        print(f"Valores:\n{self.javaCode}\n{self.typeRecomendation}")
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

            if self.model.startswith("deepseek"):
                response = re.split(pattern=r"</think>", string=response)[1]

            response = self.cleanDict(response)

            return response

        except Exception as e:
            print("Error con: ", e)
            return None


if __name__ == "__main__":
    code = """
    public class Main {
        public static void main(String[] args) {
            int rows = 5;

            for (int i = 1; i <= rows; ++i) {
            for (int j = 1; j <= i; ++j) {
                System.out.print("* ");
            }
            System.out.println();
            }
        }
        }
    """
    instancia = getRecomendations(javaCode=code)

    print(instancia.chatGroq())


########################################################################################################333
# borrador
# def mergeCodeAndNames(self, df_code: pd.DataFrame, pathFile: str) -> None:
# """Función que utiliza el DataFrame que retorna la función del chat con Groq
# y modifica el código a raiz del nombre sugerido por el LLM y los almacena en disco
# como archivo final para pasarlo a la red neuronal

# Args:
#     df_code (pd.DataFrame): Dataframe que contiene las columnas de codigo, nombres sugeridos
#     pathFile (str): Path donde se va a guardar el archivo resultante de esta función
# """
# listNames = [
#     "Clase",
#     "Métodos",
#     "Variables",
# ]  # lista con el typo de nombre que se solicito al modelo

# # Variable para almacenar codigo bueno y malo
# saveDicts = list()

# # Obtención del codigo bueno y malo
# for index, row in df_code.iterrows():
#     actual = df_code.loc[index, "Sugerencias"]
#     if len(actual) > 0:
#         indice = 0  # Indice para recorrer a listNames
#         for item in actual:
#             for key, value in item.items():
#                 try:
#                     # Se crea una variable con los nombres nuevos proporcionados por el LLM
#                     codigo = re.sub(
#                         pattern=rf"{key}",
#                         repl=value,
#                         string=df_code.loc[index, "Codigo_java"],
#                     )

#                     # Se crea un diccionario con las columnas finales y como es el valor correcto se pasa el valor true en la ultima columan
#                     codigo_bueno = {
#                         "codigo": codigo,
#                         "suggested_name": value,
#                         "type": listNames[indice],
#                         "is_correct": True,
#                     }

#                     # Se guarda el diccionario en una lista
#                     saveDicts.append(codigo_bueno)
#                 except Exception as e:
#                     print(f"Error en el indice: {index}, por: {e}")
#                     pass

#                 # Se guarda un diccionario con el código malo, en la ultima columna se pasa el valor False
#                 codigo_malo = {
#                     "codigo": df_code.loc[index, "Codigo_java"],
#                     "suggested_name": key,
#                     "type": listNames[indice],
#                     "is_correct": False,
#                 }

#                 # Se guarda el diccionario del código malo en la misma lista
#                 saveDicts.append(codigo_malo)

#             indice += 1

# # Se obtiene una lista de dataframes para después crear uno solo
# df_list = [pd.DataFrame([item_dict]) for item_dict in saveDicts]

# # Se guarda el archivo csv en la ruta especificada por el usuario
# pd.concat(df_list).to_csv(
#     path_or_buf=pathFile,
#     encoding="utf-8",
#     index=False,
#     sep=",",
# )
