🛒 Sistema de Controle de Compras

Aplicação web desenvolvida com Flask (Python) para cadastro e gerenciamento de compras, com geração de relatórios dinâmicos e exportação de dados em CSV.
Permite registrar produtos, locais, datas, valores e quantidades, além de visualizar relatórios organizados por produto, local, data, mês e ano.

📂 Estrutura do Projeto
/cadastro_compras/
│
├── app.py                  ← Código principal Flask
├── compras.db              ← Banco de dados SQLite (gerado automaticamente)
│
├── /templates/             ← Páginas HTML
│   ├── home.html           ← Tela inicial (menu principal)
│   ├── index.html          ← Tela de cadastro de compras
│   └── relatorio.html      ← Tela de relatórios
│
└── /static/                ← Arquivos estáticos
    ├── style.css           ← Estilos da interface
    └── script.js           ← Funções JavaScript (relatórios)

🚀 Funcionalidades Principais

✅ Tela Inicial (home.html)

Acesso rápido ao cadastro de compras e aos relatórios.

Interface simples e intuitiva.

✅ Cadastro de Compras (index.html)

Registro de data, local, produto, quantidade e valor (R$).

Armazenamento automático no banco de dados SQLite.

Visualização imediata dos itens cadastrados.

Possibilidade de excluir itens diretamente da tabela.

Exportação de todos os dados em arquivo CSV.

✅ Relatórios (relatorio.html)

Relatórios agrupados por:

Produto

Local

Data

Mês

Ano

Geração de CSV específico por tipo de relatório.

Visualização dinâmica via AJAX (sem recarregar a página).

✅ Gerenciamento de Dados

Função /reset permite excluir todos os arquivos de dados e relatórios, recriando o banco limpo.

Sessão controlada por Flask.session com limpeza automática ao reiniciar o cadastro.

| Tecnologia              | Função                     |
| ----------------------- | -------------------------- |
| **Python 3**            | Linguagem principal        |
| **Flask**               | Framework web              |
| **SQLite3**             | Banco de dados local       |
| **HTML5 / CSS3 / JS**   | Interface e interatividade |
| **Jinja2**              | Templates dinâmicos        |
| **CSV (módulo nativo)** | Exportação de relatórios   |

⚙️ Instalação e Execução
🔹 1. Clonar o repositório
git clone https://github.com/seuusuario/cadastro_compras.git
cd cadastro_compras

🔹 2. Criar ambiente virtual (opcional, mas recomendado)
python -m venv venv
venv\Scripts\activate       # (Windows)
# ou
source venv/bin/activate    # (Linux/Mac)

🔹 3. Instalar dependências
pip install flask

🔹 4. Executar o projeto
python app.py


O servidor Flask iniciará em:
http://127.0.0.1:5000

💾 Banco de Dados

O arquivo compras.db é criado automaticamente ao iniciar o app.

Tabela principal:

compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    local TEXT,
    produto TEXT,
    quantidade INTEGER,
    valor REAL
)
📊 Relatórios CSV

Ao clicar em Gerar CSV, são criados arquivos como:

compras.csv

relatorio_produto.csv

relatorio_local.csv

relatorio_data.csv

relatorio_mes.csv

relatorio_ano.csv

Os valores são formatados no padrão brasileiro (vírgula como separador decimal) e usam “;” como delimitador.

🧹 Função de Reset

Rota:

/reset

👉 Exclui todos os arquivos de base e relatórios gerados:

compras.db, compras.csv, relatorio_ano.csv, relatorio_data.csv,
relatorio_local.csv, relatorio_mes.csv, relatorio_produto.csv

Após o reset, o banco será recriado automaticamente no próximo acesso.

🧱 Estrutura de Pastas Internas
/templates/
│   home.html        → Tela inicial
│   index.html       → Cadastro e listagem de compras
│   relatorio.html   → Geração e visualização de relatórios

/static/
│   style.css        → Estilos (layout responsivo e moderno)
│   script.js        → Lógica de relatórios em JavaScript

compras.db            → Banco SQLite (criado automaticamente)
app.py                → Código principal Flask

🎨 Interface
🏠 Tela Inicial

Escolha entre “Cadastro de Compras” ou “Relatórios”.

🧾 Tela de Cadastro

Insira e visualize as compras registradas.

Botões: Salvar, Gerar CSV, Sair.

📈 Tela de Relatórios

Relatórios dinâmicos agrupados por produto, local, data, mês e ano.

Exportação direta em CSV.

💡 Melhorias Futuras

Implementar edição de registros.

Adicionar autenticação de usuários.

Inserir gráficos interativos nos relatórios.

Suporte a exportação PDF.

👨‍💻 Autor

Jovanio Oliveira
📧 jojo.vanio@gmail.com
💼 Projeto desenvolvido para estudo e prática de Flask + SQLite + Front-End integrado.
