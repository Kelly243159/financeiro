import streamlit as st
import pandas as pd
import re
import os
import hashlib
import json
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import tempfile

PARCELA_REGEX = re.compile(r"\((\d+)/(\d+)\)")

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

COR_HEADER_BG = "0F1B2D"
COR_HEADER_FONT = "FFFFFF"
COR_TITULO_BG = "1B3A5C"
COR_TITULO_FONT = "FFFFFF"
COR_ZEBRA_A = "FFFFFF"
COR_ZEBRA_B = "EDF2F7"
COR_RESUMO_BG = "E2E8F0"
COR_RESUMO_FONT = "0F1B2D"
COR_BORDA = "CBD5E1"

# ═══════════════════════════════════════════
# CONFIGURAÇÃO DE USUÁRIOS
# ═══════════════════════════════════════════
# Para adicionar novos usuários, basta incluir no dicionário abaixo.
# A senha é armazenada como hash SHA-256 para segurança básica.
# Para gerar o hash de uma nova senha, use:
#   python -c "import hashlib; print(hashlib.sha256('sua_senha'.encode()).hexdigest())"

def _hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Usuários padrão — altere as senhas antes de usar em produção!
USUARIOS = {
    "mvtec2026": {
        "senha_hash": _hash_senha("MV@@2026"),
        "nome": "MV TEC",
        "perfil": "admin",
    },
}


def autenticar(usuario, senha):
    """Verifica credenciais e retorna dados do usuário ou None."""
    user_data = USUARIOS.get(usuario.lower().strip())
    if user_data and user_data["senha_hash"] == _hash_senha(senha):
        return user_data
    return None


# ═══════════════════════════════════════════
# TELA DE LOGIN
# ═══════════════════════════════════════════

def tela_login():
    """Renderiza a tela de login com estilo profissional."""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&display=swap');

    :root {
        --mv-navy:    #0f1b2d;
        --mv-blue:    #1b3a5c;
        --mv-accent:  #3b82f6;
        --mv-accent2: #60a5fa;
        --mv-surface: #f8fafc;
        --mv-border:  #e2e8f0;
        --mv-text:    #1e293b;
        --mv-muted:   #64748b;
        --mv-radius:  14px;
    }

    .stApp {
        background: linear-gradient(160deg, #0f1b2d 0%, #1b3a5c 40%, #234e7a 70%, #2d6498 100%) !important;
        min-height: 100vh;
    }

    html, body, .stApp, .stApp * {
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Container do login ── */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
        min-height: 70vh;
    }

    .login-card {
        background: rgba(255, 255, 255, 0.97);
        border-radius: 20px;
        padding: 2.8rem 2.4rem 2.2rem;
        width: 100%;
        max-width: 400px;
        box-shadow:
            0 4px 6px rgba(0,0,0,0.07),
            0 20px 60px rgba(0,0,0,0.15),
            0 0 0 1px rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }

    .login-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #3b82f6);
        background-size: 200% 100%;
        animation: shimmer 3s ease infinite;
    }

    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .login-logo {
        text-align: center;
        margin-bottom: 0.3rem;
    }

    .login-logo .icon-circle {
        width: 64px; height: 64px;
        background: linear-gradient(135deg, #0f1b2d, #1b3a5c);
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 12px rgba(15,27,45,0.2);
    }

    .login-logo h2 {
        color: #0f1b2d;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        margin: 0;
    }

    .login-logo p {
        color: #64748b;
        font-size: 0.78rem;
        margin: 0.25rem 0 0;
        letter-spacing: 0.3px;
    }

    .login-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 1.4rem 0 1.6rem;
    }

    /* ── Estilizar inputs ── */
    .login-card [data-testid="stTextInput"] label,
    .login-card [data-testid="stPasswordInput"] label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .login-card [data-testid="stTextInput"] input,
    .login-card [data-testid="stPasswordInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 0.6rem 0.9rem !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease !important;
        background: #f8fafc !important;
    }

    .login-card [data-testid="stTextInput"] input:focus,
    .login-card [data-testid="stPasswordInput"] input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
        background: #fff !important;
    }

    /* ── Botão de login ── */
    .login-card .stButton > button[kind="primary"],
    .login-card button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #0f1b2d, #1b3a5c) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.5px;
        transition: all 0.25s ease;
        margin-top: 0.5rem;
    }

    .login-card .stButton > button[kind="primary"]:hover,
    .login-card button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #1b3a5c, #234e7a) !important;
        box-shadow: 0 6px 20px rgba(15,27,45,0.3);
        transform: translateY(-1px);
    }

    .login-footer {
        text-align: center;
        margin-top: 1.2rem;
        color: #94a3b8;
        font-size: 0.72rem;
        letter-spacing: 0.3px;
    }

    /* ── Erro de login ── */
    .login-error {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.2);
        border-radius: 10px;
        padding: 0.6rem 1rem;
        color: #dc2626;
        font-size: 0.82rem;
        font-weight: 500;
        text-align: center;
        margin-top: 0.5rem;
        animation: shakeX 0.5s ease;
    }

    @keyframes shakeX {
        0%, 100% { transform: translateX(0); }
        20%, 60% { transform: translateX(-6px); }
        40%, 80% { transform: translateX(6px); }
    }

    /* ── Partículas de fundo ── */
    .bg-particles {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 0;
    }

    .bg-particles .orb {
        position: absolute;
        border-radius: 50%;
        opacity: 0.06;
        background: #60a5fa;
        animation: floatOrb 20s ease-in-out infinite;
    }

    .bg-particles .orb:nth-child(1) {
        width: 300px; height: 300px; top: 10%; left: -5%;
        animation-delay: 0s;
    }
    .bg-particles .orb:nth-child(2) {
        width: 200px; height: 200px; top: 60%; right: -3%;
        animation-delay: -7s;
    }
    .bg-particles .orb:nth-child(3) {
        width: 150px; height: 150px; bottom: 10%; left: 30%;
        animation-delay: -14s;
    }

    @keyframes floatOrb {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -20px) scale(1.05); }
        66% { transform: translate(-20px, 15px) scale(0.95); }
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>

    <div class="bg-particles">
        <div class="orb"></div>
        <div class="orb"></div>
        <div class="orb"></div>
    </div>
    """, unsafe_allow_html=True)

    # Layout centralizado
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-card">
                <div class="login-logo">
                    <div class="icon-circle">📊</div>
                    <h2>MV TEC</h2>
                    <p>Gestão de parcelas e empréstimos</p>
                </div>
                <div class="login-divider"></div>
        """, unsafe_allow_html=True)

        usuario = st.text_input("Usuário", placeholder="Digite seu usuário", key="login_user")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="login_pass")

        if st.button("Entrar", use_container_width=True, type="primary", key="login_btn"):
            if usuario and senha:
                user_data = autenticar(usuario, senha)
                if user_data:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["nome_usuario"] = user_data["nome"]
                    st.session_state["perfil"] = user_data["perfil"]
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="login-error">⚠ Usuário ou senha incorretos</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="login-error">Preencha todos os campos</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("""
                <div class="login-footer">
                    © 2026 MV TEC — Acesso restrito
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# GERADOR DE RELATÓRIO PROFISSIONAL
# ═══════════════════════════════════════════

def _gerar_relatorio(ws_origem, linhas_quitadas, mes, ano):
    wb_rel = Workbook()
    ws = wb_rel.active
    ws.title = "Quitados"

    total_colunas_orig = ws_origem.max_column
    borda_fina = Border(
        left=Side(style="thin", color=COR_BORDA),
        right=Side(style="thin", color=COR_BORDA),
        top=Side(style="thin", color=COR_BORDA),
        bottom=Side(style="thin", color=COR_BORDA),
    )

    colunas_com_dados = []
    for col in range(1, total_colunas_orig + 1):
        header_val = ws_origem.cell(row=1, column=col).value
        if header_val is None or str(header_val).strip() == "":
            continue
        tem_dado = False
        for row in linhas_quitadas:
            val = ws_origem.cell(row=row, column=col).value
            if val is not None and str(val).strip() != "":
                tem_dado = True
                break
        if tem_dado:
            colunas_com_dados.append(col)

    if not colunas_com_dados and linhas_quitadas:
        for col in range(1, total_colunas_orig + 1):
            header_val = ws_origem.cell(row=1, column=col).value
            if header_val is not None and str(header_val).strip() != "":
                colunas_com_dados.append(col)

    total_colunas = len(colunas_com_dados)
    if total_colunas == 0:
        total_colunas = total_colunas_orig
        colunas_com_dados = list(range(1, total_colunas_orig + 1))

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_colunas)
    titulo_cell = ws.cell(row=1, column=1)
    nome_mes = MESES_PT.get(int(mes), mes)
    titulo_cell.value = f"RELATÓRIO DE PARCELAS QUITADAS — {nome_mes.upper()} / {ano}"
    titulo_cell.font = Font(name="Arial", bold=True, size=13, color=COR_TITULO_FONT)
    titulo_cell.fill = PatternFill("solid", fgColor=COR_TITULO_BG)
    titulo_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36
    for c in range(2, total_colunas + 1):
        ws.cell(row=1, column=c).fill = PatternFill("solid", fgColor=COR_TITULO_BG)

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_colunas)
    sub_cell = ws.cell(row=2, column=1)
    sub_cell.value = f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}  •  Total de registros: {len(linhas_quitadas)}"
    sub_cell.font = Font(name="Arial", size=9, color="64748B", italic=True)
    sub_cell.fill = PatternFill("solid", fgColor=COR_ZEBRA_B)
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22
    for c in range(2, total_colunas + 1):
        ws.cell(row=2, column=c).fill = PatternFill("solid", fgColor=COR_ZEBRA_B)

    header_fill = PatternFill("solid", fgColor=COR_HEADER_BG)
    header_font = Font(name="Arial", bold=True, size=10, color=COR_HEADER_FONT)
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for dest_col, orig_col in enumerate(colunas_com_dados, start=1):
        cell = ws.cell(row=3, column=dest_col, value=ws_origem.cell(row=1, column=orig_col).value)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = borda_fina
    ws.row_dimensions[3].height = 28

    fill_a = PatternFill("solid", fgColor=COR_ZEBRA_A)
    fill_b = PatternFill("solid", fgColor=COR_ZEBRA_B)
    data_font = Font(name="Arial", size=10, color="1E293B")
    data_align = Alignment(vertical="center", wrap_text=True)
    data_align_center = Alignment(horizontal="center", vertical="center")

    linha_destino = 4
    for idx, row in enumerate(linhas_quitadas):
        fill = fill_a if idx % 2 == 0 else fill_b
        for dest_col, orig_col in enumerate(colunas_com_dados, start=1):
            valor = ws_origem.cell(row=row, column=orig_col).value
            cell = ws.cell(row=linha_destino, column=dest_col, value=valor)
            cell.font = data_font
            cell.fill = fill
            cell.border = borda_fina
            if isinstance(valor, (int, float)):
                cell.alignment = data_align_center
                if isinstance(valor, float):
                    cell.number_format = '#,##0.00'
                elif isinstance(valor, int) and valor > 100:
                    cell.number_format = '#,##0'
            else:
                cell.alignment = data_align
        ws.row_dimensions[linha_destino].height = 22
        linha_destino += 1

    if linhas_quitadas:
        resumo_row = linha_destino + 1
        resumo_fill = PatternFill("solid", fgColor=COR_RESUMO_BG)
        resumo_font = Font(name="Arial", bold=True, size=10, color=COR_RESUMO_FONT)

        merge_end = min(2, total_colunas)
        if merge_end > 1:
            ws.merge_cells(start_row=resumo_row, start_column=1, end_row=resumo_row, end_column=merge_end)
        cell_label = ws.cell(row=resumo_row, column=1, value="TOTAL QUITADOS")
        cell_label.font = resumo_font
        cell_label.fill = resumo_fill
        cell_label.alignment = Alignment(horizontal="right", vertical="center")
        cell_label.border = borda_fina
        if merge_end > 1:
            ws.cell(row=resumo_row, column=2).fill = resumo_fill
            ws.cell(row=resumo_row, column=2).border = borda_fina

        val_col = min(3, total_colunas)
        if val_col > merge_end:
            cell_val = ws.cell(row=resumo_row, column=val_col, value=len(linhas_quitadas))
            cell_val.font = Font(name="Arial", bold=True, size=12, color=COR_RESUMO_FONT)
            cell_val.fill = resumo_fill
            cell_val.alignment = Alignment(horizontal="center", vertical="center")
            cell_val.border = borda_fina

        for col in range(val_col + 1, total_colunas + 1):
            c = ws.cell(row=resumo_row, column=col)
            c.fill = resumo_fill
            c.border = borda_fina
        ws.row_dimensions[resumo_row].height = 28

    for dest_col in range(1, total_colunas + 1):
        max_len = 0
        col_letter = get_column_letter(dest_col)
        for row_idx in range(1, linha_destino + 2):
            val = ws.cell(row=row_idx, column=dest_col).value
            if val:
                max_len = max(max_len, len(str(val)))
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 45)

    ws.freeze_panes = "A4"

    if linhas_quitadas:
        last_data_row = 3 + len(linhas_quitadas)
        ws.auto_filter.ref = f"A3:{get_column_letter(total_colunas)}{last_data_row}"

    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = "1:3"

    return wb_rel


# ═══════════════════════════════════════════
# FUNÇÕES DE PROCESSAMENTO
# ═══════════════════════════════════════════

def processar_planilha(caminho_entrada, mes, ano):
    wb = load_workbook(caminho_entrada)
    ws = wb.active
    linhas_quitadas = []

    for row in range(2, ws.max_row + 1):
        cell = ws[f"H{row}"]
        valor = cell.value
        if not isinstance(valor, str):
            continue
        match = PARCELA_REGEX.search(valor)
        if not match:
            continue
        atual = int(match.group(1))
        total = int(match.group(2))
        if atual == total:
            ws.row_dimensions[row].hidden = True
            linhas_quitadas.append(row)
            continue
        cell.value = f"({atual}/{total + 1})"

    wb_rel = _gerar_relatorio(ws, linhas_quitadas, mes, ano)

    pasta = os.path.dirname(caminho_entrada)
    nome_base = os.path.splitext(os.path.basename(caminho_entrada))[0]
    saida = os.path.join(pasta, f"{nome_base}_ATUALIZADO_{mes}_{ano}.xlsx")
    relatorio = os.path.join(pasta, f"{nome_base}_QUITADOS_{mes}_{ano}.xlsx")

    wb.save(saida)
    wb_rel.save(relatorio)
    return saida, relatorio, len(linhas_quitadas)


def processar_planilha_coluna_f(caminho_entrada, mes, ano):
    wb = load_workbook(caminho_entrada)
    ws = wb.active
    linhas_quitadas = []

    for row in range(2, ws.max_row + 1):
        cell_d = ws[f"D{row}"]
        cell_f = ws[f"F{row}"]
        valor_d = cell_d.value
        valor_f = cell_f.value
        if valor_d is None or valor_d == "" or valor_f is None or valor_f == "":
            continue
        try:
            if isinstance(valor_d, str):
                valor_d = re.sub(r'[^\d]', '', valor_d)
            parcela_atual = int(valor_d) if valor_d else 0
            if isinstance(valor_f, str):
                valor_f = re.sub(r'[^\d]', '', valor_f)
            total_parcelas = int(valor_f) if valor_f else 0
            if parcela_atual == 0 or total_parcelas == 0:
                continue
        except (ValueError, TypeError):
            continue

        novo_total = total_parcelas + 1
        ws[f"F{row}"] = novo_total

        if novo_total == parcela_atual:
            ws.row_dimensions[row].hidden = True
            linhas_quitadas.append(row)

    wb_rel = _gerar_relatorio(ws, linhas_quitadas, mes, ano)

    pasta = os.path.dirname(caminho_entrada)
    nome_base = os.path.splitext(os.path.basename(caminho_entrada))[0]
    saida = os.path.join(pasta, f"{nome_base}_ATUALIZADO_{mes}_{ano}.xlsx")
    relatorio = os.path.join(pasta, f"{nome_base}_QUITADOS_{mes}_{ano}.xlsx")

    wb.save(saida)
    wb_rel.save(relatorio)
    return saida, relatorio, len(linhas_quitadas)


# ═══════════════════════════════════════════
# COMPONENTE DE PROCESSAMENTO
# ═══════════════════════════════════════════

def bloco_processamento(key_prefix, descricao, funcao_processar):
    arquivo = st.file_uploader(
        "Arraste o arquivo .xlsx aqui",
        type=['xlsx'],
        key=f"{key_prefix}_uploader",
        help="Apenas arquivos .xlsx são suportados"
    )

    if not arquivo:
        st.markdown(
            f'<p style="text-align:center; color: var(--text-muted); padding: 1.5rem 0; opacity: 0.6;">'
            f'{descricao}</p>',
            unsafe_allow_html=True,
        )
        return

    temp_path = os.path.join(tempfile.gettempdir(), f"mv_{key_prefix}_{arquivo.name}")
    with open(temp_path, "wb") as f:
        f.write(arquivo.getbuffer())

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:8px 14px;'
        f'background:rgba(16,185,129,0.08);border-radius:10px;margin:0.5rem 0 1rem;">'
        f'<span style="font-size:1.15rem;">📎</span>'
        f'<span style="color:#059669;font-weight:500;font-size:0.9rem;">{arquivo.name}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        mes = st.number_input(
            "Mês de referência", min_value=1, max_value=12,
            value=datetime.now().month, step=1, key=f"{key_prefix}_mes"
        )
    with col2:
        ano = st.number_input(
            "Ano de referência", min_value=2020, max_value=2035,
            value=datetime.now().year, step=1, key=f"{key_prefix}_ano"
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button("Processar", key=f"{key_prefix}_btn", use_container_width=True, type="primary"):
        with st.spinner("Processando…"):
            try:
                saida, relatorio, qtd = funcao_processar(temp_path, str(mes), str(ano))

                st.markdown("---")
                st.markdown("#### Resultado")

                m1, m2 = st.columns(2)
                m1.metric("Parcelas quitadas", qtd)
                m2.metric("Arquivos gerados", 2)

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                d1, d2 = st.columns(2)
                with d1:
                    with open(saida, "rb") as f:
                        st.download_button(
                            "⬇  Planilha Atualizada", f,
                            file_name=os.path.basename(saida),
                            use_container_width=True,
                        )
                with d2:
                    with open(relatorio, "rb") as f:
                        st.download_button(
                            "⬇  Relatório de Quitados", f,
                            file_name=os.path.basename(relatorio),
                            use_container_width=True,
                        )

            except Exception as e:
                st.error(f"Erro ao processar: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)


# ═══════════════════════════════════════════
# INTERFACE PRINCIPAL (PÓS-LOGIN)
# ═══════════════════════════════════════════

def tela_principal():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,400&display=swap');

    :root {
        --mv-navy:    #0f1b2d;
        --mv-blue:    #1b3a5c;
        --mv-accent:  #3b82f6;
        --mv-accent2: #60a5fa;
        --mv-surface: #f8fafc;
        --mv-border:  #e2e8f0;
        --mv-text:    #1e293b;
        --mv-muted:   #64748b;
        --mv-radius:  14px;
    }

    .stApp { background: var(--mv-surface) !important; }
    html, body, .stApp, .stApp * { font-family: 'DM Sans', sans-serif !important; }

    .mv-header {
        background: linear-gradient(135deg, var(--mv-navy) 0%, var(--mv-blue) 60%, #234e7a 100%);
        padding: 2.2rem 2rem 1.8rem;
        border-radius: 0 0 var(--mv-radius) var(--mv-radius);
        margin: -1rem -1rem 1.8rem;
        position: relative; overflow: hidden;
    }
    .mv-header::before {
        content: ''; position: absolute; top: -40%; right: -10%;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .mv-header h1 {
        color: #fff; font-size: 1.6rem; font-weight: 700;
        letter-spacing: 2.5px; margin: 0; position: relative;
    }
    .mv-header p {
        color: rgba(255,255,255,0.55); font-size: 0.82rem;
        font-weight: 400; margin: 0.35rem 0 0;
        letter-spacing: 0.5px; position: relative;
    }
    .mv-header .user-badge {
        position: absolute; top: 50%; right: 2rem;
        transform: translateY(-50%);
        display: flex; align-items: center; gap: 10px;
        color: rgba(255,255,255,0.7); font-size: 0.82rem;
    }
    .mv-header .user-badge .avatar {
        width: 34px; height: 34px;
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0; background: #fff; border-radius: var(--mv-radius);
        padding: 4px; border: 1px solid var(--mv-border);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px; padding: 0.55rem 1.2rem;
        font-size: 0.85rem; font-weight: 500;
        color: var(--mv-muted); background: transparent; white-space: nowrap;
    }
    .stTabs [aria-selected="true"] {
        background: var(--mv-navy) !important; color: #fff !important; font-weight: 600;
    }
    .stTabs [data-baseweb="tab-border"],
    .stTabs [data-baseweb="tab-highlight"] { display: none; }

    [data-testid="stFileUploader"] { border-radius: var(--mv-radius); }
    [data-testid="stFileUploader"] section {
        border-radius: var(--mv-radius) !important;
        border: 2px dashed var(--mv-border) !important;
        padding: 1.5rem !important; transition: border-color 0.2s;
    }
    [data-testid="stFileUploader"] section:hover { border-color: var(--mv-accent) !important; }
    [data-testid="stFileUploader"] svg { display: none; }

    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: var(--mv-navy) !important; color: #fff !important;
        border: none !important; border-radius: 10px !important;
        padding: 0.65rem 1.5rem !important; font-weight: 600 !important;
        font-size: 0.9rem !important; letter-spacing: 0.3px; transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background: var(--mv-blue) !important;
        box-shadow: 0 4px 14px rgba(15,27,45,0.25); transform: translateY(-1px);
    }

    .stDownloadButton > button {
        background: #fff !important; color: var(--mv-navy) !important;
        border: 1.5px solid var(--mv-border) !important; border-radius: 10px !important;
        font-weight: 600 !important; font-size: 0.85rem !important; transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover {
        border-color: var(--mv-accent) !important; color: var(--mv-accent) !important;
        box-shadow: 0 2px 8px rgba(59,130,246,0.12);
    }

    [data-testid="stMetric"] {
        background: #fff; border: 1px solid var(--mv-border);
        border-radius: 12px; padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricValue"] { color: var(--mv-navy); font-weight: 700; }
    [data-testid="stMetricLabel"] { color: var(--mv-muted); font-size: 0.8rem; font-weight: 500; }

    [data-testid="stNumberInput"] label {
        font-size: 0.85rem; font-weight: 500; color: var(--mv-text);
    }

    hr { border-color: var(--mv-border) !important; opacity: 0.5; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    nome = st.session_state.get("nome_usuario", "Usuário")
    iniciais = "".join([p[0].upper() for p in nome.split()[:2]]) if nome else "U"

    st.markdown(f"""
        <div class="mv-header">
            <h1>MV TEC</h1>
            <p>Gestão de parcelas e empréstimos</p>
            <div class="user-badge">
                <span>{nome}</span>
                <div class="avatar">{iniciais}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Botão de logout na sidebar
    with st.sidebar:
        st.markdown(f"**Logado como:** {nome}")
        st.markdown(f"**Perfil:** {st.session_state.get('perfil', 'operador').title()}")
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            for key in ["autenticado", "usuario", "nome_usuario", "perfil"]:
                st.session_state.pop(key, None)
            st.rerun()

    tab1, tab2 = st.tabs(["Empréstimos Individuais", "Empréstimos"])

    with tab1:
        bloco_processamento(
            key_prefix="ind",
            descricao="Processa parcelas no formato (X/Y) na coluna H",
            funcao_processar=processar_planilha,
        )

    with tab2:
        bloco_processamento(
            key_prefix="col",
            descricao="Incrementa coluna F — se F = D após incremento, marca como quitado",
            funcao_processar=processar_planilha_coluna_f,
        )


# ═══════════════════════════════════════════
# PONTO DE ENTRADA
# ═══════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="MV TEC",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    if st.session_state.get("autenticado"):
        tela_principal()
    else:
        tela_login()


if __name__ == "__main__":
    main()