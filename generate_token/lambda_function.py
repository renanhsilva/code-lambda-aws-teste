import json
import boto3
import jwt

SECRET_NAME = "token-secret"  # Nome do segredo no AWS Secret Manager

def lambda_handler(event, context):
    # Recebe o CPF a partir do evento de entrada 
    cpf = event.get("cpf")

    if not cpf:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "CPF nao fornecido"})
        }
    
    # CPF deve ser válido
    if not validate_cpf(cpf):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "CPF invalido"})
        }

    # Recupere o segredo do AWS Secret Manager
    secret_value = get_secret_value(SECRET_NAME)

    if not secret_value:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Falha ao recuperar o segredo"})
        }

    secret = secret_value["SecretString"]

    # Gere um token JWT usando o segredo
    jwt_token = generate_jwt_token(cpf, secret)

    return {
        "statusCode": 200,
        "body": json.dumps({"token": jwt_token})
    }

def validate_cpf(cpf):
    # Implemente a validação do CPF aqui
    if cpf == "12345678900": #Somente um exemplo
        return True
    pass

def get_secret_value(secret_name):
    # Conecte-se ao AWS Secret Manager e recupere o valor do segredo
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        return json.loads(response["SecretString"])
    else:
        return None

def generate_jwt_token(cpf, secret):
    # Gere um token JWT usando a biblioteca PyJWT
    token_payload = {"cpf": cpf}
    jwt_token = jwt.encode(token_payload, secret, algorithm="HS256")

    return jwt_token
