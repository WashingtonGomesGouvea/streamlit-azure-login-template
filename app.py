"""
Aplicação de Demonstração - Template Login Microsoft
Execute com: streamlit run app.py
"""

import streamlit as st
from auth_microsoft import (
    MicrosoftAuth,
    AuthManager,
    create_login_page,
    create_user_header,
    LOGIN_CONFIG
)

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA DE LOGIN (PERSONALIZE AQUI!)
# ============================================================================
LOGIN_CONFIG.update({
    "title": "Minha Aplicação",
    "subtitle": "Sistema de demonstração com login Microsoft",
    "badge_text": "Acesso Restrito",
    "email_domain": "@empresa.com",
    "highlights": [
        {
            "icon": "🔒",
            "title": "Segurança Integrada",
            "description": "Autenticação via Azure AD"
        },
        {
            "icon": "⚡",
            "title": "Acesso Rápido",
            "description": "Use sua conta Microsoft corporativa"
        },
        {
            "icon": "📊",
            "title": "Recursos Completos",
            "description": "Acesse todas as funcionalidades do sistema"
        }
    ]
})

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="Minha Aplicação",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================
# ============================================================================
# TELA DE APRESENTAÇÃO (QUANDO NÃO CONFIGURADO)
# ============================================================================
def create_presentation_page():
    """Mostra uma tela de apresentação quando o app não está configurado"""
    st.title("🔐 Template de Login Microsoft")
    
    st.info("👋 Bem-vindo ao Template de Login Microsoft + SharePoint!")
    
    st.markdown("""
    ### O que é este projeto?
    
    Este é um **template reutilizável** para criar aplicações Streamlit com autenticação corporativa segura.
    
    Ele já vem todo configurado para:
    
    *   ✅ **Autenticação Microsoft Azure AD**: Login seguro com sua conta corporativa.
    *   ✅ **Conexão SharePoint/OneDrive**: Leitura e escrita de arquivos diretamente no seu cloud storage.
    *   ✅ **Interface Moderna**: UI limpa e responsiva, pronta para uso.
    
    ---
    
    ### ⚠️ Configuração Necessária
    
    Para ver a tela de login real, você precisa configurar as credenciais do Azure.
    
    #### No Streamlit Cloud:
    1. Vá em **Settings** > **Secrets**.
    2. Adicione suas credenciais no formato TOML (veja o `README.md` ou `secrets.toml.example`).
    
    #### Localmente:
    1. Execute o script de configuração interativo:
       ```bash
       python configure_azure.py
       ```
    
    ---
    
    ### 📚 Recursos
    
    *   [Documentação do Streamlit](https://docs.streamlit.io)
    *   [Portal do Azure](https://portal.azure.com)
    """)
    
    # Exemplo visual dos componentes
    st.divider()
    st.write("### Preview de Componentes")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ Autenticação Pronta")
    with col2:
        st.info("📂 Conector SharePoint Incluso")

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================
# ============================================================================
# AUTENTICAÇÃO
# ============================================================================
auth = None
try:
    auth = MicrosoftAuth()
except ValueError:
    # Se houver erro de configuração (secrets faltando), mostra a apresentação
    create_presentation_page()
    st.stop()
except Exception as e:
    st.error(f"Erro inesperado na autenticação: {e}")
    st.stop()

# Tela de login (bloqueia execução se não autenticado)
if not create_login_page(auth, LOGIN_CONFIG):
    st.stop()

# Mostrar header do usuário na sidebar
create_user_header()

# Renovar token se necessário
AuthManager.check_and_refresh_token(auth)

# ============================================================================
# OBTER INFORMAÇÕES DO USUÁRIO
# ============================================================================
user = AuthManager.get_current_user()
user_name = user.get("displayName", "Usuário") if user else "Usuário"
user_email = user.get("mail") or user.get("userPrincipalName", "") if user else ""

# ============================================================================
# SUA APLICAÇÃO COMEÇA AQUI! 🚀
# ============================================================================

st.title("🎉 Bem-vindo!")
st.markdown(f"### Olá, **{user_name}**!")

st.success("✅ Login realizado com sucesso! Você pode começar a desenvolver sua aplicação.")

st.divider()

# Exemplo de conteúdo
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Usuário", user_name)

with col2:
    st.metric("Email", user_email.split("@")[0] if user_email else "N/A")

with col3:
    st.metric("Status", "Autenticado ✅")

st.divider()

# Informações de debug (remova em produção)
with st.expander("🔧 Informações de Debug"):
    st.json(user)

st.info("""
### Próximos Passos

1. **Personalize** o `LOGIN_CONFIG` no início deste arquivo
2. **Adicione** seu código abaixo da seção "SUA APLICAÇÃO COMEÇA AQUI!"
3. **Configure** as credenciais Azure com `python configure_azure.py`
4. **Faça deploy** no Streamlit Cloud

📖 Consulte o `README.md` para instruções detalhadas.
""")
