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
