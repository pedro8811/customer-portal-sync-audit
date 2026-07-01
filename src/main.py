import csv
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# caminho das pastas dos arquivos a serem analisados
PORTAL_PATH = '/app/data/portal.csv'
CRM_PATH = '/app/data/crm.json'

# função que acha e carrega os arquivos, retornando em dictionary
def carregar_dados():
    portal_users = {}
    crm_users = {}

    try: # garante que caminho existe
        with open(PORTAL_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # transforma cada linha em dict
            for row in reader:
                portal_users[row['email'].strip().lower()] = row
    # pesquisei um except que mais se encaixa
    except FileNotFoundError:
        print("Erro ao encontrar arquivo")
    except Exception as e:
        print(f"Erro inesperado ao ler o CSV: {e}")

    try: # garante que caminho existe
        with open(CRM_PATH, mode='r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # transforma cada objeto json da lista em dict
                for item in data:
                    crm_users[item['email'].strip().lower()] = item
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo JSON.")
    # pesquisei um except que mais se encaixa
    except FileNotFoundError:
        print("Erro ao encontrar arquivo")
    except Exception as e:
        print(f"Erro inesperado ao ler o CSV: {e}")
    
    return portal_users, crm_users

# função que pega os dados gerados e filtra para o relatório
def gerar_relatorio():
    portal, crm = carregar_dados()

    # para fazer a filtragem, é criado uma lista com as chaves (emails) de cada dictionary criado (dict.keys())
    emails_portal = set(portal.keys())
    emails_crm = set(crm.keys())
    
    apenas_portal = []
    # emails_portal - emails_crm faz com que apenas os registros que estão no portal e não estão no crm sejam filtrados
    for email in (emails_portal - emails_crm):
        # adiciona os campos na nova lista filtrada
        apenas_portal.append({
            "email": email,
            "name": portal[email].get('name') or portal[email].get('nome', 'Sem Nome'),
            "status": portal[email].get('status', 'Não informado')
        })

    # emails_crm - emails_portal faz com que apenas os registros que estão no crm e não estão no portal sejam filtrados
    apenas_crm = []
    for email in (emails_crm - emails_portal):
        # diciona os campos na nova lista filtrada
        apenas_crm.append({
            "email": email,
            "name": crm[email].get('name') or crm[email].get('nome', 'Sem Nome'),
            "status": crm[email].get('status', 'Não informado')
        })

    # filtra emails de ambas as lista removendo os repetidos
    ambos_emails = emails_portal.intersection(emails_crm)
    # nova lista para filtrar usuarios que estão em ambos porém com status diferente
    status_diferente = []
    
    for email in ambos_emails:
        # pega o status em cada lista atraves do valor do email
        status_portal = portal[email].get('status', 'Não informado')
        status_crm = crm[email].get('status', 'Não informado')

        # verifica se é diferete e adiciona os 2
        if status_portal != status_crm:
            status_diferente.append({
                "email": email,
                "nome_portal": portal[email].get('name') or portal[email].get('nome', 'Sem Nome'),
                "status_portal": status_portal,
                "status_crm": status_crm
            })

    return {
        "apenas_no_portal": apenas_portal,
        "apenas_no_crm": apenas_crm,
        "status_divergente": status_diferente
    }

def gerar_html(relatorio):
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Comparação Base de Dados</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }
            h1 { color: #2c3e50; }
            h2 { color: #2980b9; margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background: #fff; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #34495e; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .empty { color: #7f8c8d; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>Relatório de Comparação: Portal vs CRM</h1>
    """

    html += "<h2>1. Usuários que existem no Portal, mas NÃO existem no CRM</h2>"
    if relatorio["apenas_no_portal"]:
        html += "<table><tr><th>Nome</th><th>Email</th><th>Status Portal</th></tr>"
        for u in relatorio["apenas_no_portal"]:
            html += f"<tr><td>{u['name']}</td><td>{u['email']}</td><td>{u['status']}</td></tr>"
        html += "</table>"
    else:
        html += "<p class='empty'>Nenhum registro encontrado.</p>"

    html += "<h2>2. Clientes que existem no CRM, mas NÃO existem no Portal</h2>"
    if relatorio["apenas_no_crm"]:
        html += "<table><tr><th>Nome</th><th>Email</th><th>Status CRM</th></tr>"
        for u in relatorio["apenas_no_crm"]:
            html += f"<tr><td>{u['name']}</td><td>{u['email']}</td><td>{u['status']}</td></tr>"
        html += "</table>"
    else:
        html += "<p class='empty'>Nenhum registro encontrado.</p>"

    html += "<h2>3. Usuários em ambos os sistemas com STATUS diferente</h2>"
    if relatorio["status_divergente"]:
        html += "<table><tr><th>Email</th><th>Nome Portal</th><th>Status Portal</th><th>Status CRM</th></tr>"
        for u in relatorio["status_divergente"]:
            html += f"<tr><td>{u['email']}</td><td>{u['nome_portal']}</td><td>{u['status_portal']}</td><td>{u['status_crm']}</td></tr>"
        html += "</table>"
    else:
        html += "<p class='empty'>Nenhum registro encontrado.</p>"

    html += "</body></html>"
    return html

class RelatorioRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        relatorio = gerar_relatorio()

        # criação das rotas para consulta

        if self.path == '/api/relatorio':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(relatorio, indent=2).encode('utf-8'))
        
        elif self.path == '/' or self.path == '/relatorio':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html_content = gerar_html(relatorio)
            self.wfile.write(html_content.encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Pagina nao encontrada")

def run(server_class=HTTPServer, handler_class=RelatorioRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor rodando na porta {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()