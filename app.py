from flask import Flask, render_template, request, redirect, jsonify, send_file, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from io import StringIO
from io import BytesIO
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "SEGREDO_MUITO_SEGURO_E_LONGO") 

# 🔗 Conexão com PostgreSQL do Render
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # URL fixa para testes locais
    DATABASE_URL = "postgresql://compras_db_ny5g_user:q00cmzOnnraJPKPIuLWku3km8GikZi7I@dpg-d419opgdl3ps73d8ddtg-a.oregon-postgres.render.com/compras_db_ny5g"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------------------------
# MODELOS DE BANCO (PostgreSQL)
# -------------------------------------------------
class Compra(db.Model):
    __tablename__ = "compras"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20))
    local = db.Column(db.String(100))
    produto = db.Column(db.String(100))
    quantidade = db.Column(db.Integer)
    valor = db.Column(db.Float)

class Produto(db.Model):
    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True)

with app.app_context():
    db.create_all()

# -------------------------------------------------
# ROTAS DE PÁGINAS
# -------------------------------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')

# -------------------------------------------------
# LISTAR COMPRAS (API para o JS)
# -------------------------------------------------
@app.route('/listar_compras')
def listar_compras_api():
    compras = Compra.query.order_by(Compra.id.asc()).all()
    lista_de_compras = [
        [c.id, c.data, c.local, c.produto, c.quantidade, c.valor]
        for c in compras
    ]
    return jsonify(lista_de_compras)

# -------------------------------------------------
# CADASTRAR COMPRA 
# -------------------------------------------------
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"erro": "Dados inválidos ou ausentes."}), 400

    data = dados.get('data')
    local = dados.get('local')
    produto = dados.get('produto')
    quantidade = dados.get('quantidade')
    valor_str = dados.get('valor')

    if not (data and local and produto and quantidade and valor_str):
        return jsonify({"erro": "⚠️ Todos os campos devem ser preenchidos!"}), 400

    try:
        valor_float = float(valor_str)
        quantidade_int = int(quantidade)
    except ValueError:
        return jsonify({"erro": "❌ Valor ou Quantidade inválida."}), 400

    try:
        nova_compra = Compra(data=data, local=local, produto=produto, quantidade=quantidade_int, valor=valor_float)
        db.session.add(nova_compra)
        db.session.commit()
        return jsonify({"mensagem": "✅ Item cadastrado com sucesso!"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Erro ao cadastrar no banco de dados."}), 500


# -------------------------------------------------
# EXCLUIR ITEM (API para o JS)
# -------------------------------------------------
@app.route('/deletar/<int:id>', methods=['DELETE'])
def deletar_item_api(id):
    item = Compra.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"mensagem": "Item excluído com sucesso!"}), 200
    return jsonify({"erro": "Item não encontrado."}), 404

@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    item = Compra.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("🗑️ Item excluído com sucesso!")
    return redirect('/index')


# -------------------------------------------------
# RESET COMPLETO
# -------------------------------------------------
@app.route('/reset', methods=["POST"])
def reset_data():
    db.session.query(Compra).delete()
    db.session.query(Produto).delete()
    db.session.commit()
    flash("✅ Reset completo: banco limpo.")
    return redirect('/index')

# -------------------------------------------------
# PRODUTOS
# -------------------------------------------------
@app.route("/listar_produtos")
def listar_produtos():
    produtos = Produto.query.order_by(Produto.nome.asc()).all()
    return jsonify([p.nome for p in produtos])

@app.route("/adicionar_produto", methods=["POST"])
def adicionar_produto():
    data = request.get_json()
    novo_produto = data.get("produto")

    if not novo_produto:
        return "Nome inválido", 400

    try:
        novo = Produto(nome=novo_produto)
        db.session.add(novo)
        db.session.commit()
        return "Produto adicionado", 200
    except Exception:
        db.session.rollback()
        return "Produto já existe", 409

# -------------------------------------------------
# RELATÓRIOS (PostgreSQL)
# -------------------------------------------------
@app.route('/relatorio_dados/<tipo>')
def relatorio_dados(tipo):
    dados = []

    if tipo == "produto":
        resultados = db.session.query(
            Compra.produto, Compra.local, func.sum(Compra.valor * Compra.quantidade)
        ).group_by(Compra.produto, Compra.local).all()
        dados = [{"Produto": p, "Local": l, "Total R$": f"{t:.2f}".replace('.', ',')} for p, l, t in resultados]

    elif tipo == "local":
        resultados = db.session.query(
            Compra.local, func.substr(Compra.data, 6, 2), func.sum(Compra.valor * Compra.quantidade)
        ).group_by(Compra.local, func.substr(Compra.data, 6, 2)).all()
        dados = [{"Local": l, "Mês": m, "Total R$": f"{t:.2f}".replace('.', ',')} for l, m, t in resultados]

    elif tipo == "data":
        resultados = db.session.query(
            Compra.data, func.sum(Compra.valor * Compra.quantidade)
        ).group_by(Compra.data).all()
        dados = [{"Data": d, "Total R$": f"{t:.2f}".replace('.', ',')} for d, t in resultados]

    elif tipo == "mes":
        resultados = db.session.query(
            func.substr(Compra.data, 6, 2), func.sum(Compra.valor * Compra.quantidade)
        ).group_by(func.substr(Compra.data, 6, 2)).all()
        dados = [{"Mês": m, "Total R$": f"{t:.2f}".replace('.', ',')} for m, t in resultados]

    elif tipo == "ano":
        resultados = db.session.query(
            func.substr(Compra.data, 1, 4), func.sum(Compra.valor * Compra.quantidade)
        ).group_by(func.substr(Compra.data, 1, 4)).all()
        dados = [{"Ano": a, "Total R$": f"{t:.2f}".replace('.', ',')} for a, t in resultados]

    return jsonify(dados)

# -------------------------------------------------
# GERAR CSV DE CADA TIPO DE RELATÓRIO (COM BOM UTF-8)
# -------------------------------------------------
@app.route("/gerar_csv_tipo/<tipo>")
def gerar_csv_tipo(tipo):
    
    if tipo == "produto":
        resultados = db.session.query(
            Compra.produto,
            func.count(Compra.id),
            func.sum(Compra.valor * Compra.quantidade)
        ).group_by(Compra.produto).all()
        cabecalho = ["Produto", "Quantidade", "Total (R$)"]

    elif tipo == "local":
        resultados = db.session.query(
            Compra.local,
            func.count(Compra.id),
            func.sum(Compra.valor * Compra.quantidade)
        ).group_by(Compra.local).all()
        cabecalho = ["Local", "Quantidade", "Total (R$)"]

    elif tipo == "data":
        resultados = db.session.query(
            Compra.data,
            func.count(Compra.id),
            func.sum(Compra.valor * Compra.quantidade)
        ).group_by(Compra.data).all()
        cabecalho = ["Data", "Quantidade", "Total (R$)"]

    elif tipo == "mes":
        resultados = db.session.query(
            func.substr(Compra.data, 6, 2),
            func.count(Compra.id),
            func.sum(Compra.valor * Compra.quantidade)
        ).group_by(func.substr(Compra.data, 6, 2)).all()
        cabecalho = ["Mês", "Quantidade", "Total (R$)"]

    elif tipo == "ano":
        resultados = db.session.query(
            func.substr(Compra.data, 1, 4),
            func.count(Compra.id),
            func.sum(Compra.valor * Compra.quantidade)
        ).group_by(func.substr(Compra.data, 1, 4)).all()
        cabecalho = ["Ano", "Quantidade", "Total (R$)"]

    else:
        return "Tipo de relatório inválido", 400

    csv_output = StringIO()
    writer = csv.writer(csv_output, delimiter=';')
    writer.writerow(cabecalho)
    for linha in resultados:
        linha_formatada = [
            str(linha[0]),
            str(linha[1]),
            f"{linha[2]:.2f}".replace('.', ',') if linha[2] is not None else "0,00"
        ]
        writer.writerow(linha_formatada)

    csv_output.seek(0)
    # 🌟 CORREÇÃO DE CODIFICAÇÃO: Adiciona o Byte Order Mark (BOM) para compatibilidade com o Excel
    csv_bytes = BytesIO(b'\xef\xbb\xbf' + csv_output.getvalue().encode('utf-8'))

    return send_file(
        csv_bytes,
        as_attachment=True,
        download_name=f"relatorio_{tipo}.csv",
        mimetype="text/csv"
    )

# -------------------------------------------------
# GERAR CSV COMPLETO (COM BOM UTF-8)
# -------------------------------------------------
@app.route('/gerar_csv', methods=['GET'])
def gerar_csv_completo():
    compras = Compra.query.order_by(Compra.id.asc()).all()
    
    csv_output = StringIO()
    writer = csv.writer(csv_output, delimiter=';')
    
    writer.writerow(["ID", "Data", "Local", "Produto", "Quantidade", "Valor (R$)"])
    
    for item in compras:
        writer.writerow([
            item.id,
            item.data,
            item.local,
            item.produto,
            item.quantidade,
            f"{item.valor:.2f}".replace('.', ',')
        ])

    csv_output.seek(0)
    # 🌟 CORREÇÃO DE CODIFICAÇÃO: Adiciona o Byte Order Mark (BOM) para compatibilidade com o Excel
    csv_bytes = BytesIO(b'\xef\xbb\xbf' + csv_output.getvalue().encode('utf-8'))

    return send_file(
        csv_bytes,
        as_attachment=True,
        download_name="compras_completas.csv",
        mimetype="text/csv"
    )

if __name__ == '__main__':
    app.run(debug=True)