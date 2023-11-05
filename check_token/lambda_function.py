import json
import jwt
import boto3

SECRET_NAME = "token-secret"  # Nome do segredo no AWS Secret Manager

def lambda_handler(event, context):
    # Recebe o token JWT da entrada do evento
    jwt_token = event.get("token")

    if not jwt_token:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Token JWT nao fornecido"})
        }

    # Recupera o segredo do AWS Secret Manager
    secret_value = get_secret_value(SECRET_NAME)

    if not secret_value:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Falha ao recuperar o segredo"})
        }

    secret = secret_value["SecretString"]

    # Valida o token JWT
    valid = validate_jwt_token(jwt_token, secret)

    if valid:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "active"})
        }
    else:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Token JWT invalido ou expirado"})
        }

def get_secret_value(secret_name):
    # Conecta-se ao AWS Secret Manager e recupera o valor do segredo
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        return json.loads(response["SecretString"])
    else:
        return None

def validate_jwt_token(jwt_token, secret):
    try:
        # Decodificar o token JWT usando a chave secreta
        token_payload = jwt.decode(jwt_token, secret, algorithms=["HS256"])

        # Verificar se o payload do token contém o campo "cpf"
        if "cpf" in token_payload:
            cpf = token_payload["cpf"]
            return True
        else:
            return False
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
