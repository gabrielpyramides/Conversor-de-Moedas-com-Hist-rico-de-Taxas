import customtkinter as ctk
import requests
from datetime import datetime
import csv
import json
import os
import hashlib  
from tkinter import filedialog, messagebox
import threading

"""
=========================================================
1. CONFIGURAÇÕES VISUAIS (PALETA DE CORES)
=========================================================
Centralizamos todas as cores aqui no topo. Pense nisso como 
a "lata de tinta" do nosso aplicativo. Se um dia quisermos 
mudar o aplicativo de Azul para Verde, só precisamos alterar 
os códigos aqui, e o aplicativo inteiro muda automaticamente.
"""
COLOR_BG = "#1E293B"       # Cor de fundo principal (Azul bem escuro)
COLOR_CARD = "#334155"     # Cor das caixas e painéis (Um pouco mais claro)
COLOR_ACCENT = "#38BDF8"   # Cor de destaque para botões e textos importantes (Azul claro)
COLOR_TEXT = "#F8FAFC"     # Cor do texto principal (Branco gelo)
COLOR_TEXT_DIM = "#94A3B8" # Cor do texto secundário/apagado (Cinza azulado)
COLOR_SUCCESS = "#10B981"  # Cor para mensagens de Sucesso (Verde)
COLOR_ERROR = "#F87171"    # Cor para mensagens de Erro ou Exclusão (Vermelho)
COLOR_BORDER = "#475569"   # Cor das bordas dos elementos

class FinancePro(ctk.CTk):
    """
    =========================================================
    2. O CORAÇÃO DO APLICATIVO (CLASSE PRINCIPAL)
    =========================================================
    Esta classe é a "planta baixa" do nosso aplicativo. 
    Ela herda todas as funções visuais do CustomTkinter (ctk.CTk).
    Tudo acontece aqui dentro: telas, botões, lógica de login e conversão.
    """
    def __init__(self): # Configurações iniciais: Título, banco de dados, taxas de câmbio e tela de login.
        super().__init__() # Aciona a inicialização da janela básica do CustomTkinter/Tkinter para que possamos customizá-la. 

        self.title("FinancePro Sessions - 2026")
        self.configure(fg_color=COLOR_BG)

        # 2. Comando que diz ao sistema operacional para abrir a janela MAXIMIZADA:
        self.state("zoomed") 

        self.arquivo_dados = "database.json"                                                                         

        # Puxa os dados salvos no computador (se existirem)
        self.carregar_dados_json()
        
        self.perfil_logado = None # Ninguém está logado quando o app abre
        self.iof_cartao = 4.38    # Imposto fixo brasileiro para compras internacionais
        
        # Dicionário com as moedas que o app aceita e suas respectivas bandeiras
        self.bandeiras = {
            "BRL": "🇧🇷", "USD": "🇺🇸", "EUR": "🇪🇺", 
            "GBP": "🇬🇧", "JPY": "🇯🇵", "CHF": "🇨🇭", 
            "CAD": "🇨🇦", "AUD": "🇦🇺"
        }
        
        # Inicia todas as taxas valendo 1.0. Elas serão atualizadas via internet em breve.
        self.taxas = {moeda: 1.0 for moeda in self.bandeiras.keys()}

        # Desenha a primeira tela que o usuário vê (A tela de Login)
        self.render_tela_login_principal()
        
        """
        TRABALHANDO EM SEGUNDO PLANO (THREADS)
        Se tentássemos baixar as taxas da internet agora, o aplicativo ia 
        congelar até o download terminar. Ao usar uma 'Thread', criamos um 
        'assistente' que vai buscar os dados na internet silenciosamente enquanto 
        o usuário já pode interagir com a tela de login.
        """
        thread_sync = threading.Thread(target=lambda: self.sincronizar_sistema(), daemon=True)
        thread_sync.start()

    def gerar_hash(self, senha):
        """
        SISTEMA DE SEGURANÇA (CRIPTOGRAFIA IRREVERSÍVEL)
        Recebe uma senha (ex: "1234") e a transforma em um texto bagunçado e seguro 
        (ex: "03ac674216f3e15c..."). Nem mesmo o dono do sistema consegue 
        descobrir qual era a senha original lendo o arquivo salvo.
        """
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    def carregar_dados_json(self):
        """
        LENDO O ARQUIVO DO COMPUTADOR
        O app procura o arquivo 'database.json'. Se achar, ele lê e guarda na memória.
        Se for a primeira vez que o app é aberto (o arquivo não existe), 
        ele cria um usuário 'Admin' com a senha '1234' por padrão.
        """
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                self.usuarios = json.load(f)
        else:
            senha_admin_hash = self.gerar_hash("1234")
            # Cria a estrutura padrão: Nome do usuário, sua senha secreta e um histórico vazio
            self.usuarios = {"Admin": {"pin": senha_admin_hash, "historico": []}}
            self.salvar_dados_json()

    def salvar_dados_json(self):
        """
        SALVANDO AS INFORMAÇÕES NO COMPUTADOR
        Pega tudo que aconteceu no app (novos perfis, novas conversões) 
        e grava fisicamente no arquivo 'database.json'.
        """
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, indent=4, ensure_ascii=False)

    def sincronizar_sistema(self):
        """
        Função centralizadora acionada pelo 'assistente' (Thread) 
        para buscar cotações da internet sem travar a tela.
        """
        self.buscar_taxas_api()

    def render_tela_login_principal(self):
        """
        DESENHANDO A TELA DE LOGIN
        O comando 'winfo_children().destroy()' atua como um apagador de quadro negro.
        Ele limpa qualquer coisa que estivesse na tela para desenhar o Login do zero.
        """
        for widget in self.winfo_children():
            widget.destroy()

        # Cria uma caixa retangular centralizada para colocar os botões dentro
        self.f_login_main = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=20, width=400, height=520)
        self.f_login_main.place(relx=0.5, rely=0.5, anchor="center")
        self.f_login_main.pack_propagate(0) # Força a caixa a não mudar de tamanho

        # Título e ícone
        ctk.CTkLabel(self.f_login_main, text="🏦", font=("Segoe UI", 60)).pack(pady=(40, 10))
        ctk.CTkLabel(self.f_login_main, text="Login Financeiro", font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(pady=10)
        ctk.CTkLabel(self.f_login_main, text="Selecione seu Perfil:", font=("Segoe UI", 12), text_color=COLOR_TEXT).pack(pady=(20, 0))
        
        # Caixa de seleção com os nomes dos usuários cadastrados
        self.cb_perfil = ctk.CTkComboBox(
            self.f_login_main, values=list(self.usuarios.keys()), width=250, 
            fg_color=COLOR_BG, border_color=COLOR_BORDER, 
            text_color=COLOR_TEXT, dropdown_text_color=COLOR_TEXT, dropdown_fg_color=COLOR_CARD
        )
        self.cb_perfil.pack(pady=10)

        # Campo para digitar a senha (oculta por asteriscos devido ao show="*")
        self.entry_pin = ctk.CTkEntry(
            self.f_login_main, placeholder_text="Digite seu PIN", show="*", width=250, 
            justify="center", fg_color=COLOR_BG, border_color=COLOR_BORDER, text_color=COLOR_TEXT
        )
        self.entry_pin.pack(pady=10)

        # Botão que chama a função de verificar se a senha está correta
        ctk.CTkButton(self.f_login_main, text="ENTRAR", fg_color=COLOR_ACCENT, text_color=COLOR_BG, 
                      font=("Segoe UI", 14, "bold"), command=self.autenticar_usuario).pack(pady=20)

        # Mini menu de rodapé para criar ou excluir usuários
        f_perfil_acoes = ctk.CTkFrame(self.f_login_main, fg_color="transparent")
        f_perfil_acoes.pack()

        ctk.CTkButton(f_perfil_acoes, text="+ Criar Perfil", fg_color="transparent", text_color=COLOR_TEXT_DIM,
                      width=100, command=self.janela_criar_perfil).pack(side="left")
        
        ctk.CTkButton(f_perfil_acoes, text="🗑 Excluir Perfil", fg_color="transparent", text_color=COLOR_ERROR,
                      width=100, command=self.janela_excluir_perfil).pack(side="left")

    def autenticar_usuario(self):
        """
        VERIFICANDO SE A SENHA ESTÁ CORRETA
        Como não guardamos a senha original, nós transformamos a senha que 
        o usuário acabou de digitar em 'hash' e comparamos com o 'hash' que 
        está salvo no banco de dados. Se forem iguais, ele entra.
        """
        nome = self.cb_perfil.get()
        pin_digitado = self.entry_pin.get()
        pin_hash = self.gerar_hash(pin_digitado) 

        # Verifica se o usuário existe e se a senha criptografada bate
        if nome in self.usuarios and self.usuarios[nome]["pin"] == pin_hash:
            self.perfil_logado = nome # Memoriza quem está usando o app agora
            self.setup_main_ui()      # Desenha a tela principal do app
        else:
            messagebox.showerror("Segurança", "Credenciais incorretas!")

    def janela_criar_perfil(self):
        """
        CADASTRANDO NOVO USUÁRIO
        Abre uma janelinha por cima da tela principal (Toplevel) para pegar
        um novo nome e senha. Criptografa a senha antes de salvar.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Novo Perfil")
        dialog.geometry("300x280")
        dialog.configure(fg_color=COLOR_BG)
        dialog.attributes("-topmost", True) # Garante que a janelinha fique sempre na frente

        # Campos de texto para nome e senha
        ctk.CTkLabel(dialog, text="Nome do Usuário:", text_color=COLOR_TEXT).pack(pady=(20,0))
        nome_ent = ctk.CTkEntry(dialog, text_color=COLOR_TEXT, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        nome_ent.pack(pady=5)

        ctk.CTkLabel(dialog, text="PIN (4 dígitos):", text_color=COLOR_TEXT).pack(pady=(10,0))
        pin_ent = ctk.CTkEntry(dialog, show="*", text_color=COLOR_TEXT, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        pin_ent.pack(pady=5)

        def salvar():
            # Limpa espaços vazios digitados sem querer
            nome, pin = nome_ent.get().strip(), pin_ent.get().strip()
            if nome and pin: # Verifica se não deixou em branco
                if nome not in self.usuarios:
                    pin_hash = self.gerar_hash(pin) 
                    self.usuarios[nome] = {"pin": pin_hash, "historico": []}
                    self.salvar_dados_json() # Salva no HD do PC
                    
                    # Atualiza a caixa de seleção de usuários com o novo nome
                    self.cb_perfil.configure(values=list(self.usuarios.keys()))
                    dialog.destroy() # Fecha a janelinha
                    messagebox.showinfo("Sucesso", "Perfil cadastrado e criptografado!")
                else:
                    messagebox.showerror("Erro", "Usuário já existe!")
            else:
                messagebox.showwarning("Erro", "Preencha tudo!")

        ctk.CTkButton(dialog, text="CADASTRAR", fg_color=COLOR_SUCCESS, command=salvar).pack(pady=25)

    def janela_excluir_perfil(self):
        """
        EXCLUINDO UM USUÁRIO (SISTEMA DE CHAVE-MESTRA)
        Para impedir que qualquer um exclua perfis, você precisa digitar 
        ou a senha do perfil que será excluído, ou a senha do 'Admin' 
        (que funciona como uma chave-mestra).
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Excluir Perfil")
        dialog.geometry("320x320")
        dialog.configure(fg_color=COLOR_BG)
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Qual perfil deseja excluir?", text_color=COLOR_TEXT).pack(pady=(20,0))
        
        # Cria lista de opções, mas esconde o 'Admin' para que ele nunca seja excluído
        cb_del = ctk.CTkComboBox(
            dialog, values=[u for u in self.usuarios.keys() if u != "Admin"], width=200,
            text_color=COLOR_TEXT, dropdown_text_color=COLOR_TEXT, dropdown_fg_color=COLOR_CARD, 
            fg_color=COLOR_BG, border_color=COLOR_BORDER
        )
        cb_del.pack(pady=5)

        ctk.CTkLabel(dialog, text="Confirmação de Segurança", font=("Segoe UI", 11, "bold"), text_color=COLOR_ACCENT).pack(pady=(15,0))
        ctk.CTkLabel(dialog, text="PIN do Usuário (Ou PIN do Admin):", text_color=COLOR_TEXT_DIM, font=("Segoe UI", 9)).pack()
        
        pin_ent = ctk.CTkEntry(dialog, show="*", width=200, text_color=COLOR_TEXT, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        pin_ent.pack(pady=5)

        def confirmar_exclusao():
            alvo = cb_del.get()
            pin_informado_hash = self.gerar_hash(pin_ent.get()) 
            pin_admin_hash = self.usuarios["Admin"]["pin"]
            pin_alvo_hash = self.usuarios[alvo]["pin"] if alvo in self.usuarios else ""

            # Lógica: Se o pin bate com o do Admin OU com o do usuário alvo, ele permite
            if pin_informado_hash == pin_admin_hash or pin_informado_hash == pin_alvo_hash:
                if messagebox.askyesno("Atenção", f"Excluir definitivamente o perfil {alvo}?"):
                    del self.usuarios[alvo] # Remove o dado da memória
                    self.salvar_dados_json() # Salva a remoção no HD
                    self.cb_perfil.configure(values=list(self.usuarios.keys()))
                    dialog.destroy()
                    messagebox.showinfo("Sucesso", "Perfil removido com sucesso!")
            else:
                messagebox.showerror("Segurança", "PIN Inválido! Operação negada.")

        ctk.CTkButton(dialog, text="EXCLUIR PERFIL", fg_color=COLOR_ERROR, command=confirmar_exclusao).pack(pady=25)

    def setup_main_ui(self):
        """
        DESENHANDO O APLICATIVO PÓS-LOGIN
        Apaga a tela de login e desenha o cabeçalho (com o nome do usuário)
        e o sistema de abas (Conversor e Histórico).
        """
        for widget in self.winfo_children():
            widget.destroy()

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=(25, 10), padx=30, fill="x")
        
        # Saudação e botão de Sair (Logout)
        f_user = ctk.CTkFrame(self.header, fg_color="transparent")
        f_user.pack(side="left")
        ctk.CTkLabel(f_user, text=f"👤 {self.perfil_logado}", font=("Segoe UI", 16, "bold"), text_color=COLOR_ACCENT).pack(side="left")
        ctk.CTkButton(f_user, text="Sair", width=40, height=20, fg_color=COLOR_ERROR, command=self.render_tela_login_principal).pack(side="left", padx=10)

        # Indicador de funcionamento online
        self.lbl_status = ctk.CTkLabel(self.header, text="● Câmbio Online", font=("Segoe UI", 9), text_color=COLOR_SUCCESS)
        self.lbl_status.pack(side="right")

        # Criação das duas abas principais
        self.abas = ctk.CTkTabview(self, width=470, height=620, corner_radius=25, fg_color=COLOR_CARD,
                                    segmented_button_selected_color=COLOR_ACCENT, segmented_button_fg_color=COLOR_BG, text_color=COLOR_TEXT)
        self.abas.pack(pady=10, padx=20)
        
        self.tab_conv = self.abas.add("CONVERSOR")
        self.tab_hist = self.abas.add("HISTÓRICO")

        # Chama as funções que preenchem cada aba com conteúdo
        self.render_conversor()
        self.render_historico_logado()

    def render_conversor(self):
        """
        A ABA DA CALCULADORA (CONVERSOR)
        Onde a mágica acontece. Cria o espaço para o usuário digitar o valor,
        escolher as moedas e ver os cartões bonitos de resultado.
        """
        ctk.CTkLabel(self.tab_conv, text="VALOR PARA CONVERSÃO", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=(20, 5))
        
        # Onde o usuário digita os números
        self.entry_valor = ctk.CTkEntry(
            self.tab_conv, placeholder_text="0.00", width=340, height=60, 
            font=("Segoe UI", 30, "bold"), justify="center",
            text_color=COLOR_TEXT, fg_color=COLOR_BG, border_color=COLOR_BORDER
        )
        self.entry_valor.pack(pady=5)

        # Container para colocar os seletores de moeda lado a lado (em grade/grid)
        f_moedas = ctk.CTkFrame(self.tab_conv, fg_color="transparent")
        f_moedas.pack(pady=10)
        
        lista_moedas = sorted(list(self.bandeiras.keys()))
        
        # Moeda que eu TENHO (Origem)
        self.cb_orig = ctk.CTkComboBox(
            f_moedas, values=lista_moedas, width=120, 
            text_color=COLOR_TEXT, dropdown_text_color=COLOR_TEXT, dropdown_fg_color=COLOR_CARD, 
            fg_color=COLOR_BG, border_color=COLOR_BORDER
        )
        self.cb_orig.set("USD")
        self.cb_orig.grid(row=0, column=0, padx=8)

        # Botão central para inverter as moedas rapidamente (Ex: de USD->BRL para BRL->USD)
        self.btn_swap = ctk.CTkButton(f_moedas, text="⇄", width=45, height=45, corner_radius=22, fg_color=COLOR_BG, hover_color=COLOR_ACCENT, border_width=1, border_color=COLOR_BORDER, text_color=COLOR_TEXT, command=self.inverter_moedas)
        self.btn_swap.grid(row=0, column=1, padx=5)

        # Moeda que eu QUERO (Destino)
        self.cb_dest = ctk.CTkComboBox(
            f_moedas, values=lista_moedas, width=120, 
            text_color=COLOR_TEXT, dropdown_text_color=COLOR_TEXT, dropdown_fg_color=COLOR_CARD, 
            fg_color=COLOR_BG, border_color=COLOR_BORDER
        )
        self.cb_dest.set("BRL")
        self.cb_dest.grid(row=0, column=2, padx=8)

        # Botão gigante que aciona o cálculo matemático
        ctk.CTkButton(self.tab_conv, text="CONVERTER", command=self.converter, height=55, width=340, font=("Segoe UI", 16, "bold"), fg_color=COLOR_ACCENT, text_color=COLOR_BG).pack(pady=15)

        # Área para mostrar os resultados
        self.res_frame = ctk.CTkFrame(self.tab_conv, fg_color="transparent")
        self.res_frame.pack(fill="both", expand=True, padx=20)

        # Usa uma função "atalho" (criar_card_resultado) para não repetir código
        self.card_bruto = self.criar_card_resultado(self.res_frame, "VALOR COMERCIAL", COLOR_BORDER)
        self.lbl_res_bruto = self.card_bruto._label_resultado

        self.card_iof = self.criar_card_resultado(self.res_frame, f"TOTAL COM IOF ({self.iof_cartao}%)", COLOR_ERROR)
        self.lbl_res_iof = self.card_iof._label_resultado

    def render_historico_logado(self):
        """
        ABA DE HISTÓRICO
        Este é um painel rolável (Scrollable) que lista apenas as operações
        feitas pelo usuário que está logado no momento. Privacidade em 1º lugar.
        """
        f_top = ctk.CTkFrame(self.tab_hist, fg_color="transparent")
        f_top.pack(fill="x", padx=20, pady=15)
        
        # Botões de ação do histórico
        ctk.CTkButton(f_top, text="Limpar", width=80, fg_color=COLOR_ERROR, text_color=COLOR_TEXT, command=self.limpar_historico).pack(side="right", padx=5)
        ctk.CTkButton(f_top, text="CSV", width=80, fg_color=COLOR_SUCCESS, text_color=COLOR_BG, command=self.exportar_csv).pack(side="right")
        
        # Área onde entraremos com as linhas do histórico
        self.scroll = ctk.CTkScrollableFrame(self.tab_hist, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10)
        
        # Puxa o histórico específico do usuário e recria os cartões na tela
        for dado in self.usuarios[self.perfil_logado]["historico"]:
            self.adicionar_card_historico(dado)

    def criar_card_resultado(self, master, titulo, cor_borda):
        """
        CRIADOR DE CAIXAS DE RESULTADO
        Uma mini fábrica de criar os painéis onde o valor convertido aparece.
        Como precisamos de duas (Uma pro Valor e outra pro Imposto), criamos
        essa função para economizar linhas de código.
        """
        card = ctk.CTkFrame(master, fg_color=COLOR_BG, corner_radius=15, border_width=1, border_color=cor_borda)
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=(10, 0))
        lbl = ctk.CTkLabel(card, text="---", font=("Segoe UI", 28, "bold"), text_color=COLOR_TEXT)
        lbl.pack(pady=(0, 10))
        card._label_resultado = lbl # Armazena o texto num 'bolso' secreto para mudarmos depois
        return card

    def converter(self):
        """
        A MATEMÁTICA E O REGISTRO DO SISTEMA
        Lê o número digitado, faz a conversão cruzada via Real (BRL),
        soma o imposto do governo e, se tudo der certo, salva isso no histórico.
        """
        try:
            # Substitui vírgula por ponto, porque o Python só entende decimais com ponto (Ex: 10.50)
            val_raw = self.entry_valor.get().strip().replace(',', '.')
            if not val_raw: return
            valor = float(val_raw)
            orig, dest = self.cb_orig.get(), self.cb_dest.get()
            
            # Regra de Três da Conversão: 
            # Multiplica pelo valor da moeda original e divide pela moeda desejada.
            bruto = (valor * self.taxas[orig]) / self.taxas[dest]
            
            # Adiciona o IOF (Imposto sobre Operações Financeiras)
            total = bruto + (bruto * (self.iof_cartao / 100))
            
            # Atualiza os textos gigantes na tela com o resultado formatado em 2 casas decimais (.2f)
            self.lbl_res_bruto.configure(text=f"{self.bandeiras[dest]} {bruto:.2f}")
            self.lbl_res_iof.configure(text=f"{self.bandeiras[dest]} {total:.2f}")
            
            # Cria um "pacote de dados" contendo: Data, Moeda1, Valor1, Moeda2, ValorConvertido, ValorComImposto
            dado = [datetime.now().strftime("%d/%m/%Y | %H:%M"), orig, valor, dest, bruto, total]
            
            # Insere no topo da lista (posição 0) do usuário atual e salva
            self.usuarios[self.perfil_logado]["historico"].insert(0, dado)
            self.salvar_dados_json()
            
            # Mostra esse pacote visualmente na aba de Histórico
            self.adicionar_card_historico(dado)
        except:
            # Caso o usuário digite letras (Ex: "abc") em vez de números, o sistema não trava
            messagebox.showerror("Erro", "Entrada inválida! Digite apenas números.")

    def adicionar_card_historico(self, dado):
        """
        CRIADOR VISUAL DAS LINHAS DE HISTÓRICO
        Recebe um "pacote de dados" da conversão e transforma isso
        em uma barrinha bonitinha na tela, cheia de bandeiras.
        """
        card = ctk.CTkFrame(self.scroll, fg_color=COLOR_BG, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        card.pack(pady=6, padx=5, fill="x")
        
        # Formata o texto. Ex: 🇺🇸 100 USD ➔ 🇧🇷 500.00 BRL
        txt = f"{self.bandeiras[dado[1]]} {dado[2]} {dado[1]} ➔ {self.bandeiras[dado[3]]} {dado[4]:.2f} {dado[3]}"
        
        ctk.CTkLabel(card, text=txt, font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(card, text=f"Data: {dado[0]}", font=("Segoe UI", 9), text_color=COLOR_ACCENT).pack(anchor="w", padx=15, pady=(0, 10))

    def buscar_taxas_api(self):
        """
        COMUNICAÇÃO COM O MUNDO EXTERIOR (INTERNET)
        Bate na porta do servidor do AwesomeAPI e pede as cotações do dia.
        Ele devolve um dicionário enorme, o código lê, extrai o que importa
        e atualiza o dicionário 'self.taxas' do nosso programa.
        """
        try:
            # Pega todas as moedas, menos o BRL, e monta o link. Ex: USD-BRL,EUR-BRL
            moedas = [m for m in self.bandeiras.keys() if m != "BRL"]
            query = ",".join([f"{m}-BRL" for m in moedas])
            
            # Faz a requisição na internet. O 'timeout=5' diz: "Se a net cair, desista após 5 segundos"
            r = requests.get(f"https://economia.awesomeapi.com.br/last/{query}", timeout=5)
            
            # Código 200 significa "Sucesso Absoluto" na linguagem da internet
            if r.status_code == 200:
                data = r.json()
                for m in moedas:
                    chave = f"{m}BRL"
                    # Atualiza a memória interna com o valor de compra ('bid') atual
                    if chave in data: self.taxas[m] = float(data[chave]['bid'])
        except: 
            pass # Se o PC estiver sem internet, ele não faz nada e mantém a taxa padrão de 1.0

    def limpar_historico(self):
        """
        LIXEIRA SEGURA
        Limpa a lista na memória e apaga os elementos visuais, 
        mas pede confirmação antes (askyesno) para evitar acidentes.
        """
        if messagebox.askyesno("Limpar", "Apagar histórico pessoal?"):
            self.usuarios[self.perfil_logado]["historico"].clear()
            self.salvar_dados_json()
            
            # Varre os filhos da aba rolável destruindo um por um visualmente
            for w in self.scroll.winfo_children(): w.destroy()

    def inverter_moedas(self):
        """
        O truque clássico de trocar copos de mão.
        Guarda os valores originais, e depois inverte quem está onde.
        """
        o, d = self.cb_orig.get(), self.cb_dest.get()
        self.cb_orig.set(d)
        self.cb_dest.set(o)

    def exportar_csv(self):
        """
        GERAÇÃO DE RELATÓRIO P/ EXCEL
        Abre uma janela pedindo onde você quer salvar o arquivo.
        Pega a sua lista particular de conversões e escreve separando por vírgulas,
        formato perfeito para abrir depois no Excel ou Google Sheets.
        """
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Escreve a linha do cabeçalho
                writer.writerow(["Data", "De", "Valor", "Para", "Comercial", "Total"])
                # Escreve todos os dados logo abaixo
                writer.writerows(self.usuarios[self.perfil_logado]["historico"])

# Ponto de partida padrão do Python. Quando você roda o arquivo, o sistema começa a ler por aqui.
if __name__ == "__main__":
    app = FinancePro()
    app.mainloop() # Mantém o aplicativo aberto rodando infinitamente aguardando seus cliques