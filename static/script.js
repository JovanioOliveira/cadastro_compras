document.addEventListener("DOMContentLoaded", () => {
    
    // A tabela começa vazia e o carregamento não é automático aqui
    carregarProdutos();

    const btnAdd = document.getElementById("btnAdicionarProduto");
    if (btnAdd) {
        btnAdd.addEventListener("click", adicionarProduto);
    }

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", event => {
            event.preventDefault();
            
            const formData = new FormData(form);
            const dados = Object.fromEntries(formData.entries());
            
            dados.valor = parseFloat(dados.valor);
            dados.quantidade = parseInt(dados.quantidade);

            fetch("/cadastrar", {
                method: "POST",
                headers: { "Content-Type": "application/json; charset=utf-8" }, 
                body: JSON.stringify(dados)
            })
                .then(res => {
                    if (res.ok) {
                        // Fazemos uma nova requisição para obter o item recém-cadastrado
                        // O Flask não retorna o ID, então buscamos a lista e pegamos o último (solução simplificada)
                        return fetch("/listar_compras");
                    } else {
                        // Trata erros de validação retornados pelo Flask
                        return res.json().then(err => {
                            alert(`Erro ao cadastrar compra: ${err.erro || res.statusText}`);
                            throw new Error('Erro de cadastro');
                        });
                    }
                })
                .then(res => res.json())
                .then(dadosCompletos => {
                    if (dadosCompletos && dadosCompletos.length > 0) {
                        const novoItem = dadosCompletos[dadosCompletos.length - 1];
                        
                        // 🌟 CORREÇÃO: Usamos a nova função para adicionar apenas o item novo
                        adicionarItemNaTabela(novoItem);
                        
                        // Limpa o formulário após o sucesso
                        form.reset(); 
                    }
                })
                .catch(err => console.error("Erro ao cadastrar:", err));
        });
    }

});

// ---- FUNÇÃO DE POPULAR TABELA ----

/**
 * Função utilitária para adicionar um item à tabela.
 * @param {Array} item - Array contendo os dados do item (id, data, local, produto, qtd, valor).
 * @param {boolean} limparTabela - Se deve limpar a tabela antes de adicionar. Usado em carregarTodasCompras.
 */
function adicionarItemNaTabela(item, limparTabela = false) {
    const tbody = document.querySelector("#tabelaCompras tbody");
    
    // Se for para limpar (usado apenas em carregarTodasCompras)
    if (limparTabela) {
        tbody.innerHTML = "";
    }

    const tr = document.createElement("tr");
    // item[0]=id, item[1]=data, item[2]=local, item[3]=produto, item[4]=quantidade, item[5]=valor
    tr.innerHTML = `
        <td>${item[0]}</td>
        <td>${item[1]}</td>
        <td>${item[2]}</td>
        <td>${item[3]}</td>
        <td>${item[4]}</td>
        <td>${item[5] ? item[5].toFixed(2) : '0.00'}</td>
        <td><button onclick="deletar(${item[0]})">Excluir</button></td>
    `;
    tbody.appendChild(tr);
}

// ---- FUNÇÕES DE VISUALIZAÇÃO E LIMPEZA ----

/**
 * Funçao que carrega TODOS os dados do banco e popula a tabela.
 * Chamada apenas pelo botão 'Ver Todos os Itens Salvos'.
 */
function carregarTodasCompras() {
    fetch("/listar_compras")
        .then(res => res.json())
        .then(dados => {
            const tbody = document.querySelector("#tabelaCompras tbody");
            tbody.innerHTML = ""; // Limpa antes de carregar todos
            dados.forEach(item => {
                // Chama a função utilitária com limparTabela=false (já limpamos acima)
                adicionarItemNaTabela(item); 
            });
            alert("✅ Todos os itens salvos no banco de dados foram carregados na tabela.");
        })
        .catch(err => console.error("Erro ao carregar compras:", err));
}

/**
 * Apenas limpa o conteúdo da tabela na tela.
 */
function limparTabelaNaTela() {
    const tbody = document.querySelector("#tabelaCompras tbody");
    tbody.innerHTML = "";
    alert("✅ Tabela de itens cadastrados na tela foi limpa. Os dados continuam salvos no banco de dados.");
}

function deletar(id) {
    if (!confirm("Tem certeza que deseja excluir este item?")) {
        return;
    }
    fetch(`/deletar/${id}`, { method: "DELETE" }) 
        .then(res => {
            if (res.ok) {
                // Após deletar, carregamos todos os itens novamente para atualizar a lista
                carregarTodasCompras(); 
            } else {
                alert("Erro ao excluir item.");
            }
        })
        .catch(err => console.error("Erro ao deletar:", err));
}

// ❌ REMOVIDA: A função carregarCompras() anterior foi renomeada para carregarTodasCompras() 
// e não é mais chamada automaticamente no início.

// ---- RELATÓRIOS (Mantido) ----

function gerarRelatorio(tipo) {
    fetch(`/relatorio_dados/${tipo}`)
        .then(res => res.json())
        .then(dados => {
            const div = document.getElementById("resultado-relatorio");
            div.innerHTML = `
                <h3>Resumo: ${tipo.toUpperCase()}</h3>
                <table border="1" style="width:100%; text-align:center; border-collapse:collapse;">
                    <thead>
                        <tr>${Object.keys(dados[0] || {}).map(k => `<th>${k}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${dados.map(linha => `<tr>${Object.values(linha).map(v => `<td>${v}</td>`).join('')}</tr>`).join('')}
                    </tbody>
                </table>
                <div class="botoes">
                    <button onclick="gerarCSV('${tipo}')">Gerar CSV</button>
                    <button onclick="limparRelatorio()">Sair</button>
                </div>
            `;
        });
}

function gerarCSV(tipo) {
    window.location.href = `/gerar_csv_tipo/${tipo}`;
}

function limparRelatorio() {
    document.getElementById("resultado-relatorio").innerHTML = "";
}

// ---- PRODUTOS (Mantido) ----

function carregarProdutos() {
    fetch("/listar_produtos")
        .then(res => res.json())
        .then(produtos => {
            const select = document.getElementById("produto");
            if (select) {
                select.innerHTML = "";
                produtos.forEach(prod => {
                    const option = document.createElement("option");
                    option.value = prod;
                    option.textContent = prod;
                    select.appendChild(option);
                });
            }
        })
        .catch(err => console.error("Erro ao carregar produtos:", err));
}

function adicionarProduto() {
    const novoProduto = prompt("Digite o nome do novo produto:");
    if (novoProduto && novoProduto.trim() !== "") {
        fetch("/adicionar_produto", {
            method: "POST",
            headers: { "Content-Type": "application/json; charset=utf-8" },
            body: JSON.stringify({ produto: novoProduto.trim() })
        })
            .then(res => {
                if (res.ok) {
                    alert("Produto adicionado com sucesso!");
                    carregarProdutos();
                } else {
                    alert("Erro ao adicionar produto!");
                }
            })
            .catch(err => console.error("Erro ao adicionar produto:", err));
    }
}

// ---- CONFIRMAR RESET (Mantido) ----

function confirmarReset() {
    return confirm("⚠️ Tem certeza que deseja apagar todos os dados e relatórios?");
}