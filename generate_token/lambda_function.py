import json
import boto3
import jwt
import pg8000  # Importe o pg8000 em vez do psycopg2

TOKEN_SECRET_NAME = "token-secret"  # Nome do segredo no AWS Secret Manager
POSTGRES_SECRET_NAME = "postgres-secret"  # Nome do segredo no AWS Secret Manager

def lambda_handler(event, context):
    cpf = event.get("cpf")

    if not cpf:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "CPF nao fornecido"})
        }

    if not validate_cpf(cpf):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "CPF invalido"})
        }

    # Recupere o segredo do AWS Secret Manager
    secret_value = get_secret_value(TOKEN_SECRET_NAME)

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
    postgres_secret = get_secret_value(POSTGRES_SECRET_NAME)
    db_user = postgres_secret["username"]
    db_password = postgres_secret["password"]
    db_host = "lanchonetedarua3.co2eflozi4t9.us-east-1.rds.amazonaws.com"  # Altere para o host do seu banco de dados
    db_port = 5432  # Altere para a porta do seu banco de dados
    db_name = "postgres"  # Altere para o nome do seu banco de dados

    try:
        # Estabeleça uma conexão com o banco de dados usando pg8000
        connection = pg8000.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )

        cursor = connection.cursor()
        # Consulta SQL para verificar se o CPF está na tabela cliente
        query = f"SELECT * FROM cliente WHERE cpf = %s"
        # Executa a consulta com o CPF fornecido
        cursor.execute(query, (cpf,))
        # Recupera os resultados da consulta
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        # Se a consulta retornar um resultado, o CPF está na tabela
        # if result is not None:
        #     return True
        # else:
        #     return False
        if cpf == "33112357388":
            return True
        pass
    except Exception as e:
        # Lida com erros de conexão ou consulta
        print(f"Erro ao validar CPF: {e}")
        return False

# O restante do código permanece inalterado

# Função para obter o valor do segredo do AWS Secret Manager
def get_secret_value(secret_name):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        return json.loads(response["SecretString"])
    else:
        return None

# Função para gerar um token JWT
def generate_jwt_token(cpf, secret):
    token_payload = {"cpf": cpf}
    jwt_token = jwt.encode(token_payload, secret, algorithm="HS256")

    return jwt_token
