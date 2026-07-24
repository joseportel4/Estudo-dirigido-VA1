import pygame


class MenuPrincipal:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura

        self.COR_FUNDO = (15, 18, 25)
        self.BRANCO = (240, 240, 245)
        self.CINZA = (100, 110, 120)
        self.AZUL_DESTAQUE = (0, 180, 255)
        self.OURO = (255, 190, 50)
        self.VERDE = (40, 200, 80)

        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.fonte_botoes = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fonte_sub = pygame.font.SysFont("Segoe UI", 16)

        largura_botao = 350
        altura_botao = 60
        centro_x = (self.largura // 2) - (largura_botao // 2)

        self.botoes_main = {
            "JOGAR_MANUAL": pygame.Rect(centro_x, 260, largura_botao, altura_botao),
            "TREINAMENTO_IA": pygame.Rect(centro_x, 340, largura_botao, altura_botao),
            "COMPARAR_AGENTES": pygame.Rect(centro_x, 420, largura_botao, altura_botao),
            "SAIR": pygame.Rect(centro_x, 500, largura_botao, altura_botao)
        }

        self.botoes_agentes = {
            "ASTAR": pygame.Rect(centro_x, 280, largura_botao, altura_botao),
            "GENETICO": pygame.Rect(centro_x, 370, largura_botao, altura_botao),
            "QLEARNING": pygame.Rect(centro_x, 460, largura_botao, altura_botao),
            "VOLTAR": pygame.Rect(centro_x, 570, largura_botao, altura_botao)
        }

        self.botoes_dificuldade = {
            "FACIL": pygame.Rect(centro_x, 280, largura_botao, altura_botao),
            "MEDIO": pygame.Rect(centro_x, 370, largura_botao, altura_botao),
            "DIFICIL": pygame.Rect(centro_x, 460, largura_botao, altura_botao),
            "VOLTAR": pygame.Rect(centro_x, 570, largura_botao, altura_botao)
        }

        # --- TELA DE COMPARAÇÃO (Múltipla Escolha) ---
        self.agentes_comparacao = {
            "A* Focado": False,
            "A* Equilibrado": False,
            "A* Guloso": False,
            "Algoritmo Genético": False,
            "Q-Learning": False
        }
        self.botoes_checkbox = {}
        y_start = 220
        for nome in self.agentes_comparacao.keys():
            self.botoes_checkbox[nome] = pygame.Rect(centro_x, y_start, largura_botao, 45)
            y_start += 60

        self.btn_iniciar_comp = pygame.Rect(centro_x, y_start + 20, largura_botao, altura_botao)
        self.btn_voltar_comp = pygame.Rect(centro_x, y_start + 90, largura_botao, altura_botao)

        self.botao_wip_voltar = pygame.Rect(centro_x, 500, largura_botao, altura_botao)
        self.botoes_galeria = []
        self.dados_galeria = []

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_main["JOGAR_MANUAL"].collidepoint(pos_mouse):
                    return "SELECIONAR_DIF_MANUAL"
                elif self.botoes_main["TREINAMENTO_IA"].collidepoint(pos_mouse):
                    return "ESTADO_SELECIONAR_AGENTE"
                elif self.botoes_main["COMPARAR_AGENTES"].collidepoint(pos_mouse):
                    return "ESTADO_SELECIONAR_COMPARACAO"
                elif self.botoes_main["SAIR"].collidepoint(pos_mouse):
                    return "SAIR"
        return "ESTADO_MENU"

    def desenhar(self, tela):
        tela.fill(self.COR_FUNDO)
        texto_titulo = self.fonte_titulo.render("RESGATE TÁTICO: IA", True, self.BRANCO)
        tela.blit(texto_titulo, texto_titulo.get_rect(center=(self.largura // 2, 130)))
        texto_sub = self.fonte_botoes.render("Selecione o Modo de Simulação", True, self.CINZA)
        tela.blit(texto_sub, texto_sub.get_rect(center=(self.largura // 2, 180)))
        self._desenhar_botoes(tela, self.botoes_main,
                              ["JOGAR_MANUAL", "TREINAMENTO_IA", "COMPARAR_AGENTES", "SAIR"],
                              ["Simulação Manual", "Painel de Agentes (IA)", "Arena: Comparar IAs", "Sair"])

    def processar_eventos_comparacao(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()

                for nome, rect in self.botoes_checkbox.items():
                    if rect.collidepoint(pos_mouse):
                        self.agentes_comparacao[nome] = not self.agentes_comparacao[nome]

                if self.btn_iniciar_comp.collidepoint(pos_mouse):
                    selecionados = [k for k, v in self.agentes_comparacao.items() if v]
                    if len(selecionados) > 0:
                        return "SELECIONAR_DIF_COMPARACAO"

                if self.btn_voltar_comp.collidepoint(pos_mouse):
                    return "ESTADO_MENU"
        return "ESTADO_SELECIONAR_COMPARACAO"

    def desenhar_selecao_comparacao(self, tela):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("ARENA DE COMPARAÇÃO", True, self.OURO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 100)))
        img_sub = self.fonte_botoes.render("Marque as inteligências que deseja testar simultaneamente:", True,
                                           self.BRANCO)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 150)))

        pos_mouse = pygame.mouse.get_pos()

        # Desenhar Checkboxes
        for nome, rect in self.botoes_checkbox.items():
            ativo = self.agentes_comparacao[nome]
            cor_borda = self.AZUL_DESTAQUE if ativo else self.CINZA
            cor_fundo = (35, 42, 55) if rect.collidepoint(pos_mouse) else self.COR_FUNDO

            pygame.draw.rect(tela, cor_fundo, rect, border_radius=8)
            pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=8)

            # Caixa do check
            check_rect = pygame.Rect(rect.x + 15, rect.y + 12, 20, 20)
            pygame.draw.rect(tela, cor_borda, check_rect, 2)
            if ativo:
                pygame.draw.rect(tela, self.AZUL_DESTAQUE, check_rect.inflate(-6, -6))

            texto = self.fonte_botoes.render(nome, True, self.BRANCO if ativo else self.CINZA)
            tela.blit(texto, (rect.x + 50, rect.y + 7))

        # Botão Iniciar
        selecionados = [k for k, v in self.agentes_comparacao.items() if v]
        cor_iniciar = self.VERDE if len(selecionados) > 0 else (50, 50, 50)
        pygame.draw.rect(tela, cor_iniciar, self.btn_iniciar_comp, border_radius=8)
        txt_iniciar = self.fonte_botoes.render("Avançar para Dificuldade ->", True,
                                               self.COR_FUNDO if len(selecionados) > 0 else self.CINZA)
        tela.blit(txt_iniciar, txt_iniciar.get_rect(center=self.btn_iniciar_comp.center))

        # Botão Voltar
        pygame.draw.rect(tela, (35, 42, 55), self.btn_voltar_comp, border_radius=8)
        pygame.draw.rect(tela, self.CINZA, self.btn_voltar_comp, 2, border_radius=8)
        txt_voltar = self.fonte_botoes.render("<- Voltar", True, self.BRANCO)
        tela.blit(txt_voltar, txt_voltar.get_rect(center=self.btn_voltar_comp.center))

    def processar_eventos_agentes(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_agentes["ASTAR"].collidepoint(pos_mouse):
                    return "ASTAR"
                elif self.botoes_agentes["GENETICO"].collidepoint(pos_mouse):
                    return "GENETICO"
                elif self.botoes_agentes["QLEARNING"].collidepoint(pos_mouse):
                    return "QLEARNING"
                elif self.botoes_agentes["VOLTAR"].collidepoint(pos_mouse):
                    return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_agentes(self, tela):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("TREINAMENTO DE IA", True, self.BRANCO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 120)))
        img_sub = self.fonte_botoes.render("Selecione o Modelo de Inteligência Artificial", True, self.AZUL_DESTAQUE)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 170)))
        self._desenhar_botoes(tela, self.botoes_agentes, ["ASTAR", "GENETICO", "QLEARNING", "VOLTAR"],
                              ["Agente A* (Busca)", "Algoritmo Genético", "Q-Learning (RL)", "<- Voltar ao Menu"])

    def processar_eventos_wip(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.botao_wip_voltar.collidepoint(pygame.mouse.get_pos()): return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_em_desenvolvimento(self, tela, nome_agente):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("EM CONSTRUÇÃO", True, self.OURO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 250)))
        img_sub = self.fonte_botoes.render(f"A integração do modelo {nome_agente} será disponibilizada em breve.", True,
                                           self.CINZA)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 320)))
        self._desenhar_botoes(tela, {"VOLTAR": self.botao_wip_voltar}, ["VOLTAR"], ["<- Voltar"])

    def processar_eventos_dificuldade(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_dificuldade["FACIL"].collidepoint(pos_mouse):
                    return "FACIL"
                elif self.botoes_dificuldade["MEDIO"].collidepoint(pos_mouse):
                    return "MEDIO"
                elif self.botoes_dificuldade["DIFICIL"].collidepoint(pos_mouse):
                    return "DIFICIL"
                elif self.botoes_dificuldade["VOLTAR"].collidepoint(pos_mouse):
                    return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_dificuldade(self, tela, modo_origem):
        tela.fill(self.COR_FUNDO)
        titulo_texto = "SIMULAÇÃO MANUAL" if modo_origem == "MANUAL" else (
            "ARENA DE IAs" if modo_origem == "COMPARACAO" else "TREINAMENTO DE IA")
        img_titulo = self.fonte_titulo.render(titulo_texto, True, self.BRANCO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 120)))
        self._desenhar_botoes(tela, self.botoes_dificuldade, ["FACIL", "MEDIO", "DIFICIL", "VOLTAR"],
                              ["Modo Fácil", "Modo Médio", "Modo Difícil", "<- Voltar"])

    def desenhar_treinamento_ag(self, tela, dados_geracao):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("Evoluindo População...", True, self.OURO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 250)))

        texto = f"Geração: {dados_geracao['geracao']}  |  Melhor Fitness: {dados_geracao['fitness_campeao']:.0f}  |  Taxa Sobrevivência: {dados_geracao['taxa_sucesso'] * 100:.1f}%"
        img_sub = self.fonte_botoes.render(texto, True, self.BRANCO)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 320)))

        img_aviso = self.fonte_sub.render(
            "Os cálculos pesados estão ocorrendo em background. Pressione [ESC] para abortar.", True, self.CINZA)
        tela.blit(img_aviso, img_aviso.get_rect(center=(self.largura // 2, 400)))

    def desenhar_treinamento_ql(self, tela, dados_episodio, total_episodios):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("Treinando Q-Learning...", True, self.AZUL_DESTAQUE)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 230)))

        if dados_episodio:
            ep = dados_episodio.get('episodio', 0)
            eps = dados_episodio.get('epsilon', 0.0)
            max_y = dados_episodio.get('max_y_alcançado', 0)
            pct = int((ep / max(1, total_episodios)) * 100)

            texto = f"Episódio: {ep} / {total_episodios} ({pct}%) | Epsilon: {eps:.4f} | Máx Y: {max_y}"
            img_sub = self.fonte_botoes.render(texto, True, self.BRANCO)
            tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 310)))

            largura_barra = 600
            altura_barra = 20
            x_barra = (self.largura - largura_barra) // 2
            y_barra = 370
            pygame.draw.rect(tela, (35, 42, 55), (x_barra, y_barra, largura_barra, altura_barra), border_radius=10)
            largura_preenchida = int((pct / 100.0) * largura_barra)
            if largura_preenchida > 0:
                pygame.draw.rect(tela, self.AZUL_DESTAQUE,
                                 (x_barra, y_barra, min(largura_barra, largura_preenchida), altura_barra),
                                 border_radius=10)
            pygame.draw.rect(tela, self.CINZA, (x_barra, y_barra, largura_barra, altura_barra), 2, border_radius=10)

        img_aviso = self.fonte_sub.render(
            "Treinamento tabular por Aprendizado por Reforço. Pressione [ESC] para abortar.", True, self.CINZA)
        tela.blit(img_aviso, img_aviso.get_rect(center=(self.largura // 2, 440)))

    def _desenhar_botoes(self, tela, dic_botoes, chaves, textos):
        pos_mouse = pygame.mouse.get_pos()
        for i, chave in enumerate(chaves):
            rect = dic_botoes[chave]
            if rect.collidepoint(pos_mouse):
                pygame.draw.rect(tela, self.AZUL_DESTAQUE, rect, border_radius=8)
                cor_texto = self.COR_FUNDO
            else:
                pygame.draw.rect(tela, (35, 42, 55), rect, border_radius=8)
                pygame.draw.rect(tela, self.CINZA, rect, 2, border_radius=8)
                cor_texto = self.BRANCO
            texto_btn = self.fonte_botoes.render(textos[i], True, cor_texto)
            tela.blit(texto_btn, texto_btn.get_rect(center=rect.center))