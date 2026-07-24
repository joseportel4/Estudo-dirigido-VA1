import pygame


class Dashboard:
    def __init__(self):
        self.LARGURA_CELULA = 35
        self.ALTURA_TELA = 720
        self.LARGURA_JOGO = 0
        self.LARGURA_PAINEL = 0

        self.COR_FUNDO = (15, 18, 25)
        self.COR_PAINEL = (22, 26, 36)
        self.COR_CARD = (32, 38, 50)
        self.BRANCO = (240, 240, 245)
        self.CINZA_TEXTO = (170, 180, 190)
        self.VERDE_GRAMA = (40, 50, 45)
        self.MARROM_LAMA = (80, 55, 35)
        self.OURO_CHOCOLATE = (255, 190, 50)
        self.VERMELHO_MINA = (220, 50, 60)
        self.AZUL_OBJETIVO = (0, 180, 255)

        pygame.font.init()
        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.fonte_texto = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.fonte_grande = pygame.font.SysFont("Consolas", 30, bold=True)
        self.fonte_gigante = pygame.font.SysFont("Segoe UI", 48, bold=True)

        self.fonte_mini_titulo = pygame.font.SysFont("Segoe UI", 20, bold=True)

    def _desenhar_icone_mina(self, tela, x, y, tamanho):
        centro = (x + tamanho // 2, y + tamanho // 2)
        pygame.draw.circle(tela, (20, 20, 20), centro, tamanho // 2.5)
        pygame.draw.line(tela, self.VERMELHO_MINA, (x + 8, y + 8), (x + tamanho - 8, y + tamanho - 8), 3)
        pygame.draw.line(tela, self.VERMELHO_MINA, (x + tamanho - 8, y + 8), (x + 8, y + tamanho - 8), 3)

    def _desenhar_icone_chocolate(self, tela, x, y, tamanho):
        pontos = [
            (x + tamanho // 2, y + 6),
            (x + tamanho - 6, y + tamanho // 2),
            (x + tamanho // 2, y + tamanho - 6),
            (x + 6, y + tamanho // 2)
        ]
        pygame.draw.polygon(tela, self.OURO_CHOCOLATE, pontos)

    def _gerar_surface_jogo(self, env, tempo, cor_agente):
        largura_pixel = env.largura * self.LARGURA_CELULA
        altura_pixel = self.ALTURA_TELA
        surface = pygame.Surface((largura_pixel, altura_pixel))
        surface.fill(self.COR_FUNDO)

        agente_py_visual = (env.comprimento - 1 - env.posicao_y) * self.LARGURA_CELULA
        offset_y = agente_py_visual - (self.ALTURA_TELA * 0.70)
        offset_y = max(0, min(env.comprimento * self.LARGURA_CELULA - self.ALTURA_TELA, offset_y))

        for y in range(env.comprimento):
            for x in range(env.largura):
                px = x * self.LARGURA_CELULA
                py_visual_absoluto = (env.comprimento - 1 - y) * self.LARGURA_CELULA
                py = py_visual_absoluto - offset_y

                if py < -self.LARGURA_CELULA or py > self.ALTURA_TELA:
                    continue

                terreno = env.mapa[y][x]
                cor_base = self.MARROM_LAMA if terreno == env.LAMA else self.VERDE_GRAMA
                rect_celula = (px, py, self.LARGURA_CELULA, self.LARGURA_CELULA)

                pygame.draw.rect(surface, cor_base, rect_celula)
                pygame.draw.rect(surface, (25, 30, 35), rect_celula, 1)

                if terreno == env.MINA:
                    self._desenhar_icone_mina(surface, px, py, self.LARGURA_CELULA)
                elif terreno == env.CHOCOLATE:
                    self._desenhar_icone_chocolate(surface, px, py, self.LARGURA_CELULA)
                elif terreno == env.OBJETIVO:
                    centro = (px + self.LARGURA_CELULA // 2, py + self.LARGURA_CELULA // 2)
                    pulso = abs((tempo % 1000) - 500) / 500.0
                    pygame.draw.circle(surface, self.AZUL_OBJETIVO, centro, int(self.LARGURA_CELULA // 2.5))
                    pygame.draw.circle(surface, self.AZUL_OBJETIVO, centro, int(self.LARGURA_CELULA // 2 * pulso), 2)

                if abs(x - env.posicao_x) > 2 or abs(y - env.posicao_y) > 2:
                    s_fog = pygame.Surface((self.LARGURA_CELULA, self.LARGURA_CELULA), pygame.SRCALPHA)
                    s_fog.fill((10, 12, 15, 200))
                    surface.blit(s_fog, (px, py))

        agente_px = env.posicao_x * self.LARGURA_CELULA
        py_agente = (env.comprimento - 1 - env.posicao_y) * self.LARGURA_CELULA - offset_y
        centro = (agente_px + self.LARGURA_CELULA // 2, py_agente + self.LARGURA_CELULA // 2)

        cor_exibida = self.OURO_CHOCOLATE if env.bonus_visual else cor_agente
        pygame.draw.circle(surface, cor_exibida, centro, self.LARGURA_CELULA // 2.5)
        pygame.draw.circle(surface, (20, 20, 20), centro, self.LARGURA_CELULA // 5)

        return surface

    def _desenhar_card(self, tela, x, y, largura, altura, titulo, valor, cor_valor):
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(tela, self.COR_CARD, rect, border_radius=10)

        img_titulo = self.fonte_texto.render(titulo, True, self.CINZA_TEXTO)
        tela.blit(img_titulo, (x + 15, y + 15))

        img_valor = self.fonte_grande.render(str(valor), True, cor_valor)
        tela.blit(img_valor, (x + 15, y + 45))

    def _desenhar_painel(self, tela, env, pontuacao, acao_str, status, modo, ag_instancia=None):
        pygame.draw.rect(tela, self.COR_PAINEL, (self.LARGURA_JOGO, 0, self.LARGURA_PAINEL, self.ALTURA_TELA))
        pygame.draw.line(tela, self.COR_CARD, (self.LARGURA_JOGO, 0), (self.LARGURA_JOGO, self.ALTURA_TELA), 5)

        margem_x = self.LARGURA_JOGO + 30
        img_titulo = self.fonte_titulo.render("TELEMETRIA DA SIMULAÇÃO", True, self.BRANCO)
        tela.blit(img_titulo, (margem_x, 30))
        pygame.draw.line(tela, self.CINZA_TEXTO, (margem_x, 75), (tela.get_width() - 30, 75), 1)

        largura_total = self.LARGURA_PAINEL - 60
        largura_metade = (largura_total - 20) // 2

        cor_status = self.VERDE_GRAMA if status == "Correndo" else (
            self.AZUL_OBJETIVO if "VITÓRIA" in status else self.VERMELHO_MINA)
        self._desenhar_card(tela, margem_x, 100, largura_total, 90, "STATUS DO AGENTE", status, cor_status)

        self._desenhar_card(tela, margem_x, 210, largura_metade, 90, "AVANÇO (EIXO Y)",
                            f"{env.posicao_y} / {env.comprimento - 1}", self.BRANCO)

        passos_restantes = env.limite_passos - env.passos_dados
        cor_bateria = self.VERMELHO_MINA if passos_restantes < (env.limite_passos * 0.2) else self.BRANCO
        self._desenhar_card(tela, margem_x + largura_metade + 20, 210, largura_metade, 90, "ENERGIA / PASSOS",
                            f"{passos_restantes}", cor_bateria)

        self._desenhar_card(tela, margem_x, 320, largura_metade, 90, "FITNESS (PONTOS)", f"{pontuacao}",
                            self.OURO_CHOCOLATE)
        self._desenhar_card(tela, margem_x + largura_metade + 20, 320, largura_metade, 90, "ÚLTIMA AÇÃO", acao_str,
                            self.AZUL_OBJETIVO)

        y_ia = 450
        pygame.draw.rect(tela, (25, 30, 42), (margem_x, y_ia, largura_total, 180), border_radius=10)
        pygame.draw.rect(tela, self.AZUL_OBJETIVO, (margem_x, y_ia, largura_total, 180), 2, border_radius=10)
        img_ia_titulo = self.fonte_texto.render("PARÂMETROS DE APRENDIZADO DA IA", True, self.AZUL_OBJETIVO)
        tela.blit(img_ia_titulo, (margem_x + 15, y_ia + 15))

        if modo == "IA_QLEARNING" and ag_instancia is not None:
            textos_ia = [f"Episódios Treinados: {ag_instancia.episodio_atual} / {ag_instancia.episodios_totais}",
                         f"Taxa Epsilon (Exploração): {ag_instancia.epsilon:.4f}",
                         f"Estados na Tabela Q: {len(ag_instancia.q_tabela)}", f"Semente do Mapa: {env.seed_atual}"]
        elif modo == "IA_ASTAR" and ag_instancia is not None:
            textos_ia = [f"Algoritmo: Heurístico (A-Estrela)", f"Personalidade Ativa:",
                         f"-> {ag_instancia.modo_selecionado}", f"Semente do Mapa: {env.seed_atual}"]
        else:
            textos_ia = ["Geração Atual: ---", "Melhor Fitness Global: ---", "Taxa de Exploração (Epsilon): ---",
                         "Penalidades Sofridas: ---"]

        for i, texto in enumerate(textos_ia):
            img_texto = self.fonte_texto.render(texto, True, self.CINZA_TEXTO)
            tela.blit(img_texto, (margem_x + 15, y_ia + 55 + (i * 28)))

        # --- MERGE: Atualização dos textos de rodapé (UX) ---
        if modo == "MANUAL":
            texto_rodape = "[Setas] Mover  |  [R] Reiniciar  |  [N] Avançar Nível  |  [ESC] Voltar"
        elif modo == "IA_ASTAR":
            texto_rodape = "[A] Iniciar | [1] Focado | [2] Equilibrado | [3] Guloso | [M] Novo Mapa | [ESC] Voltar"
        elif modo == "IA_GENETICO":
            texto_rodape = "[L] Continuar Treino |  [C] Injetar Cérebro Atual |  [ESC] Voltar"
        elif modo == "IA_QLEARNING":
            if env.dificuldade in ["FACIL", "MEDIO"]:
                texto_rodape = "[A] Executar  |  [R] Repetir  |  [M] Novo Mapa  |  [N] Subir Nível  |  [ESC] Voltar"
            else:
                texto_rodape = "[A] Executar  |  [R] Repetir  |  [M] Novo Mapa  |  [ESC] Voltar"
        elif modo == "IA_REPLAY":
            if env.dificuldade in ["FACIL", "MEDIO"]:
                texto_rodape = "[A] Iniciar Replay  |  [R] Repetir Replay  |  [N] Subir Nível  |  [ESC] Voltar"
            else:
                texto_rodape = "[A] Iniciar Replay  |  [R] Repetir Replay  |  [ESC] Voltar"
        else:
            texto_rodape = "[ESC] Voltar"

        img_dica = self.fonte_texto.render(texto_rodape, True, self.CINZA_TEXTO)
        tela.blit(img_dica, (margem_x, self.ALTURA_TELA - 40))

    def _desenhar_overlay_fim_jogo(self, tela, status, env, modo="MANUAL"):
        s_overlay = pygame.Surface((self.LARGURA_JOGO, self.ALTURA_TELA), pygame.SRCALPHA)
        s_overlay.fill((0, 0, 0, 180))
        tela.blit(s_overlay, (0, 0))
        cor = self.AZUL_OBJETIVO if "VITÓRIA" in status else self.VERMELHO_MINA
        texto = "OBJETIVO ALCANÇADO" if "VITÓRIA" in status else "AGENTE ABATIDO"
        img = self.fonte_gigante.render(texto, True, cor)
        rect = img.get_rect(center=(self.LARGURA_JOGO // 2, self.ALTURA_TELA // 2))

        pygame.draw.rect(tela, (20, 20, 25), rect.inflate(40, 40), border_radius=10)
        pygame.draw.rect(tela, cor, rect.inflate(40, 40), 2, border_radius=10)
        tela.blit(img, rect)

        if modo == "IA_QLEARNING":
            img_dica1 = self.fonte_texto.render("[ R / A ] Executar Novamente   |   [ M ] Mudar Mapa", True,
                                                self.BRANCO)
            rect_dica1 = img_dica1.get_rect(center=(self.LARGURA_JOGO // 2, (self.ALTURA_TELA // 2) + 55))
            tela.blit(img_dica1, rect_dica1)

            if env.dificuldade in ["FACIL", "MEDIO"]:
                prox_nivel = "MÉDIO" if env.dificuldade == "FACIL" else "DIFÍCIL"
                img_dica2 = self.fonte_texto.render(f"[ N ] Subir para Nível {prox_nivel}   |   [ ESC ] Sair", True,
                                                    self.OURO_CHOCOLATE)
            else:
                img_dica2 = self.fonte_texto.render("[ ESC ] Sair para Menu de Dificuldade", True, self.OURO_CHOCOLATE)

            rect_dica2 = img_dica2.get_rect(center=(self.LARGURA_JOGO // 2, (self.ALTURA_TELA // 2) + 85))
            tela.blit(img_dica2, rect_dica2)
        else:
            img_dica = self.fonte_texto.render("Pressione [ R ] para jogar novamente", True, self.BRANCO)
            rect_dica = img_dica.get_rect(center=(self.LARGURA_JOGO // 2, (self.ALTURA_TELA // 2) + 60))
            tela.blit(img_dica, rect_dica)

            if "VITÓRIA" in status and env.dificuldade in ["FACIL", "MEDIO"]:
                prox_nivel = "MÉDIO" if env.dificuldade == "FACIL" else "DIFÍCIL"
                img_next = self.fonte_texto.render(f"Pressione [ N ] para avançar ao nível {prox_nivel}", True,
                                                   self.OURO_CHOCOLATE)
                rect_next = img_next.get_rect(center=(self.LARGURA_JOGO // 2, (self.ALTURA_TELA // 2) + 90))
                tela.blit(img_next, rect_next)

    def renderizar_frame(self, tela, env, pontuacao, acao_str, status, modo="MANUAL", ag_instancia=None):
        self.LARGURA_JOGO = env.largura * self.LARGURA_CELULA
        self.LARGURA_PAINEL = tela.get_width() - self.LARGURA_JOGO

        tempo = pygame.time.get_ticks()
        surf_jogo = self._gerar_surface_jogo(env, tempo, self.BRANCO)
        tela.blit(surf_jogo, (0, 0))

        self._desenhar_painel(tela, env, pontuacao, acao_str, status, modo, ag_instancia)

        if status != "Correndo":
            self._desenhar_overlay_fim_jogo(tela, status, env, modo)

    def renderizar_arena(self, tela, lista_agentes, status_arena):
        tela.fill(self.COR_FUNDO)
        tempo = pygame.time.get_ticks()

        LARGURA_PAINEL_ARENA = 300
        LARGURA_GRID = tela.get_width() - LARGURA_PAINEL_ARENA
        ALTURA_GRID = self.ALTURA_TELA

        n = len(lista_agentes)
        if n <= 2:
            cols, rows = 2, 1
        elif n <= 4:
            cols, rows = 2, 2
        else:
            cols, rows = 3, 2

        cell_w = LARGURA_GRID // cols
        cell_h = ALTURA_GRID // rows

        for i, ag_data in enumerate(lista_agentes):
            cx = (i % cols) * cell_w
            cy = (i // cols) * cell_h

            surf_nativa = self._gerar_surface_jogo(ag_data['env'], tempo, ag_data['cor'])
            surf_escalada = pygame.transform.smoothscale(surf_nativa, (cell_w - 4, cell_h - 4))

            rect_moldura = pygame.Rect(cx, cy, cell_w, cell_h)
            pygame.draw.rect(tela, (40, 45, 55), rect_moldura)
            tela.blit(surf_escalada, (cx + 2, cy + 2))

            bg_nome = pygame.Surface((cell_w, 30))
            bg_nome.set_alpha(200)
            bg_nome.fill((10, 15, 20))
            tela.blit(bg_nome, (cx, cy))

            txt_nome = self.fonte_mini_titulo.render(ag_data['nome'], True, ag_data['cor'])
            tela.blit(txt_nome, (cx + 10, cy + 5))

            if ag_data['done']:
                s_dark = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                s_dark.fill((0, 0, 0, 150))
                tela.blit(s_dark, (cx, cy))

                txt_status = "VITÓRIA!" if ag_data['pontuacao'] > 0 else "FALHOU"
                cor_status = self.AZUL_OBJETIVO if ag_data['pontuacao'] > 0 else self.VERMELHO_MINA
                img_win = self.fonte_titulo.render(txt_status, True, cor_status)
                tela.blit(img_win, img_win.get_rect(center=(cx + cell_w // 2, cy + cell_h // 2)))

        px_inicio = LARGURA_GRID
        pygame.draw.rect(tela, self.COR_PAINEL, (px_inicio, 0, LARGURA_PAINEL_ARENA, self.ALTURA_TELA))
        pygame.draw.line(tela, self.COR_CARD, (px_inicio, 0), (px_inicio, self.ALTURA_TELA), 5)

        img_titulo = self.fonte_titulo.render("RANKING", True, self.BRANCO)
        tela.blit(img_titulo, (px_inicio + 20, 20))

        y_card = 80
        for ag in sorted(lista_agentes, key=lambda x: x['pontuacao'], reverse=True):
            pygame.draw.rect(tela, self.COR_CARD, (px_inicio + 15, y_card, LARGURA_PAINEL_ARENA - 30, 80),
                             border_radius=8)
            pygame.draw.circle(tela, ag['cor'], (px_inicio + 35, y_card + 40), 10)
            t_nome = self.fonte_texto.render(ag['nome'], True, self.BRANCO)
            tela.blit(t_nome, (px_inicio + 55, y_card + 15))

            passos = ag['env'].limite_passos - ag['env'].passos_dados
            t_status = self.fonte_texto.render(f"Pts: {ag['pontuacao']} | Bat: {passos}", True, self.CINZA_TEXTO)
            tela.blit(t_status, (px_inicio + 55, y_card + 40))
            y_card += 95

        rodape = "[A] Iniciar Corrida | [M] Novo Mapa | [ESC] Voltar"
        t_rodape = self.fonte_texto.render(rodape, True, self.CINZA_TEXTO)

        if t_rodape.get_width() > LARGURA_PAINEL_ARENA - 20:
            tela.blit(self.fonte_texto.render("[A] Iniciar | [M] Mudar", True, self.CINZA_TEXTO),
                      (px_inicio + 20, self.ALTURA_TELA - 60))
            tela.blit(self.fonte_texto.render("[ESC] Voltar", True, self.CINZA_TEXTO),
                      (px_inicio + 20, self.ALTURA_TELA - 35))
        else:
            tela.blit(t_rodape, (px_inicio + 20, self.ALTURA_TELA - 40))