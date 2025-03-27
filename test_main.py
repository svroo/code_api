from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def testMain():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Index": "hola mundo"}


def testInputMethods():
    java_code = """
    public class Main { public static void main(String[] args) {
        int rows = 5;
        for (int i = 1; i <= rows; ++i) {
            for (int j = 1; j <= i; ++j) {
                System.out.print('*');
            }  
        System.out.println();  
        } 
    } 
    """

    response = client.post(
        "/getRecomendations",
        json={"typeRecomendation": "metodos", "javaCode": java_code},
    )

    assert response.status_code == 200
    # assert response.json() == {
    #     "javaCode": "public class Main { public static void main(String[] args) {  int rows = 5;   for (int i = 1; i <= rows; ++i) {   for (int j = 1; j <= i; ++j) {   System.out.print('*');   }  System.out.println();  } } }",
    #     "tipeModification": 2,
    #     "changes": {"main": "printStarPattern"},
    # }
    response_dict = response.json()

    assert response_dict["tipeModification"] == 2
    assert response_dict["changes"] == {"main": "printStarPattern"}


def testInputClass():
    java_code = """
    public class Main { public static void main(String[] args) {
        int rows = 5;
        for (int i = 1; i <= rows; ++i) {
            for (int j = 1; j <= i; ++j) {
                System.out.print('*');
            }  
        System.out.println();  
        } 
    } 
    """

    response = client.post(
        "/getRecomendations",
        json={"typeRecomendation": "clase", "javaCode": java_code},
    )

    assert response.status_code == 200

    response_dict = response.json()

    assert response_dict["tipeModification"] == 1
    assert response_dict["changes"] == {
        "Main": "StarPatternPrinter",
        "main": "printStarPattern",
        "rows": "numberOfRows",
        "i": "currentRow",
        "j": "currentColumn",
    }


def testInputVar():
    java_code = """
    public class Main { public static void main(String[] args) {
        int rows = 5;
        for (int i = 1; i <= rows; ++i) {
            for (int j = 1; j <= i; ++j) {
                System.out.print('*');
            }  
        System.out.println();  
        } 
    } 
    """

    response = client.post(
        "/getRecomendations",
        json={"typeRecomendation": "clase", "javaCode": java_code},
    )

    assert response.status_code == 200

    response_dict = response.json()

    assert response_dict["tipeModification"] == 3
    assert response_dict["changes"] == {
        "rows": "numberOfRows",
        "i": "currentRow",
        "j": "currentColumn",
    }
