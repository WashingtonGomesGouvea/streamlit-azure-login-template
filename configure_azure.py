#!/usr/bin/env python3
"""
Script de Configuração Azure AD para Login Microsoft + SharePoint

Execute: python configure_azure.py

Este script:
1. Solicita as credenciais do Azure (Client ID, Client Secret, Tenant ID)
2. Solicita o nome da aplicação no Streamlit Cloud
3. Gera automaticamente as URIs de redirecionamento (localhost + produção)
4. Configura opcionalmente a conexão com SharePoint/OneDrive
5. Cria/atualiza o arquivo .streamlit/secrets.toml
"""

import os
import sys
from pathlib import Path


def print_header():
    """Exibe cabeçalho do script"""
    print("\n" + "=" * 70)
    print("🔐 CONFIGURADOR DE LOGIN MICROSOFT AZURE + SHAREPOINT")
    print("   Template de Autenticação para Streamlit")
    print("=" * 70 + "\n")


def print_uris(app_name: str):
    """Exibe as URIs de redirecionamento formatadas"""
    local_uri = "http://localhost:8501"
    prod_uri = f"https://{app_name}.streamlit.app"
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║  📋 URIs de Redirecionamento para Azure                            ║")
    print("╠" + "═" * 68 + "╣")
    print(f"║  🏠 Local:     {local_uri:<52} ║")
    print(f"║  🌐 Produção:  {prod_uri:<52} ║")
    print("╚" + "═" * 68 + "╝")
    
    print("\n" + "─" * 70)
    print("📝 COPIE E COLE NO AZURE PORTAL:")
    print("─" * 70)
    print(f"\n{local_uri}")
    print(f"{prod_uri}\n")
    print("─" * 70)
    
    return local_uri, prod_uri


def print_azure_instructions():
    """Exibe instruções de configuração no Azure Portal"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║  📌 COMO ADICIONAR AS URIs NO AZURE PORTAL                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. Acesse: https://portal.azure.com                                 ║
║                                                                      ║
║  2. Navegue até:                                                     ║
║     🇧🇷 PT: Microsoft Entra ID > Registros de aplicativo            ║
║     🇺🇸 EN: Microsoft Entra ID > App registrations                  ║
║                                                                      ║
║  3. Selecione sua aplicação                                          ║
║                                                                      ║
║  4. No menu lateral, clique em:                                      ║
║     🇧🇷 PT: Autenticação                                             ║
║     🇺🇸 EN: Authentication                                          ║
║                                                                      ║
║  5. Em "URIs de Redirecionamento" / "Redirect URIs":                 ║
║     - Clique em "Adicionar uma plataforma" / "Add a platform"        ║
║     - Selecione "Web"                                                ║
║     - Cole CADA URI em uma linha separada                            ║
║     - Clique em "Configurar" / "Configure"                           ║
║                                                                      ║
║  ⚠️  IMPORTANTE: Adicione AMBAS as URIs (localhost E produção)!     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")


def print_sharepoint_info():
    """Exibe informações sobre configuração do SharePoint"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║  📁 CONFIGURAÇÃO DE ACESSO AO SHAREPOINT/ONEDRIVE                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ⚠️  IMPORTANTE: Para acessar arquivos no SharePoint/OneDrive,      ║
║     você precisa de um App Registration DIFERENTE do login!         ║
║                                                                      ║
║  O App de LOGIN usa:                                                 ║
║     - Permissão DELEGADA: User.Read                                  ║
║                                                                      ║
║  O App de SHAREPOINT precisa:                                        ║
║     - Permissão de APLICATIVO: Files.Read.All                        ║
║     - Consentimento do administrador (Grant admin consent)           ║
║                                                                      ║
║  COMO CONFIGURAR:                                                    ║
║  1. Crie um NOVO App Registration (ou use um existente com perm.)    ║
║  2. Vá em "Permissões de API" / "API permissions"                    ║
║  3. Adicionar permissão > Microsoft Graph > Application permissions  ║
║  4. Selecione "Files.Read.All" (ou ReadWrite.All se precisar gravar) ║
║  5. Clique em "Conceder consentimento admin" / "Grant admin consent" ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")


def get_input(prompt: str, required: bool = True, default: str = None) -> str:
    """Solicita entrada do usuário"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        value = input(prompt).strip()
        
        if not value and default:
            return default
        
        if value or not required:
            return value
        
        print("❌ Este campo é obrigatório. Tente novamente.")


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Solicita resposta sim/não do usuário"""
    default_str = "S/n" if default else "s/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['s', 'sim', 'y', 'yes']


def create_secrets_file(config: dict):
    """Cria o arquivo secrets.toml"""
    
    # Criar diretório .streamlit se não existir
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    secrets_path = streamlit_dir / "secrets.toml"
    
    # Verificar se já existe
    if secrets_path.exists():
        overwrite = input("\n⚠️  O arquivo secrets.toml já existe. Sobrescrever? [s/N]: ").strip().lower()
        if overwrite not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada.")
            return False
    
    # Construir conteúdo do arquivo
    content = f'''# Configuração Azure AD - Gerado por configure_azure.py
# ⚠️ NUNCA COMMITE ESTE ARQUIVO NO GIT!

'''
    
    # Seção [graph] para SharePoint (se configurado)
    if config.get('sharepoint_enabled'):
        content += f'''# ============================================================================
# [graph] - Credenciais para ACESSO AO SHAREPOINT/ONEDRIVE
# Este App precisa ter permissão "Files.Read.All" (Application permission)
# ============================================================================
[graph]
tenant_id = "{config['graph_tenant_id']}"
client_id = "{config['graph_client_id']}"
client_secret = "{config['graph_client_secret']}"

'''
        if config.get('sharepoint_mode') == 'onedrive':
            content += f'''# OneDrive do usuário
user_upn = "{config['user_upn']}"
file_path = "{config['file_path']}"

'''
        else:
            content += f'''# SharePoint Site
hostname = "{config['hostname']}"
site_path = "{config['site_path']}"
library_name = "{config['library_name']}"
file_path = "{config['file_path']}"

'''
    
    # Seção [auth] para login
    content += f'''# ============================================================================
# [auth] - Credenciais para LOGIN DO USUÁRIO
# Este App usa permissão "User.Read" (Delegated permission)
# ============================================================================
[auth]
tenant_id = "{config['auth_tenant_id']}"
client_id = "{config['auth_client_id']}"
client_secret = "{config['auth_client_secret']}"

# URIs de redirecionamento (devem estar cadastradas no Azure Portal!)
redirect_uri_local = "{config['local_uri']}"
redirect_uri_prod = "{config['prod_uri']}"

# Escopo Microsoft Graph
scope = ["https://graph.microsoft.com/User.Read"]
'''
    
    # Escrever arquivo
    secrets_path.write_text(content, encoding='utf-8')
    
    print(f"\n✅ Arquivo criado: {secrets_path.absolute()}")
    return True


def update_gitignore():
    """Adiciona secrets.toml ao .gitignore se não estiver"""
    gitignore_path = Path(".gitignore")
    secret_entry = ".streamlit/secrets.toml"
    
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding='utf-8')
        if secret_entry not in content:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write(f"\n# Secrets do Streamlit\n{secret_entry}\n")
            print(f"✅ Adicionado {secret_entry} ao .gitignore")
    else:
        gitignore_path.write_text(f"# Secrets do Streamlit\n{secret_entry}\n", encoding='utf-8')
        print(f"✅ Criado .gitignore com {secret_entry}")


def main():
    """Função principal"""
    print_header()
    
    config = {}
    
    # ========== PASSO 1: Informações da Aplicação ==========
    print("📋 PASSO 1: Informações da Aplicação\n")
    
    print("📝 Digite o nome da sua aplicação no Streamlit Cloud.")
    print("   Exemplo: se sua URL for https://meu-app.streamlit.app")
    print("   Digite apenas: meu-app\n")
    
    app_name = get_input("Nome da aplicação (sem .streamlit.app)")
    app_name = app_name.replace(".streamlit.app", "").replace("https://", "").replace("http://", "").strip("/")
    
    config['local_uri'], config['prod_uri'] = print_uris(app_name)
    
    print_azure_instructions()
    input("Pressione ENTER após adicionar as URIs no Azure Portal...")
    
    # ========== PASSO 2: Credenciais de Login ==========
    print("\n" + "=" * 70)
    print("📋 PASSO 2: Credenciais do Azure para LOGIN")
    print("=" * 70 + "\n")
    
    print("🔐 Onde encontrar as credenciais:")
    print("   Azure Portal > Microsoft Entra ID > Registros de aplicativo")
    print("   > [Sua App de Login] > Visão geral (Overview)\n")
    
    config['auth_tenant_id'] = get_input("Tenant ID (ID do Diretório)")
    config['auth_client_id'] = get_input("Client ID (ID do Aplicativo)")
    
    print("\n🔑 O Client Secret é encontrado em:")
    print("   [Sua App] > Certificados e segredos > Segredos do cliente\n")
    
    config['auth_client_secret'] = get_input("Client Secret (Valor do segredo)")
    
    # ========== PASSO 3: SharePoint (Opcional) ==========
    print("\n" + "=" * 70)
    print("📋 PASSO 3: Conexão com SharePoint/OneDrive (Opcional)")
    print("=" * 70 + "\n")
    
    config['sharepoint_enabled'] = get_yes_no("Deseja configurar acesso ao SharePoint/OneDrive?", default=False)
    
    if config['sharepoint_enabled']:
        print_sharepoint_info()
        input("Pressione ENTER após configurar as permissões no Azure...")
        
        print("\n🔐 Credenciais do App com permissão Files.Read.All:")
        print("   (Pode ser um App diferente do de login!)\n")
        
        use_same = get_yes_no("Usar as mesmas credenciais do login?", default=False)
        
        if use_same:
            config['graph_tenant_id'] = config['auth_tenant_id']
            config['graph_client_id'] = config['auth_client_id']
            config['graph_client_secret'] = config['auth_client_secret']
        else:
            config['graph_tenant_id'] = get_input("Tenant ID do App SharePoint", default=config['auth_tenant_id'])
            config['graph_client_id'] = get_input("Client ID do App SharePoint")
            config['graph_client_secret'] = get_input("Client Secret do App SharePoint")
        
        print("\n📂 Tipo de conexão:")
        print("   1. OneDrive (pasta Documents de um usuário)")
        print("   2. SharePoint Site (biblioteca de documentos)\n")
        
        mode_choice = get_input("Escolha (1 ou 2)", default="1")
        
        if mode_choice == "2":
            config['sharepoint_mode'] = 'sharepoint'
            print("\n📍 Configuração do SharePoint Site:")
            print("   Exemplo: https://empresa.sharepoint.com/sites/meusite")
            print("   hostname = empresa.sharepoint.com")
            print("   site_path = sites/meusite\n")
            
            config['hostname'] = get_input("Hostname (ex: empresa.sharepoint.com)")
            config['site_path'] = get_input("Site Path (ex: sites/meusite)")
            config['library_name'] = get_input("Nome da Biblioteca", default="Documents")
            config['file_path'] = get_input("Caminho do arquivo (relativo à biblioteca)", required=False)
        else:
            config['sharepoint_mode'] = 'onedrive'
            print("\n📍 Configuração do OneDrive:")
            config['user_upn'] = get_input("Email do usuário dono do OneDrive (ex: usuario@empresa.com)")
            config['file_path'] = get_input("Caminho do arquivo (relativo a Documents/)", required=False)
    
    # ========== PASSO 4: Criar arquivo ==========
    print("\n" + "=" * 70)
    print("📋 PASSO 4: Criando arquivo de configuração")
    print("=" * 70 + "\n")
    
    if create_secrets_file(config):
        update_gitignore()
        
        print("\n" + "=" * 70)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
        sharepoint_info = ""
        if config.get('sharepoint_enabled'):
            sharepoint_info = """
   📁 SharePoint/OneDrive configurado!
      Use o SPConnector para acessar arquivos:
      
      from sp_connector import SPConnector
      sp = SPConnector(
          tenant_id=st.secrets["graph"]["tenant_id"],
          client_id=st.secrets["graph"]["client_id"],
          client_secret=st.secrets["graph"]["client_secret"],
          user_upn=st.secrets["graph"].get("user_upn")  # ou hostname/site_path
      )
      df = sp.read_csv("caminho/arquivo.csv")
"""
        
        print(f"""
📁 Arquivos criados/atualizados:
   ├── .streamlit/secrets.toml  (suas credenciais)
   └── .gitignore               (protege suas credenciais)
{sharepoint_info}
🚀 Próximos passos:

   1. Execute a aplicação localmente:
      streamlit run app.py

   2. Teste o login com sua conta Microsoft

   3. Para deploy no Streamlit Cloud:
      - Faça push do código (sem o secrets.toml!)
      - No painel do Streamlit Cloud, vá em Settings > Secrets
      - Cole o conteúdo do seu secrets.toml

📖 Consulte o README.md para mais detalhes.
""")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)
