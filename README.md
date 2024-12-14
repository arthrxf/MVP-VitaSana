# API Clínica VitaSana

## Descrição

A API Clínica VitaSana foi criada com o objetivo de gerenciar informações de clientes de uma clínica. Atualmente, ela permite o cadastro e a visualização de clientes, mas a meta é expandir a aplicação para incluir diversos recursos que irão facilitar o trabalho e o gerenciamento do staff da clínica. O projeto está sendo desenvolvido para atender a necessidades mais amplas e melhorar a experiência dos usuários.

## Instruções de Instalação

Para configurar o ambiente local e rodar o projeto, siga as etapas abaixo:

1. Criar e ativar o ambiente virtual
Se estiver usando venv:
python -m venv venv
source venv/bin/activate 

2. Instalar as dependências
Instale as dependências do projeto usando pip:
pip install -r requirements.txt

3. Configuração do Banco de Dados
Verifique se o banco de dados MySQL esteja configurado corretamente. O banco de dados utilizado é o MySQL. Você pode configurar as credenciais no arquivo app.py.

4. Inicializar o Banco de Dados

5. Rodar a aplicação
Após a instalação das dependências e configuração do banco, execute o comando abaixo para iniciar o servidor local:
flask run --host 0.0.0.0 --port 5000 --reload

Agora você pode acessar a documentação da API em http://localhost:5001/swagger-ui para visualizar e testar as rotas.
