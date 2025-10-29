document.addEventListener("DOMContentLoaded", carregarCompras);

function carregarCompras() {
  fetch("/listar")
    .then(res => res.json())
    .then(dados => {
      const tbody = document.querySelector("#tabelaCompras tbody");
      tbody.innerHTML = "";
      dados.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${item[0]}</td>
          <td>${item[1]}</td>
          <td>${item[2]}</td>
          <td>${item[3]}</td>
          <td>${item[4]}</td>
          <td>${item[5].toFixed(2)}</td>
          <td><button onclick="deletar(${item[0]})">Excluir</button></td>
        `;
        tbody.appendChild(tr);
      });
    });
}

function deletar(id) {
  fetch(`/deletar/${id}`, { method: "DELETE" })
    .then(() => carregarCompras());
}

function exportarCSV() {
  window.location.href = "/exportar";
}


// ---- Relatórios ----

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

// ----------- PRODUTOS -------------------

// Aguarda o carregamento completo da página
document.addEventListener("DOMContentLoaded", () => {
  carregarProdutos();

  const btnAdd = document.getElementById("btnAdicionarProduto");
  if (btnAdd) {
    btnAdd.addEventListener("click", adicionarProduto);
  }
});

// Função para listar produtos existentes
function carregarProdutos() {
  fetch("/listar_produtos")
    .then(res => res.json())
    .then(produtos => {
      const select = document.getElementById("produto");
      select.innerHTML = "";
      produtos.forEach(prod => {
        const option = document.createElement("option");
        option.value = prod;
        option.textContent = prod;
        select.appendChild(option);
      });
    })
    .catch(err => console.error("Erro ao carregar produtos:", err));
}

// Função para adicionar um novo produto
function adicionarProduto() {
  const novoProduto = prompt("Digite o nome do novo produto:");
  if (novoProduto && novoProduto.trim() !== "") {
    fetch("/adicionar_produto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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

// FUNÇÃO CONFIRMAR RESET

function confirmarReset(){
  return confirm ("⚠️ Tem certeza que deseja apagar todos os dados e relatórios?");
}