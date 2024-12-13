from flask_sqlalchemy import SQLAlchemy
import os

# Instanciando o objeto db para usar com Flask-SQLAlchemy
db = SQLAlchemy()

# Verifica se o diretório de banco de dados existe
db_path = "database/"
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Configurando a URL do banco de dados MySQL
db_url = 'mysql+pymysql://root:Vitasana1.@localhost/Dados_VitaSana'

# Definindo o modelo Cliente


class Cliente(db.Model):
    __tablename__ = 'cliente'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(140), nullable=False)
    idade = db.Column(db.Integer)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)

    # Relacionamento com Comentário
    comentarios = db.relationship(
        "Comentario", backref="cliente", cascade="all, delete")

    def __init__(self, nome: str, idade: int, telefone: str, email: str, cpf: str):
        self.nome = nome
        self.idade = idade
        self.telefone = telefone
        self.email = email
        self.cpf = cpf

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'idade': self.idade
        }

    def adiciona_comentario(self, comentario):
        """ Adiciona um comentário ao cliente """
        self.comentarios.append(comentario)

# Definindo o modelo Comentario


class Comentario(db.Model):
    __tablename__ = 'comentario'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(4000), nullable=False)

    # Definição do relacionamento com Cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey(
        'cliente.id'), nullable=False)

    def __init__(self, texto: str, cliente_id: int):
        self.texto = texto
        self.cliente_id = cliente_id

# Inicializando o banco de dados


def init_db(app):
    """Inicializa o banco de dados com o contexto do Flask."""
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()
