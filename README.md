# 🔐 Template de Login Microsoft + SharePoint para Streamlit

Template reutilizável para criar aplicações Streamlit com:
- ✅ Autenticação Microsoft Azure AD (login corporativo)
- ✅ Conexão com SharePoint/OneDrive (leitura e escrita de arquivos)

## 📋 Pré-requisitos

- Python 3.8+
- Uma conta no [Azure Portal](https://portal.azure.com)
- Acesso para registrar aplicações no Microsoft Entra ID (antigo Azure AD)

## 🚀 Início Rápido

### 1. Clone ou copie este template

```bash
# Copie a pasta para seu novo projeto
cp -r streamlit-azure-login-template meu-novo-projeto
cd meu-novo-projeto
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais Azure

Execute o script de configuração interativo:

```bash
python configure_azure.py
```

O script irá:
- ✅ Solicitar o nome da sua aplicação no Streamlit Cloud
- ✅ Gerar automaticamente as URIs de redirecionamento (localhost + produção)
- ✅ Solicitar suas credenciais Azure (login)
- ✅ **[NOVO]** Configurar opcionalmente conexão com SharePoint/OneDrive
- ✅ Criar o arquivo `.streamlit/secrets.toml`
- ✅ Atualizar o `.gitignore`

### 4. Execute localmente

```bash
streamlit run app.py
```

---

## 📁 Estrutura do Projeto

```
streamlit-azure-login-template/
├── .streamlit/
│   ├── secrets.toml          # Suas credenciais (NÃO commite!)
│   └── secrets.toml.example  # Template de referência
├── auth_microsoft.py         # Módulo de autenticação
├── sp_connector.py           # [NOVO] Conector SharePoint/OneDrive
├── app.py                    # Aplicação de demonstração
├── configure_azure.py        # Script de configuração
├── requirements.txt          # Dependências
├── .gitignore               # Ignora secrets.toml
└── README.md                # Este arquivo
```

---

## 🔧 Configuração Manual no Azure Portal

### Passo 1: Criar App Registration para LOGIN

1. Acesse [portal.azure.com](https://portal.azure.com)
2. Navegue para **Microsoft Entra ID** > **Registros de aplicativo**
3. Clique em **+ Novo registro**
4. Preencha:
   - **Nome**: Nome da sua aplicação (ex: "Minha App Streamlit - Login")
   - **Tipos de conta suportados**: "Contas somente neste diretório organizacional"
   - **URI de Redirecionamento**: Deixe vazio por enquanto
5. Clique em **Registrar**

### Passo 2: Copiar IDs

Na página de **Visão geral** da aplicação, copie:

| Campo PT-BR | Campo EN | Descrição |
|-------------|----------|-----------| 
| ID do aplicativo (cliente) | Application (client) ID | Seu `client_id` |
| ID do diretório (locatário) | Directory (tenant) ID | Seu `tenant_id` |

### Passo 3: Criar Client Secret

1. No menu lateral, clique em **Certificados e segredos**
2. Clique em **+ Novo segredo do cliente**
3. Adicione uma descrição (ex: "Streamlit App")
4. Escolha a validade (recomendado: 24 meses)
5. Clique em **Adicionar**
6. **⚠️ IMPORTANTE**: Copie o **Valor** imediatamente (não será mostrado novamente!)

### Passo 4: Adicionar URIs de Redirecionamento

1. No menu lateral, clique em **Autenticação**
2. Clique em **+ Adicionar uma plataforma**
3. Selecione **Web**
4. Adicione as URIs:

```
http://localhost:8501
https://seu-app.streamlit.app
```

5. Clique em **Configurar**

> ⚠️ **IMPORTANTE**: Adicione AMBAS as URIs! A primeira é para desenvolvimento local, a segunda para produção.

---

## 📦 Configuração do SharePoint/OneDrive

### ⚠️ IMPORTANTE: Apps Separados

Para acessar arquivos no SharePoint/OneDrive, você precisa de **permissões de aplicativo** (não delegadas). Isso geralmente requer um **App Registration diferente** do de login.

| Funcionalidade | Tipo de Permissão | Escopo |
|----------------|-------------------|--------|
| Login usuário | Delegated | `User.Read` |
| Acesso arquivos | **Application** | `Files.Read.All` ou `Files.ReadWrite.All` |

### Passo 1: Criar App Registration para SHAREPOINT

1. No Azure Portal, crie um **novo App Registration**
2. Nome sugerido: "Minha App - SharePoint Access"
3. Vá em **Permissões de API** > **Adicionar uma permissão**
4. Selecione **Microsoft Graph** > **Permissões de aplicativo**
5. Adicione: `Files.Read.All` (ou `Files.ReadWrite.All` se precisar gravar)
6. **Clique em "Conceder consentimento do administrador"** (Grant admin consent)

### Passo 2: Criar Client Secret

Mesmo processo do App de login (passo 3 acima).

### Estrutura do secrets.toml

```toml
# App para ACESSO AO SHAREPOINT (Files.Read.All)
[graph]
tenant_id = "seu-tenant-id"
client_id = "client-id-do-app-sharepoint"
client_secret = "secret-do-app-sharepoint"

# Para OneDrive de um usuário
user_upn = "usuario@empresa.com"
file_path = "Pasta/arquivo.csv"

# OU para SharePoint Site
# hostname = "empresa.sharepoint.com"
# site_path = "sites/meusite"
# library_name = "Documents"

# App para LOGIN DO USUÁRIO (User.Read)
[auth]
tenant_id = "seu-tenant-id"
client_id = "client-id-do-app-login"
client_secret = "secret-do-app-login"
redirect_uri_local = "http://localhost:8501"
redirect_uri_prod = "https://seu-app.streamlit.app"
scope = ["https://graph.microsoft.com/User.Read"]
```

---

## 📚 Usando o SPConnector

### Leitura de arquivos

```python
import streamlit as st
from sp_connector import SPConnector

# Criar conector usando credenciais do secrets.toml
@st.cache_resource
def get_sp_connector():
    graph_cfg = st.secrets["graph"]
    return SPConnector(
        tenant_id=graph_cfg["tenant_id"],
        client_id=graph_cfg["client_id"],
        client_secret=graph_cfg["client_secret"],
        user_upn=graph_cfg.get("user_upn"),  # Para OneDrive
        # OU para SharePoint:
        # hostname=graph_cfg.get("hostname"),
        # site_path=graph_cfg.get("site_path"),
        # library_name=graph_cfg.get("library_name"),
    )

# Usar o conector
sp = get_sp_connector()

# Ler CSV
df = sp.read_csv("Pasta/arquivo.csv", sep=";", encoding="utf-8-sig")

# Ler Excel
df = sp.read_excel("Pasta/arquivo.xlsx", sheet_name="Planilha1")

# Baixar arquivo genérico
content = sp.download("Pasta/imagem.png")
```

### Escrita de arquivos

```python
# Salvar DataFrame como Excel
sp.write_excel(df, "Pasta/relatorio.xlsx", overwrite=True)

# Upload de arquivo genérico
with open("local_file.pdf", "rb") as f:
    sp.upload_small("Pasta/arquivo.pdf", f.read())
```

### OneDrive vs SharePoint

```python
# OneDrive (pasta Documents de um usuário)
sp = SPConnector(
    tenant_id="...",
    client_id="...",
    client_secret="...",
    user_upn="usuario@empresa.com"  # Email do dono do OneDrive
)
df = sp.read_csv("Pasta/arquivo.csv")  # Relativo a Documents/

# SharePoint Site
sp = SPConnector(
    tenant_id="...",
    client_id="...",
    client_secret="...",
    hostname="empresa.sharepoint.com",
    site_path="sites/meusite",
    library_name="Documents"
)
df = sp.read_csv("Pasta/arquivo.csv")  # Relativo à biblioteca
```

---

## 🎨 Personalizando a Página de Login

Edite o dicionário `LOGIN_CONFIG` no arquivo `app.py`:

```python
LOGIN_CONFIG.update({
    "title": "Minha Aplicação",
    "subtitle": "Sistema de gestão corporativa",
    "badge_text": "Acesso Restrito Synvia",
    "email_domain": "@synvia.com",
    "highlights": [
        {
            "icon": "📊",
            "title": "Dashboards",
            "description": "Visualize métricas em tempo real"
        },
        # ... adicione mais itens
    ]
})
```

Para mudar as cores, edite as constantes no início de `auth_microsoft.py`:

```python
PRIMARY_COLOR = "#6BBF47"    # Verde principal
SECONDARY_COLOR = "#52B54B"  # Verde secundário
ACCENT_DARK = "#0F1C16"      # Cor escura
MUTED_TEXT = "#5B6770"       # Cor do texto secundário
```

---

## ☁️ Deploy no Streamlit Cloud

### 1. Prepare o repositório

Certifique-se de que `.streamlit/secrets.toml` está no `.gitignore`:

```bash
cat .gitignore
# Deve conter:
# .streamlit/secrets.toml
```

### 2. Faça push do código

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 3. Configure no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **New app**
3. Selecione seu repositório
4. Após deploy, vá em **Settings** > **Secrets**
5. Cole o conteúdo do seu `secrets.toml`
6. Clique em **Save**

---

## 🔍 Troubleshooting

### Erro: "redirect_uri_mismatch"

A URI de redirecionamento não está cadastrada no Azure. Verifique:
1. Se AMBAS as URIs estão cadastradas (localhost e produção)
2. Se a URI está exatamente igual (sem barras extras no final)

### Erro: "invalid_client"

O Client Secret está incorreto ou expirou. Crie um novo segredo no Azure Portal.

### Erro: "AADSTS50011"

A URI de resposta não corresponde. Execute `python configure_azure.py` novamente e verifique as URIs geradas.

### Erro: "401 Unauthorized" no SharePoint

O App não tem permissão para acessar arquivos. Verifique:
1. Se o App tem a permissão `Files.Read.All` (Application, não Delegated)
2. Se foi concedido "Admin consent" para essa permissão
3. Se está usando as credenciais corretas (seção `[graph]`, não `[auth]`)

### Erro: "FileNotFoundError" no SharePoint

O caminho do arquivo está incorreto. Lembre-se:
- **OneDrive**: Caminho relativo a `Documents/` (não incluir "Documents" no path)
- **SharePoint**: Caminho relativo à biblioteca

---

## 📞 Suporte

- **Documentação MSAL**: [msal-python.readthedocs.io](https://msal-python.readthedocs.io)
- **Microsoft Entra ID**: [docs.microsoft.com/azure/active-directory](https://docs.microsoft.com/azure/active-directory/)
- **Microsoft Graph API**: [docs.microsoft.com/graph](https://docs.microsoft.com/graph/)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)

---

Desenvolvido com ❤️ para a Synvia
