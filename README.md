# 🛒 Sistema de Controle de Compras

Aplicação web desenvolvida com Flask (Python) para cadastro e gerenciamento de compras, com geração de relatórios dinâmicos e exportação de dados em CSV.

Permite registrar produtos, locais, datas, valores e quantidades. **Hospedado na nuvem (Render)** com persistência de dados utilizando **PostgreSQL**.

## 📂 Estrutura do Projeto
/cadastro_compras/
│
├── app.py                  ← Código principal Flask
├── requirements.txt        ← Dependências para o Python
├── .env                    ← Variáveis de ambiente (uso LOCAL - **Ignorado pelo Git**)
│
├── /templates/             ← Páginas HTML
│   ├── home.html           ← Tela inicial (menu principal)
│   ├── index.html          ← Tela de cadastro de compras
│   └── relatorio.html      ← Tela de relatórios
│
└── /static/                ← Arquivos estáticos
    ├── style.css           ← Estilos da interface
    └── script.js           ← Funções JavaScript (sessão e interatividade)

## 🚀 Funcionalidades Principais

✅ **Cadastro de Compras (index.html)**
* Registro de data, local, produto, quantidade e valor (R$).
* **Nova Lógica de Sessão:** Permite limpar a lista de "Itens Cadastrados" na tela sem apagar os dados no banco (botão "Limpar Itens na Tela"). A lista de cadastro é independente dos dados salvos.
* Visualização imediata dos itens **recém-cadastrados na sessão atual**.
* Botão "Ver Todos os Itens Salvos" para carregar o histórico completo.
* Possibilidade de excluir itens diretamente da tabela.
* Exportação de todos os dados em arquivo CSV.

✅ **Relatórios (relatorio.html)**
* Relatórios agrupados por: Produto, Local, Data, Mês, Ano.
* Geração de CSV específico por tipo de relatório.
* Visualização dinâmica via AJAX (sem recarregar a página).

✅ **Gerenciamento de Dados**
* Função `/reset` permite excluir **todos** os dados do banco, recriando as tabelas limpas.

---

## ⚙️ Instalação e Execução (Desenvolvimento Local)

Esta aplicação utiliza **PostgreSQL** e requer a configuração de credenciais no ambiente local para rodar.

#### **Pré-requisitos:**
* Python 3.10+
* PostgreSQL (servidor local)

🔹 1. **Clonar o repositório**
```bash
git clone [https://docs.github.com/pt/repositories/creating-and-managing-repositories/about-repositories](https://docs.github.com/pt/repositories/creating-and-managing-repositories/about-repositories)
cd cadastro_compras

🔹 2. Criar e Ativar ambiente virtual

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

🔹 3. Instalar dependências
pip install -r requirements.txt

🔹 4. Configurar o Banco de Dados Crie um arquivo chamado .env (adicionado ao .gitignore) na raiz do projeto e configure a URL de conexão:
DATABASE_URL="[SUA URL DE CONEXÃO POSTGRESQL]"

Recomendado criar uma instância de PostgreSQL para desenvolvimento local.

🔹 5. Executar o projeto
python app.py

O servidor Flask iniciará em: http://127.0.0.1:5000

🌐 Tecnologias Utilizadas (Produção)
| Tecnologia           | Função                                  |
-----------------------|_----------------------------------------|       
| Python 3             | Linguagem principal                     |
| Flask/Gunicorn       | Framework web e servidor de produção    |
| Flask-SQLAlchemyORM  | ORM para interagir com o DB             |
| PostgreSQL (Render)  | Banco de dados de produção              |
| Render               | Serviço de hospedagem e deploy contínuo |
| HTML5/CSS3/JS        | Interface e interatividade              |
| CSV (módulo nativo)  | Exportação de relatórios                |

💾 Banco de Dados
A tabela principal é a Compra:

compras (
    id SERIAL PRIMARY KEY,
    data TEXT,
    local TEXT,
    produto TEXT,
    quantidade INTEGER,
    valor REAL
)

👨‍💻 Autor

Jovanio Oliveira
📧 jojo.vanio@gmail.com
💼 Projeto desenvolvido para estudo e prática de Flask + PostgreSQL e deploy em nuvem (Render)..
