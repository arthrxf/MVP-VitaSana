from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info, Tag
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint  # type: ignore
from urllib.parse import unquote
from model import db, init_db, Cliente, Comentario
from logger import logger
from schemas import (
    ClienteCreateSchema,
    ClienteViewSchema,
    ListagemClientesSchema,
    ClienteDelSchema,
    ErrorSchema,
    ClienteBuscaSchema,
    ClienteCreateSchema,
    ComentarioCreateSchema
)
from werkzeug.utils import secure_filename
import os

# Configuração da API e informações
info = Info(title="API Clínica VitaSana", version="2.0.0")
app = OpenAPI(__name__, info=info)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Vitasana1.@localhost/Dados_VitaSana'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Caminho para salvar o arquivo swagger.json
SWAGGER_JSON_PATH = os.path.join(
    os.path.dirname(__file__), 'static', 'swagger.json')

# Definindo URL e caminho para o Swagger UI
SWAGGER_URL = '/swagger-ui'
API_URL = '/static/swagger.json'

# Criando e registrando o blueprint do Swagger UI
swagger_ui = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "VitaSana API"}
)
app.register_blueprint(swagger_ui, url_prefix=SWAGGER_URL)

# Rota para fornecer o swagger.json


@app.route("/static/swagger.json")
def swagger_json():
    """Serve o arquivo swagger.json."""
    return app.send_static_file("swagger.json")


# Inicializando o banco de dados
# init_db(app)

# Definindo tags
home_tag = Tag(name="Documentação",
               description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
cliente_tag = Tag(
    name="Cliente", description="Adição, visualização e remoção de clientes")
comentario_tag = Tag(
    name="Comentário", description="Adição de comentários a clientes cadastrados")

# Rota principal para documentação


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para a documentação Swagger UI."""
    return redirect('/swagger-ui')


@app.get('/clientes', tags=[cliente_tag], responses={"200": ListagemClientesSchema, "404": ErrorSchema})
def get_clientes(query: ClienteBuscaSchema = None):
    """Retorna a listagem de todos os clientes cadastrados ou busca pelo nome do cliente."""
    logger.debug("Buscando clientes na base de dados")

    db_query = db.session.query(Cliente)

    # Filtrar pelo nome ou listar todos se query for None
    if query:
        if query.nome:
            logger.debug(f"Realizando busca por nome: {query.nome}")
            db_query = db_query.filter(Cliente.nome.ilike(f"%{query.nome}%"))
        if query.email:
            db_query = db_query.filter(Cliente.email == query.email)
        if query.cpf:
            db_query = db_query.filter(Cliente.cpf == query.cpf)
        if query.idade:
            logger.debug(f"Realizando busca por idade: {query.idade}")
            db_query = db_query.filter(Cliente.idade == query.idade)
        if query.telefone:
            logger.debug(f"Realizando busca por telefone: {query.telefone}")
            db_query = db_query.filter(
                Cliente.telefone.ilike(f"%{query.telefone}%"))

    # Executa a consulta no banco de dados
    clientes = db_query.all()

    # Retorna mensagem caso não haja resultados
    if not clientes:
        logger.debug("Nenhum cliente encontrado.")
        return {"message": "Nenhum cliente encontrado."}, 404

    print(f"{len(clientes)} cliente(s) encontrado(s).")
    return jsonify({"clientes": [cliente.to_dict() for cliente in clientes]}), 200


@app.post("/cliente", tags=[cliente_tag], responses={"201": ClienteViewSchema, "400": ErrorSchema})
def add_cliente():
    """Adiciona um cliente ao banco de dados."""
    try:
        # Recebendo os dados com request.form
        nome = request.form.get("nome")
        idade = request.form.get("idade")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        cpf = request.form.get("cpf")

        # Verificar se todos os campos necessários estão presentes
        if not (nome and idade and telefone and email and cpf):
            return {"message": "Todos os campos são obrigatórios."}, 400

        # Validar e converter idade para inteiro
        try:
            idade = int(idade)
        except ValueError:
            return {"message": "Idade deve ser um número inteiro."}, 400

        # Verificar se já existe um cliente com o mesmo email ou CPF
        cliente_existente = db.session.query(
            Cliente).filter_by(email=email).first()
        if cliente_existente:
            # Conflito: E-mail duplicado
            return jsonify({"message": "Já existe um cliente com esse e-mail."}), 409

        cliente_existente_cpf = db.session.query(
            Cliente).filter_by(cpf=cpf).first()
        if cliente_existente_cpf:
            # Conflito: CPF duplicado
            return jsonify({"message": "Já existe um cliente com esse CPF."}), 409

        # Criar um novo cliente com os dados recebidos
        novo_cliente = Cliente(
            nome=nome,
            idade=idade,
            telefone=telefone,
            email=email,
            cpf=cpf
        )

        # Adicionar o cliente ao banco de dados
        db.session.add(novo_cliente)
        db.session.commit()

        # Retornar os dados do cliente criado
        print(ClienteViewSchema)
        return ClienteViewSchema.from_orm(novo_cliente).dict(), 201

    except Exception as e:
        # Caso ocorra algum erro, retornar mensagem de erro
        logger.error(f"Erro ao adicionar cliente: {str(e)}")
        return {"error": str(e)}, 400


@app.post("/comentario", tags=[comentario_tag], responses={"200": ClienteViewSchema, "404": ErrorSchema})
def add_comentario(body: ComentarioCreateSchema):
    """Adiciona um comentário a um cliente cadastrado pelo cpf."""
    logger.debug(f"Adicionando comentário ao cliente com cpf: {
                 body.cliente_cpf}")

    cliente = db.session.query(Cliente).filter(
        Cliente.cpf.ilike(f"%{body.cliente_cpf}%")).first()
    if not cliente:
        error_msg = "Cliente não encontrado na base de dados."
        logger.warning(f"Erro ao adicionar comentário: {error_msg}")
        return {"message": error_msg}, 404

    comentario = Comentario(texto=body.texto, cliente_id=cliente.id)
    db.session.add(comentario)
    db.session.commit()

    logger.debug(f"Comentário adicionado ao cliente: {cliente.nome}")
    return ClienteViewSchema.from_orm(cliente).dict(), 200


@app.delete("/cliente", tags=[cliente_tag], responses={"200": ClienteDelSchema, "404": ErrorSchema})
def del_cliente(query: ClienteBuscaSchema):
    """Remove um cliente da base de dados pelo nome."""
    print(query)
    cliente_cpf = unquote(query.cpf)  # Usando o nome informado no parâmetro
    logger.debug(f"Deletando cliente com cpf: {cliente_cpf}")

    cliente = db.session.query(Cliente).filter(
        Cliente.cpf.ilike(f"%{cliente_cpf}%")).first()
    

    if not cliente:
        error_msg = "Cliente não encontrado na base de dados."
        logger.warning(f"Erro ao deletar cliente: {error_msg}")
        return {"message": error_msg}, 404

    db.session.delete(cliente)
    db.session.commit()

    logger.debug(f"Cliente com nome {cliente_cpf} deletado.")
    return {"message": "Cliente deletado com sucesso.", "nome": cliente_cpf}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
