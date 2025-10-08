from flask import Flask, render_template, request, redirect, jsonify, send_file, flash, url_for, session
import sqlite3
import csv
from io import StringIO
import os
from datetime import datetime 

app = Flask(__name__)
# A chave secreta é essencial para usar a session
app.secret_key = "SEGREDO_MUITO_SEGURO_E_LONGO" # Use uma chave mais segura em produção!

# -------------------------------------------------
# BANCO DE DADOS
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect("compras.db")            
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            local TEXT,
            produto TEXT,
            quantidade INTEGER,
            valor REAL  /* REAL = Float / Número com ponto decimal */
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------
# ROTAS
# -------------------------------------------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cadastro')
def cadastro():
    session.pop('itens_sessao', None)   #Limpa sessão sempre que acessar
    return redirect('/index')

@app.route('/index')
def index():
    if 'itens_sessao' not in session:
        session['itens_sessao'] = []
    return render_template('index.html', compras=session.get('itens_sessao', []))

@app.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')

# --- Rotas de Relatório (Mantidas Inalteradas) ---

@app.route('/relatorio_dados/<tipo>')
def relatorio_dados(tipo):
    conn = sqlite3.connect("compras.db")
    cursor = conn.cursor()
    dados = []

    if tipo == "produto":
        cursor.execute("SELECT produto, local, SUM(valor*quantidade) as Total FROM compras GROUP BY produto, local")
        dados = [{"Produto": p, "Local": l, "Total R$": f"{t:.2f}".replace('.', ',')} for p, l, t in cursor.fetchall()]

    elif tipo == "local":
        cursor.execute("SELECT local, strftime('%m', data) as Mes, SUM(valor*quantidade) FROM compras GROUP BY local, Mes")
        dados = [{"Local": l, "Mês": m, "Total R$": f"{t:.2f}".replace('.', ',')} for l, m, t in cursor.fetchall()]

    elif tipo == "data":
        cursor.execute("SELECT data, SUM(valor*quantidade) FROM compras GROUP BY data")
        dados = [{"Data": d, "Total R$": f"{t:.2f}".replace('.', ',')} for d, t in cursor.fetchall()]

    elif tipo == "mes":
        cursor.execute("SELECT strftime('%m', data) as Mes, SUM(valor*quantidade) FROM compras GROUP BY Mes")
        dados = [{"Mês": m, "Total R$": f"{t:.2f}".replace('.', ',')} for m, t in cursor.fetchall()]

    elif tipo == "ano":
        cursor.execute("SELECT strftime('%Y', data) as Ano, SUM(valor*quantidade) FROM compras GROUP BY Ano")
        dados = [{"Ano": a, "Total R$": f"{t:.2f}".replace('.', ',')} for a, t in cursor.fetchall()]

    conn.close()
    return jsonify(dados)

@app.route('/gerar_csv_tipo/<tipo>')
def gerar_csv_tipo(tipo):
    conn = sqlite3.connect("compras.db")
    cursor = conn.cursor()
    nome_arquivo = f"relatorio_{tipo}.csv"

    # Define consulta conforme tipo
    if tipo == "produto":
        cursor.execute("SELECT produto, local, SUM(valor*quantidade) FROM compras GROUP BY produto, local")
        cabecalho = ['Produto', 'Local', 'Total (R$)']
    elif tipo == "local":
        cursor.execute("SELECT local, strftime('%m', data), SUM(valor*quantidade) FROM compras GROUP BY local, strftime('%m', data)")
        cabecalho = ['Local', 'Mês', 'Total (R$)']
    elif tipo == "data":
        cursor.execute("SELECT data, SUM(valor*quantidade) FROM compras GROUP BY data")
        cabecalho = ['Data', 'Total (R$)']
    elif tipo == "mes":
        cursor.execute("SELECT strftime('%m', data), SUM(valor*quantidade) FROM compras GROUP BY strftime('%m', data)")
        cabecalho = ['Mês', 'Total (R$)']
    elif tipo == "ano":
        cursor.execute("SELECT strftime('%Y', data), SUM(valor*quantidade) FROM compras GROUP BY strftime('%Y', data)")
        cabecalho = ['Ano', 'Total (R$)']
    else:
        return "Tipo inválido", 400

    dados = cursor.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(cabecalho)
    for linha in dados:
        linha_formatada = [f"{x:.2f}".replace('.', ',') if isinstance(x, float) else x for x in linha]
        writer.writerow(linha_formatada)

    with open(nome_arquivo, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(output.getvalue())

    return send_file(nome_arquivo, as_attachment=True, download_name=nome_arquivo)


# CADASTRAR
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    data = request.form.get('data')
    local = request.form.get('local')
    produto = request.form.get('produto')
    quantidade = request.form.get('quantidade')
    valor_str = request.form.get('valor') 

    if not (data and local and produto and quantidade and valor_str):
        flash("⚠️ Todos os campos devem ser preenchidos!")
        # CORREÇÃO 1: Redireciona para /index (Cadastro) se faltar campo
        return redirect('/index') 

    # ------------------------------------------------------------------
    # TRATAMENTO MONETÁRIO
    # ------------------------------------------------------------------
    try:
        # 1. Substitui vírgula (,) por ponto (.) para o formato numérico americano/SQL
        valor_limpo = valor_str.replace(',', '.')
        valor_float = float(valor_limpo) 
        # Converte a quantidade para inteiro
        quantidade_int = int(quantidade)
        
    except ValueError:
        flash("❌ Valor ou Quantidade inválida. Use o formato numérico correto.")
        # CORREÇÃO 2: Redireciona para /index (Cadastro) se o valor for inválido
        return redirect('/index')
    # ------------------------------------------------------------------

    # 1. SALVAR NO BANCO DE DADOS (compras.db)
    conn = sqlite3.connect("compras.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO compras (data, local, produto, quantidade, valor) VALUES (?, ?, ?, ?, ?)",
        (data, local, produto, quantidade_int, valor_float) 
    )
    novo_id = cursor.lastrowid 
    conn.commit()
    conn.close()

    # 2. ADICIONAR À LISTA DE SESSÃO (Para exibição imediata)
    valor_exibicao = f"{valor_float:.2f}".replace('.', ',')
    novo_item = (novo_id, data, local, produto, quantidade_int, valor_exibicao) 
    
    lista_atual = session.get('itens_sessao', [])
    lista_atual.append(novo_item)
    session['itens_sessao'] = lista_atual 

    flash("✅ Item cadastrado com sucesso!")
    
    # CORREÇÃO PRINCIPAL: Redirecionar para /index para permanecer na tela e ver a lista
    return redirect('/index')


# EXCLUIR ITEM
@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    conn = sqlite3.connect("compras.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compras WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    if 'itens_sessao' in session:
        session['itens_sessao'] = [item for item in session['itens_sessao'] if item[0] != id]

    flash("🗑️ Item excluído com sucesso!")
    # CORREÇÃO 3: Redireciona para /index (Cadastro) após excluir
    return redirect('/index')

@app.route('/salvar', methods=['GET'])
def salvar():
    session.pop('itens_sessao', None) 
    flash("💾 Itens cadastrados salvos com sucesso!")
    return redirect('/index')


@app.route('/gerar_csv', methods=['GET'])
def gerar_csv():
    conn = sqlite3.connect("compras.db")
    cursor = conn.cursor()
    # Consulta o banco (onde o valor está em formato numérico para cálculos)
    cursor.execute("SELECT * FROM compras")
    compras = cursor.fetchall()
    conn.close()

    # Formata a saída do CSV para manter a vírgula como separador decimal
    output = StringIO()
    writer = csv.writer(output, delimiter=';') # Use ponto e vírgula como separador do CSV (padrão Brasil)
    
    # Cabeçalho
    writer.writerow(['ID', 'Data', 'Local', 'Produto', 'Quantidade', 'Valor (R$)'])
    
    # Dados: Formata o valor de volta para R$ com vírgula antes de escrever no CSV
    linhas_formatadas = []
    for item in compras:
        # Item: (id, data, local, produto, quantidade, valor_float)
        valor_formatado_br = f"{item[5]:.2f}".replace('.', ',') # item[5] é o valor float
        linhas_formatadas.append((item[0], item[1], item[2], item[3], item[4], valor_formatado_br))
        
    writer.writerows(linhas_formatadas)

    output.seek(0)
    csv_path = "compras.csv"

    # Salva o arquivo CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        f.write(output.getvalue())

    return send_file(csv_path, as_attachment=True, download_name='compras.csv')

# NOVO CÓDIGO: Rota para apagar todos os dados e arquivos
@app.route('/reset')
def reset_data():
    arquivos_para_deletar = [
        'compras.db',
        'compras.csv',
        'relatorio_ano.csv',
        'relatorio_data.csv',
        'relatorio_local.csv',
        'relatorio_mes.csv',
        'relatorio_produto.csv'
    ]
    
    arquivos_deletados = []
    
    for arquivo in arquivos_para_deletar:
        if os.path.exists(arquivo):
            os.remove(arquivo)
            arquivos_deletados.append(arquivo)
            
    # Garante que o banco de dados e a tabela serão recriados ao iniciar a próxima sessão.
    # A função init_db() será chamada no próximo acesso.
    
    # Limpa a sessão atual (a lista que estava na tela)
    session.pop('itens_sessao', None)
    
    if arquivos_deletados:
        flash(f"✅ Reset completo. Arquivos excluídos: {', '.join(arquivos_deletados)}. O banco de dados será recriado no próximo cadastro.")
    else:
        flash("⚠️ Reset completo. Nenhum arquivo de base de dados/relatório foi encontrado para exclusão.")
        
    # Redireciona para a home ou para o cadastro limpo
    return redirect('/')


# -------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)