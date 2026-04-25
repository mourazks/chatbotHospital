"""
============================================================
  CHATBOT DE ATENDIMENTO HOSPITALAR
  Sistema de atendimento virtual para hospitais
  Desenvolvido em Python puro (sem bibliotecas externas)
============================================================
"""

import os
import uuid
from datetime import datetime

# ============================================================
# BANCO DE DADOS EM MEMÓRIA
# Estrutura pronta para futura migração a um banco real.
# Cada "tabela" é um dicionário indexado por ID único.
# ============================================================

pacientes = {}
# Formato:
# {
#   "id_paciente": {
#       "nome": str,
#       "idade": int,
#       "cpf": str,
#       "telefone": str
#   }
# }

consultas = {}
# Formato:
# {
#   "id_consulta": {
#       "id_paciente": str,
#       "especialidade": str,
#       "data": str,
#       "horario": str,
#       "status": "ativa" | "cancelada"
#   }
# }

# ============================================================
# UTILITÁRIOS GERAIS
# ============================================================

def gerar_id():
    """Gera um ID único curto para pacientes e consultas."""
    return str(uuid.uuid4())[:8].upper()

def limpar_tela():
    """Limpa o terminal para melhorar a leitura."""
    os.system('cls' if os.name == 'nt' else 'clear')

def linha_separadora():
    """Imprime uma linha separadora visual."""
    print("\n" + "=" * 55 + "\n")

def pausar():
    """Pausa a execução até o usuário pressionar Enter."""
    input("\n  Pressione Enter para continuar...")

def falar(mensagem):
    """Simula a fala do atendente com formatação visual."""
    print(f"\n  🏥 Atendente: {mensagem}")

def erro(mensagem):
    """Exibe uma mensagem de erro formatada."""
    print(f"\n  ⚠️  {mensagem}")

def sucesso(mensagem):
    """Exibe uma mensagem de sucesso formatada."""
    print(f"\n  ✅  {mensagem}")

# ============================================================
# VALIDAÇÕES
# ============================================================

def validar_cpf(cpf):
    """
    Valida o formato básico do CPF (somente dígitos, 11 caracteres).
    Em produção, aplicar validação completa com dígitos verificadores.
    """
    cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
    return cpf_limpo.isdigit() and len(cpf_limpo) == 11

def validar_telefone(telefone):
    """Valida se o telefone contém entre 10 e 11 dígitos numéricos."""
    tel_limpo = telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
    return tel_limpo.isdigit() and 10 <= len(tel_limpo) <= 11

def validar_data(data_str):
    """
    Valida se a data está no formato DD/MM/AAAA e se é uma data futura.
    Retorna True se válida, False caso contrário.
    """
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
        if data.date() < datetime.today().date():
            erro("A data informada já passou. Por favor, informe uma data futura.")
            return False
        return True
    except ValueError:
        erro("Formato de data inválido. Use DD/MM/AAAA (ex: 25/12/2025).")
        return False

def validar_horario(horario_str):
    """Valida se o horário está no formato HH:MM."""
    try:
        datetime.strptime(horario_str, "%H:%M")
        return True
    except ValueError:
        erro("Formato de horário inválido. Use HH:MM (ex: 14:30).")
        return False

def cpf_ja_cadastrado(cpf):
    """Verifica se um CPF já existe na base de pacientes."""
    cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
    for p in pacientes.values():
        if p["cpf"] == cpf_limpo:
            return True
    return False

# ============================================================
# MÓDULO 1: CADASTRO DE PACIENTE
# ============================================================

def cadastrar_paciente():
    """
    Coleta os dados do paciente via terminal e os armazena em memória.
    Valida CPF, telefone e duplicidade antes de salvar.
    """
    limpar_tela()
    linha_separadora()
    falar("Vamos fazer seu cadastro. Por favor, responda com atenção.")
    linha_separadora()

    # --- Nome ---
    while True:
        nome = input("  Nome completo: ").strip()
        if len(nome) >= 3 and nome.replace(" ", "").isalpha():
            break
        erro("Nome inválido. Use apenas letras e ao menos 3 caracteres.")

    # --- Idade ---
    while True:
        try:
            idade = int(input("  Idade: ").strip())
            if 0 <= idade <= 130:
                break
            erro("Idade inválida. Informe um valor entre 0 e 130.")
        except ValueError:
            erro("Por favor, informe um número inteiro para a idade.")

    # --- CPF ---
    while True:
        cpf = input("  CPF (somente números ou formato 000.000.000-00): ").strip()
        if not validar_cpf(cpf):
            erro("CPF inválido. Verifique e tente novamente.")
            continue
        if cpf_ja_cadastrado(cpf):
            erro("Este CPF já está cadastrado em nosso sistema.")
            pausar()
            return
        break

    # --- Telefone ---
    while True:
        telefone = input("  Telefone (com DDD): ").strip()
        if validar_telefone(telefone):
            break
        erro("Telefone inválido. Informe entre 10 e 11 dígitos.")

    # Salva o paciente com ID único
    id_paciente = gerar_id()
    pacientes[id_paciente] = {
        "nome": nome,
        "idade": idade,
        "cpf": cpf.replace(".", "").replace("-", "").strip(),
        "telefone": telefone
    }

    sucesso(f"Cadastro realizado com sucesso!")
    falar(f"Seu código de paciente é: {id_paciente}. Anote para consultas futuras.")
    pausar()

# ============================================================
# MÓDULO 2: BUSCAR PACIENTE (auxiliar)
# ============================================================

ESPECIALIDADES = [
    "Clínica Geral",
    "Cardiologia",
    "Ortopedia",
    "Pediatria",
    "Neurologia",
    "Dermatologia",
    "Ginecologia",
    "Oftalmologia"
]

def buscar_paciente_por_cpf():
    """
    Solicita o CPF e retorna o ID e dados do paciente se encontrado.
    Retorna (None, None) se não encontrado.
    """
    cpf = input("  CPF do paciente: ").strip().replace(".", "").replace("-", "")
    for id_p, dados in pacientes.items():
        if dados["cpf"] == cpf:
            return id_p, dados
    erro("Paciente não encontrado. Verifique o CPF ou faça o cadastro primeiro.")
    return None, None

# ============================================================
# MÓDULO 3: AGENDAMENTO DE CONSULTA
# ============================================================

def agendar_consulta():
    """
    Permite ao paciente agendar uma consulta escolhendo
    especialidade, data e horário. Valida todas as entradas.
    """
    limpar_tela()
    linha_separadora()
    falar("Vamos agendar sua consulta. Precisarei do seu CPF.")
    linha_separadora()

    id_paciente, dados_paciente = buscar_paciente_por_cpf()
    if not id_paciente:
        pausar()
        return

    falar(f"Olá, {dados_paciente['nome']}! Ótimo te encontrar aqui.")

    # --- Escolha da especialidade ---
    print("\n  Especialidades disponíveis:\n")
    for i, esp in enumerate(ESPECIALIDADES, 1):
        print(f"    [{i}] {esp}")

    while True:
        try:
            escolha = int(input("\n  Escolha o número da especialidade: ").strip())
            if 1 <= escolha <= len(ESPECIALIDADES):
                especialidade = ESPECIALIDADES[escolha - 1]
                break
            erro(f"Escolha entre 1 e {len(ESPECIALIDADES)}.")
        except ValueError:
            erro("Por favor, informe o número correspondente à especialidade.")

    # --- Data ---
    while True:
        data = input("  Data da consulta (DD/MM/AAAA): ").strip()
        if validar_data(data):
            break

    # --- Horário ---
    while True:
        horario = input("  Horário preferido (HH:MM): ").strip()
        if validar_horario(horario):
            break

    # Salva a consulta
    id_consulta = gerar_id()
    consultas[id_consulta] = {
        "id_paciente": id_paciente,
        "especialidade": especialidade,
        "data": data,
        "horario": horario,
        "status": "ativa"
    }

    sucesso("Consulta agendada com sucesso!")
    falar(
        f"Sua consulta de {especialidade} está marcada para "
        f"{data} às {horario}. Código da consulta: {id_consulta}."
    )
    pausar()

# ============================================================
# MÓDULO 4: LISTAR CONSULTAS
# ============================================================

def listar_consultas():
    """
    Solicita o CPF do paciente e exibe todas as suas consultas ativas,
    com formatação clara e organizada.
    """
    limpar_tela()
    linha_separadora()
    falar("Vou buscar suas consultas. Informe seu CPF.")
    linha_separadora()

    id_paciente, dados_paciente = buscar_paciente_por_cpf()
    if not id_paciente:
        pausar()
        return

    # Filtra consultas ativas do paciente
    consultas_paciente = [
        (id_c, c) for id_c, c in consultas.items()
        if c["id_paciente"] == id_paciente and c["status"] == "ativa"
    ]

    if not consultas_paciente:
        falar(f"{dados_paciente['nome']}, você não possui consultas agendadas no momento.")
        pausar()
        return

    print(f"\n  Consultas de {dados_paciente['nome']}:\n")
    print(f"  {'Código':<10} {'Especialidade':<20} {'Data':<12} {'Horário':<8}")
    print(f"  {'-'*10} {'-'*20} {'-'*12} {'-'*8}")

    for id_c, c in consultas_paciente:
        print(f"  {id_c:<10} {c['especialidade']:<20} {c['data']:<12} {c['horario']:<8}")

    pausar()

# ============================================================
# MÓDULO 5: CANCELAR CONSULTA
# ============================================================

def cancelar_consulta():
    """
    Permite cancelar uma consulta ativa, confirmando antes de prosseguir.
    Valida se o código pertence ao paciente informado.
    """
    limpar_tela()
    linha_separadora()
    falar("Para cancelar uma consulta, confirme seu CPF primeiro.")
    linha_separadora()

    id_paciente, dados_paciente = buscar_paciente_por_cpf()
    if not id_paciente:
        pausar()
        return

    # Lista apenas as consultas ativas do paciente
    consultas_ativas = [
        (id_c, c) for id_c, c in consultas.items()
        if c["id_paciente"] == id_paciente and c["status"] == "ativa"
    ]

    if not consultas_ativas:
        falar("Você não possui consultas ativas para cancelar.")
        pausar()
        return

    print(f"\n  Consultas ativas de {dados_paciente['nome']}:\n")
    for id_c, c in consultas_ativas:
        print(f"  [{id_c}] {c['especialidade']} — {c['data']} às {c['horario']}")

    codigo = input("\n  Informe o código da consulta a cancelar: ").strip().upper()

    # Verifica se o código existe e pertence ao paciente
    if codigo not in consultas:
        erro("Código de consulta não encontrado.")
        pausar()
        return

    if consultas[codigo]["id_paciente"] != id_paciente:
        erro("Esta consulta não pertence ao seu cadastro.")
        pausar()
        return

    if consultas[codigo]["status"] == "cancelada":
        erro("Esta consulta já foi cancelada anteriormente.")
        pausar()
        return

    # Confirmação antes de cancelar
    confirmacao = input("\n  Tem certeza que deseja cancelar? (s/n): ").strip().lower()
    if confirmacao == "s":
        consultas[codigo]["status"] = "cancelada"
        sucesso("Consulta cancelada com sucesso.")
        falar("Esperamos vê-lo novamente em breve. Cuide-se!")
    else:
        falar("Cancelamento abortado. Sua consulta segue agendada normalmente.")

    pausar()

# ============================================================
# MÓDULO 6: INFORMAÇÕES DO HOSPITAL
# ============================================================

INFORMACOES = {
    "1": {
        "titulo": "Horário de Funcionamento",
        "conteudo": (
            "Segunda a Sexta: 07h às 19h\n"
            "  Sábados: 08h às 14h\n"
            "  Domingos e Feriados: Emergência 24h"
        )
    },
    "2": {
        "titulo": "Endereço",
        "conteudo": (
            "Av. das Nações, 1500 — Asa Norte\n"
            "  Brasília — DF, CEP 70750-000\n"
            "  Próximo ao metrô Asa Norte"
        )
    },
    "3": {
        "titulo": "Contato e Emergência",
        "conteudo": (
            "Recepção: (61) 3000-1234\n"
            "  WhatsApp: (61) 99000-5678\n"
            "  Emergência 24h: 192 (SAMU) ou (61) 3000-9999"
        )
    },
    "4": {
        "titulo": "Convênios Aceitos",
        "conteudo": (
            "Unimed, Bradesco Saúde, SulAmérica,\n"
            "  Amil, Cassi, Postal Saúde e SUS"
        )
    }
}

def exibir_informacoes():
    """Exibe um submenu com as informações institucionais do hospital."""
    limpar_tela()
    linha_separadora()
    falar("Aqui estão as informações do hospital. O que deseja saber?")
    linha_separadora()

    print("  [1] Horário de Funcionamento")
    print("  [2] Endereço")
    print("  [3] Contato e Emergência")
    print("  [4] Convênios Aceitos")
    print("  [0] Voltar ao menu principal")

    opcao = input("\n  Sua escolha: ").strip()

    if opcao == "0":
        return

    if opcao in INFORMACOES:
        info = INFORMACOES[opcao]
        linha_separadora()
        print(f"  📋 {info['titulo']}:\n")
        print(f"  {info['conteudo']}")
    else:
        erro("Opção inválida.")

    pausar()

# ============================================================
# MENU PRINCIPAL
# ============================================================

def exibir_menu():
    """Exibe o menu principal do chatbot."""
    limpar_tela()
    linha_separadora()
    print("       🏥  HOSPITAL VIDA PLENA — ATENDIMENTO VIRTUAL")
    linha_separadora()
    falar("Olá! Eu sou a Marina, sua atendente virtual. Como posso ajudar?\n")
    print("  [1] Cadastrar paciente")
    print("  [2] Agendar consulta")
    print("  [3] Ver minhas consultas")
    print("  [4] Cancelar consulta")
    print("  [5] Informações do hospital")
    print("  [0] Encerrar atendimento")
    linha_separadora()

def main():
    """
    Função principal — loop de controle do chatbot.
    Mantém o sistema rodando até o usuário escolher sair.
    """
    while True:
        exibir_menu()
        opcao = input("  Digite o número da opção desejada: ").strip()

        if opcao == "1":
            cadastrar_paciente()
        elif opcao == "2":
            agendar_consulta()
        elif opcao == "3":
            listar_consultas()
        elif opcao == "4":
            cancelar_consulta()
        elif opcao == "5":
            exibir_informacoes()
        elif opcao == "0":
            limpar_tela()
            linha_separadora()
            falar("Atendimento encerrado. Cuide-se e até logo! 😊")
            linha_separadora()
            break
        else:
            erro("Opção inválida. Por favor, escolha uma das opções do menu.")
            pausar()

# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()