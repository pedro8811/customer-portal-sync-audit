# customer-portal-sync-audit (Portal vs CRM) 

Uma aplicação simples em Python puro (sem frameworks) que compara usuários de uma base CSV (Portal) e uma base JSON (CRM) através do e-mail, gerando um relatório de divergências. 

## 🚀 Como Executar 

### 1. Pré-requisitos * Ter o **Docker** e o **Docker Compose** instalados na máquina. 

### 2. Preparar os Dados Certifique-se de que os seus arquivos de dados estão na pasta `data/` na raiz do projeto: * `data/portal.csv` * `data/crm.json` 

### 3. Subir a Aplicação Abra o terminal na raiz do projeto e execute: docker compose up --build
