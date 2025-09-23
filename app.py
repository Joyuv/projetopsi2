from flask import *
from models import db, User, Produto
from flask_login import *
from sqlalchemy import *
from faker import Faker
from sqlalchemy.orm import Session

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///projeto.db"

faker = Faker("pt_BR")

db.init_app(app)

with app.app_context():
    db.create_all()

    if db.session.execute(db.select(User).filter_by(id=1)).scalar_one_or_none() != None:
        prodname = faker.name()
        produto = Produto(nome=prodname, preco=10)
        db.session.add(produto)  # Adiciona

        db.session.commit()

login_manager = LoginManager()
app.secret_key = "guilherme"
login_manager.init_app(app)
login_manager.login_view = "index"


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email_usuario = request.form["email_usuario"]
        nome_usuario = request.form["nome_usuario"]
        senha_usuario = request.form["senha_usuario"]

        if not nome_usuario or not senha_usuario or not email_usuario:
            flash("Preencha todos os campos", "error")
            return redirect(url_for("cadastro"))

        user = User(nome_usuario=nome_usuario, email=email_usuario, senha=senha_usuario)
        db.session.add(user)
        db.session.commit()
        redirect(url_for("login"))

    return render_template("cadastro_usuario.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email_usuario = request.form.get("email_usuario")
        senha_usuario = request.form.get("senha_usuario")

        user_data = db.session.execute(
            db.select(User).filter_by(email=email_usuario)
        ).scalar_one_or_none()

        if user_data and user_data.senha == senha_usuario:
            login_user(user_data)
            flash("Login realizado com sucesso", "success")
            return redirect(url_for("index"))
        else:
            flash("Email ou senha inválidos", "danger")

    return render_template("login.html")


@app.route("/produtos")
def produtos():
    produtos = db.session.execute(db.select(Produto).order_by(Produto.nome)).scalars()
    return render_template("produtos.html", produtos=produtos)


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return render_template("index.html")


@app.route("/produto/add", methods=["POST", "GET"])
def add():
    if request.method == "GET":
        return render_template("cadastrar_produto.html")
    else:
        nome = request.form.get("nome_produto")
        descricao = request.form.get("descricao")
        preco = request.form.get("preco")

        produto = Produto(nome=nome, descricao=descricao, preco=preco)

        db.session.add(produto)
        db.session.commit()

        return redirect(url_for("add"))


@app.route("/produto/remove")
def remove():
    id = request.args.get("pro_id")
    produto = db.session.get(Produto, id)
    if produto:
        db.session.delete(produto)
        db.session.commit()
    return redirect(url_for("produtos"))


@app.route("/produto/edit", methods=["POST", "GET"])
def edit():
    if request.method == "GET":
        id = request.args.get("pro_id")
        pro_data = db.session.execute(
            db.select(Produto).filter_by(id=id)
        ).scalar_one_or_none()
        return render_template("editar.html", id=id, produto=pro_data)
    else:
        nome = request.form.get("name")
        descricao = request.form.get("description")
        preco = request.form.get("preco")
        id = request.form.get("id")

        produto = db.session.get(Produto, id)
        if nome:
            produto.nome = nome
        if preco:
            produto.preco = preco
        if descricao:
            produto.descricao = descricao

        db.session.commit()

        return redirect(url_for("produtos"))
