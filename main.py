import pygame
import sys
import os
from environment import CampoBatalhaEnv
from interface.dashboard import Dashboard
from interface.menu import MenuPrincipal
from agent_astar import AgenteAStar
from agent_genetic import AlgoritmoGenetico
from agent_qlearning import AgenteQLearning


def main():
    pygame.init()

    LARGURA_TELA = 1280
    ALTURA_TELA = 720
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Resgate Tático: Inteligência Artificial")

    menu = MenuPrincipal(LARGURA_TELA, ALTURA_TELA)
    dashboard = Dashboard()

    env = CampoBatalhaEnv(dificuldade="MEDIO")

    estado_atual = "ESTADO_MENU"
    pontuacao = 0
    status_jogo = "Correndo"
    acao_str = "Aguardando..."

    agente_selecionado = None
    ag_instancia = None
    geracao_alvo_ag = 150

    ia_em_execucao = False
    rota_ia = []
    cerebro_carregado = None
    visitados_ag = set()  # Memória runtime do AG
    qlearning_pronto = False

    # --- VARIÁVEIS DA ARENA DE COMPARAÇÃO ---
    lista_comparacao = []
    comparacao_em_andamento = False

    CORES_AGENTES = {
        "A* Focado": (50, 150, 255),  # Azul
        "A* Equilibrado": (180, 50, 255),  # Roxo
        "A* Guloso": (255, 100, 50),  # Laranja
        "Algoritmo Genético": (50, 255, 100),  # Verde
        "Q-Learning": (255, 50, 100)  # Rosa/Vermelho
    }

    estado_ia = None
    indice_rota = 0
    delay_passo_ia = 150
    ultimo_tempo_mov = 0

    relogio = pygame.time.Clock()

    while True:
        tempo_atual = pygame.time.get_ticks()
        eventos = pygame.event.get()

        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if estado_atual == "ESTADO_MENU":
            novo_estado = menu.processar_eventos(eventos)
            if novo_estado == "SAIR":
                pygame.quit()
                sys.exit()
            elif novo_estado in ["SELECIONAR_DIF_MANUAL", "ESTADO_SELECIONAR_AGENTE", "ESTADO_SELECIONAR_COMPARACAO"]:
                estado_atual = novo_estado
            menu.desenhar(tela)

        elif estado_atual == "ESTADO_SELECIONAR_AGENTE":
            escolha_agente = menu.processar_eventos_agentes(eventos)
            if escolha_agente == "VOLTAR":
                estado_atual = "ESTADO_MENU"
            elif escolha_agente in ["ASTAR", "GENETICO"]:
                agente_selecionado = "A*" if escolha_agente == "ASTAR" else "Algoritmo Genético"
                estado_atual = "SELECIONAR_DIF_IA"
            elif escolha_agente == "QLEARNING":
                agente_selecionado = "Q-Learning"
                estado_atual = "SELECIONAR_DIF_IA"
            menu.desenhar_agentes(tela)

        # --- NOVA ROTA: SELEÇÃO DA ARENA ---
        elif estado_atual == "ESTADO_SELECIONAR_COMPARACAO":
            novo_estado = menu.processar_eventos_comparacao(eventos)
            if novo_estado != "ESTADO_SELECIONAR_COMPARACAO":
                estado_atual = novo_estado
            menu.desenhar_selecao_comparacao(tela)

        elif estado_atual == "ESTADO_EM_DESENVOLVIMENTO":
            if menu.processar_eventos_wip(eventos) == "VOLTAR": estado_atual = "ESTADO_SELECIONAR_AGENTE"
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: estado_atual = "ESTADO_SELECIONAR_AGENTE"
            menu.desenhar_em_desenvolvimento(tela, agente_selecionado)

        elif estado_atual in ["SELECIONAR_DIF_MANUAL", "SELECIONAR_DIF_IA", "SELECIONAR_DIF_COMPARACAO"]:
            escolha = menu.processar_eventos_dificuldade(eventos)

            if escolha == "VOLTAR":
                if estado_atual == "SELECIONAR_DIF_MANUAL":
                    estado_atual = "ESTADO_MENU"
                elif estado_atual == "SELECIONAR_DIF_IA":
                    estado_atual = "ESTADO_SELECIONAR_AGENTE"
                else:
                    estado_atual = "ESTADO_SELECIONAR_COMPARACAO"

            elif escolha in ["FACIL", "MEDIO", "DIFICIL"]:
                env = CampoBatalhaEnv(dificuldade=escolha)

                # Setup Arena de Comparação
                if estado_atual == "SELECIONAR_DIF_COMPARACAO":
                    lista_comparacao = []
                    semente_global = env.seed_atual

                    agentes_marcados = [k for k, v in menu.agentes_comparacao.items() if v]

                    for nome_ag in agentes_marcados:
                        # Cria um universo paralelo exato usando a mesma Semente Global
                        env_clone = CampoBatalhaEnv(dificuldade=escolha, seed=semente_global)
                        visao_inicial = env_clone.reset()

                        ag_dict = {
                            "nome": nome_ag,
                            "env": env_clone,
                            "estado": visao_inicial,
                            "cor": CORES_AGENTES.get(nome_ag, (255, 255, 255)),
                            "pontuacao": 0,
                            "done": False,
                            "visitados": set(),
                            "rota": [],
                            "indice_rota": 0
                        }

                        # Injeção Cerebral Oculta
                        if "A*" in nome_ag:
                            modo_astar = nome_ag.split(" ")[1].upper()  # FOCADO, EQUILIBRADO, GULOSO
                            inst_a = AgenteAStar(env_clone)
                            ag_dict["instancia"] = inst_a
                            ag_dict["modo"] = modo_astar
                        elif nome_ag == "Algoritmo Genético":
                            inst_g = AlgoritmoGenetico(env_clone)
                            ag_dict["cerebro"] = inst_g.carregar_cerebro()
                        elif nome_ag == "Q-Learning":
                            inst_q = AgenteQLearning(env_clone)
                            inst_q._carregar_qtable()
                            ag_dict["instancia"] = inst_q

                        lista_comparacao.append(ag_dict)

                    comparacao_em_andamento = False
                    estado_atual = "ESTADO_JOGAR_COMPARACAO"

                else:
                    estado_ia = env.reset()
                    pontuacao = 0
                    status_jogo = "Correndo"
                    ia_em_execucao = False
                    rota_ia = []
                    cerebro_carregado = None
                    visitados_ag = set()

                    if estado_atual == "SELECIONAR_DIF_MANUAL":
                        acao_str = "Nova Simulação"
                        estado_atual = "ESTADO_JOGAR"
                    else:
                        if agente_selecionado == "Algoritmo Genético":
                            acao_str = "[AG] T: Treinar | L: Continuar Treino | C: Testar Cérebro"
                            estado_atual = "ESTADO_AGENTES"
                        elif agente_selecionado == "Q-Learning":
                            ag_instancia = AgenteQLearning(env)
                            qlearning_pronto = False
                            acao_str = "[Q-Learning] Escolha uma ação..."
                            estado_atual = "ESTADO_AGENTES"
                        else:
                            ag_instancia = AgenteAStar(env)
                            acao_str = f"[{agente_selecionado}] Prontidão"
                            estado_atual = "ESTADO_AGENTES"

            modo_titulo = "MANUAL" if estado_atual == "SELECIONAR_DIF_MANUAL" else (
                "COMPARACAO" if estado_atual == "SELECIONAR_DIF_COMPARACAO" else "IA")
            menu.desenhar_dificuldade(tela, modo_titulo)

        # --- EXECUÇÃO DA ARENA DE COMPARAÇÃO ---
        elif estado_atual == "ESTADO_JOGAR_COMPARACAO":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "ESTADO_SELECIONAR_COMPARACAO"
                        comparacao_em_andamento = False
                    elif evento.key == pygame.K_m:
                        estado_atual = "SELECIONAR_DIF_COMPARACAO"
                    elif evento.key == pygame.K_a and not comparacao_em_andamento:
                        comparacao_em_andamento = True
                        ultimo_tempo_mov = tempo_atual

                        # Calcula rotas prévias para A* e Q-Learning
                        for ag in lista_comparacao:
                            ag['env'].reset()
                            ag['pontuacao'] = 0
                            ag['done'] = False
                            ag['visitados'] = set()
                            if "A*" in ag['nome']:
                                ag['rota'] = ag['instancia'].planejar_rota(modo=ag['modo'])
                                ag['indice_rota'] = 0
                                if not ag['rota']: ag['done'] = True
                            elif ag['nome'] == "Q-Learning":
                                ag['rota'] = ag['instancia'].planejar_rota()
                                ag['estado'] = ag['env'].reset()
                                ag['indice_rota'] = 0
                                if not ag['rota']: ag['done'] = True

            if comparacao_em_andamento:
                if tempo_atual - ultimo_tempo_mov > delay_passo_ia:
                    todos_finalizados = True
                    for ag in lista_comparacao:
                        if not ag['done']:
                            todos_finalizados = False
                            acao = -1

                            # Decisão Tática
                            if "A*" in ag['nome'] or ag['nome'] == "Q-Learning":
                                if ag['indice_rota'] < len(ag['rota']):
                                    acao = ag['rota'][ag['indice_rota']]
                                    ag['indice_rota'] += 1
                                else:
                                    ag['done'] = True
                                    continue
                            elif ag['nome'] == "Algoritmo Genético":
                                if ag['cerebro']:
                                    dummy_ag = AlgoritmoGenetico(ag['env'])
                                    acao = dummy_ag._decidir_acao(ag['cerebro'], ag['estado'], ag['env'],
                                                                  modo_treino=False, visitados=ag['visitados'])
                                    ag['visitados'].add((ag['env'].posicao_x, ag['env'].posicao_y, acao))
                                else:
                                    ag['done'] = True
                                    continue

                            # Execução
                            novo_estado, recomp, done, _ = ag['env'].step(acao)
                            ag['estado'] = novo_estado
                            ag['pontuacao'] += recomp
                            if done:
                                ag['done'] = True

                    if todos_finalizados:
                        comparacao_em_andamento = False
                    ultimo_tempo_mov = tempo_atual

            dashboard.renderizar_arena(tela, lista_comparacao,
                                       "Em Andamento" if comparacao_em_andamento else "Finalizado")

        elif estado_atual == "ESTADO_TREINANDO_IA":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_atual = "SELECIONAR_DIF_IA"

            if estado_atual == "ESTADO_TREINANDO_IA":
                terminou, dados_geracao_ag = ag_instancia.treinar_uma_geracao()
                menu.desenhar_treinamento_ag(tela, dados_geracao_ag)

                if terminou or ag_instancia.geracao_atual > geracao_alvo_ag:
                    if terminou:
                        acao_str = "Gênio Formado! Pressione 'C' para Injetar a Mente."
                    else:
                        ag_instancia.salvar_cerebro_campeao()
                        acao_str = "Treino Concluído. Melhor cérebro salvo! Pressione 'C'."

                    estado_ia = env.reset()
                    estado_atual = "ESTADO_AGENTES"

        elif estado_atual == "ESTADO_TREINANDO_QL":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_atual = "SELECIONAR_DIF_IA"

            if estado_atual == "ESTADO_TREINANDO_QL":
                dados_ep = None
                for _ in range(40):
                    if not ag_instancia.treinado:
                        _, dados_ep = ag_instancia.treinar_um_episodio()
                    else:
                        break

                menu.desenhar_treinamento_ql(tela, dados_ep, ag_instancia.episodios_totais)

                if ag_instancia.treinado:
                    estado_ia = env.reset()
                    pontuacao = 0
                    status_jogo = "Correndo"
                    acao_str = "[Q-Learning] Prontidão para Execução!"
                    ia_em_execucao = False
                    rota_ia = []
                    qlearning_pronto = True
                    estado_atual = "ESTADO_AGENTES"

        elif estado_atual == "ESTADO_JOGAR":
            tomou_acao = False
            acao = -1
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "SELECIONAR_DIF_MANUAL"
                    elif evento.key == pygame.K_r:
                        estado_ia = env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Nova Simulação"
                    elif evento.key == pygame.K_n and "VITÓRIA" in status_jogo:
                        if env.dificuldade == "FACIL":
                            env = CampoBatalhaEnv(dificuldade="MEDIO")
                        elif env.dificuldade == "MEDIO":
                            env = CampoBatalhaEnv(dificuldade="DIFICIL")
                        estado_ia = env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Avançou de Nível"
                    elif status_jogo == "Correndo":
                        if evento.key == pygame.K_UP:
                            acao = 0;
                            acao_str = "Avançar";
                            tomou_acao = True
                        elif evento.key == pygame.K_LEFT:
                            acao = 1;
                            acao_str = "Esquerda";
                            tomou_acao = True
                        elif evento.key == pygame.K_RIGHT:
                            acao = 2;
                            acao_str = "Direita";
                            tomou_acao = True
                        elif evento.key == pygame.K_DOWN:
                            acao = 3;
                            acao_str = "Recuar";
                            tomou_acao = True

            if tomou_acao and status_jogo == "Correndo":
                estado_ia, recompensa, done, _ = env.step(acao)
                pontuacao += recompensa
                if done: status_jogo = "VITÓRIA!" if recompensa == 100 else "BATERIA ESGOTADA/MORTO"
            tela.fill((0, 0, 0))
            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="MANUAL")

        elif estado_atual == "ESTADO_AGENTES":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "SELECIONAR_DIF_IA"
                        ia_em_execucao = False
                        rota_ia = []
                        cerebro_carregado = None

                    elif evento.key == pygame.K_r:
                        estado_ia = env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        if agente_selecionado != "Algoritmo Genético":
                            acao_str = f"[{agente_selecionado}] Prontidão"
                        else:
                            acao_str = "Mapa Reiniciado. Pressione 'A' para o Rato correr."
                        ia_em_execucao = False
                        visitados_ag = set()

                    elif evento.key == pygame.K_m and agente_selecionado in ["A*", "Algoritmo Genético"]:
                        env = CampoBatalhaEnv(dificuldade=env.dificuldade)
                        estado_ia = env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Labirinto Inédito Gerado! Pressione 'A' para testar."
                        ia_em_execucao = False
                        rota_ia = []
                        visitados_ag = set()

                        if agente_selecionado == "A*" and ag_instancia:
                            modo_atual = ag_instancia.modo_selecionado
                            ag_instancia = AgenteAStar(env)
                            ag_instancia.modo_selecionado = modo_atual

                    elif evento.key == pygame.K_1 and agente_selecionado == "A*":
                        if ag_instancia: ag_instancia.modo_selecionado = "FOCADO"
                        acao_str = "A* preparado como FOCADO"

                    elif evento.key == pygame.K_2 and agente_selecionado == "A*":
                        if ag_instancia: ag_instancia.modo_selecionado = "EQUILIBRADO"
                        acao_str = "A* preparado como EQUILIBRADO"

                    elif evento.key == pygame.K_3 and agente_selecionado == "A*":
                        if ag_instancia: ag_instancia.modo_selecionado = "GULOSO"
                        acao_str = "A* preparado como GULOSO"

                    elif evento.key == pygame.K_m and agente_selecionado == "Q-Learning":
                        env = CampoBatalhaEnv(dificuldade=env.dificuldade)
                        estado_ia = env.reset()
                        ag_instancia = AgenteQLearning(env)
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "[Q-Learning] Novo mapa gerado! Escolha uma ação..."
                        ia_em_execucao = False
                        rota_ia = []
                        qlearning_pronto = False

                    # --- MERGE: Avanço Dinâmico de Nível (UX do Colega + Correção A*) ---
                    elif evento.key == pygame.K_n and agente_selecionado in ["Q-Learning", "A*", "Algoritmo Genético"]:
                        if env.dificuldade in ["FACIL", "MEDIO"]:
                            nova_dif = "MEDIO" if env.dificuldade == "FACIL" else "DIFICIL"
                            env = CampoBatalhaEnv(dificuldade=nova_dif)
                            estado_ia = env.reset()
                            pontuacao = 0
                            status_jogo = "Correndo"
                            ia_em_execucao = False
                            rota_ia = []
                            visitados_ag = set()

                            if agente_selecionado == "Q-Learning":
                                ag_instancia = AgenteQLearning(env)
                                acao_str = f"[Q-Learning] Nível {nova_dif} Gerado! Escolha uma ação..."
                                qlearning_pronto = False
                            else:
                                acao_str = f"Nível {nova_dif} Gerado! Pressione 'A' para testar."
                                if agente_selecionado == "A*" and ag_instancia:
                                    modo_atual = ag_instancia.modo_selecionado
                                    ag_instancia = AgenteAStar(env)
                                    ag_instancia.modo_selecionado = modo_atual

                    elif evento.key == pygame.K_t and agente_selecionado == "Algoritmo Genético":
                        caminho_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_treino_ag.log")
                        if os.path.exists(caminho_log): os.remove(caminho_log)

                        ag_instancia = AlgoritmoGenetico(env)
                        ag_instancia.inicializar_populacao()
                        geracao_alvo_ag = 150
                        estado_atual = "ESTADO_TREINANDO_IA"

                    elif evento.key == pygame.K_l and agente_selecionado == "Algoritmo Genético":
                        ag_instancia = AlgoritmoGenetico(env)
                        if ag_instancia.continuar_treinamento_do_cerebro():
                            geracao_alvo_ag = ag_instancia.geracao_atual + 150
                            estado_atual = "ESTADO_TREINANDO_IA"
                        else:
                            acao_str = "Erro: Nenhum cérebro salvo para continuar!"

                    elif evento.key == pygame.K_t and agente_selecionado == "Q-Learning" and not qlearning_pronto:
                        estado_atual = "ESTADO_TREINANDO_QL"

                    elif evento.key == pygame.K_u and agente_selecionado == "Q-Learning" and not qlearning_pronto:
                        qlearning_pronto = True
                        acao_str = "[Q-Learning] Prontidão para Execução!"

                    elif evento.key == pygame.K_c and agente_selecionado == "Algoritmo Genético":
                        ag_instancia = AlgoritmoGenetico(env)
                        cerebro_carregado = ag_instancia.carregar_cerebro()

                        if cerebro_carregado:
                            acao_str = "Cérebro Injetado no Agente! Pressione 'A' para soltá-lo."
                            estado_ia = env.reset()
                            pontuacao = 0
                            status_jogo = "Correndo"
                            visitados_ag = set()
                        else:
                            acao_str = "Erro: Cérebro não encontrado! Use 'T' para forjar um."

                    elif evento.key == pygame.K_a and not ia_em_execucao:
                        if status_jogo != "Correndo" and agente_selecionado == "Q-Learning":
                            estado_ia = env.reset()
                            pontuacao = 0
                            status_jogo = "Correndo"

                        if status_jogo == "Correndo":
                            if agente_selecionado == "A*":
                                acao_str = f"A* ({ag_instancia.modo_selecionado}) Calculando Rota..."
                                dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="IA_ASTAR",
                                                           ag_instancia=ag_instancia)
                                pygame.display.flip()

                                rota_ia = ag_instancia.planejar_rota(modo=ag_instancia.modo_selecionado)
                                if not rota_ia: acao_str = "A* Erro: Sem Saída!"
                                if rota_ia: ia_em_execucao = True; indice_rota = 0

                            elif agente_selecionado == "Q-Learning":
                                if qlearning_pronto:
                                    acao_str = "Q-Learning Planejando..."
                                    dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo,
                                                               modo="IA_QLEARNING", ag_instancia=ag_instancia)
                                    pygame.display.flip()
                                    rota_ia = ag_instancia.planejar_rota()
                                    estado_ia = env.reset()
                                    if not rota_ia: acao_str = "Q-Learning: Rota não encontrada!"
                                    if rota_ia: ia_em_execucao = True; indice_rota = 0
                                else:
                                    acao_str = "Escolha Treinar [T] ou Usar Tabela [U] primeiro!"

                            elif agente_selecionado == "Algoritmo Genético":
                                if cerebro_carregado:
                                    ia_em_execucao = True
                                    acao_str = "Rato solto no labirinto!"
                                    visitados_ag = set()
                                else:
                                    acao_str = "Nenhum Cérebro na memória. Pressione 'C' primeiro."

                            if ia_em_execucao: ultimo_tempo_mov = tempo_atual

            if ia_em_execucao and status_jogo == "Correndo":
                if tempo_atual - ultimo_tempo_mov > delay_passo_ia:
                    if agente_selecionado == "Algoritmo Genético":
                        ag_dummy = AlgoritmoGenetico(env)
                        visao_local = estado_ia
                        acao = ag_dummy._decidir_acao(cerebro_carregado, visao_local, env, modo_treino=False,
                                                      visitados=visitados_ag)
                        visitados_ag.add((env.posicao_x, env.posicao_y, acao))
                    else:
                        if indice_rota < len(rota_ia):
                            acao = rota_ia[indice_rota]
                        else:
                            ia_em_execucao = False
                            continue

                    mapa_acoes = {0: "Avançar", 1: "Esquerda", 2: "Direita", 3: "Recuar"}
                    acao_str = f"IA -> {mapa_acoes[acao]}"

                    estado_ia, recompensa, done, _ = env.step(acao)
                    pontuacao += recompensa

                    if done:
                        status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"
                        ia_em_execucao = False

                    indice_rota += 1
                    ultimo_tempo_mov = tempo_atual

            tela.fill((0, 0, 0))

            if agente_selecionado == "A*":
                modo_painel = "IA_ASTAR"
            elif agente_selecionado == "Q-Learning":
                if qlearning_pronto:
                    modo_painel = "IA_QLEARNING"
                else:
                    modo_painel = "IA_QLEARNING_ESCOLHA"
            elif agente_selecionado == "Algoritmo Genético":
                if cerebro_carregado and (ia_em_execucao or status_jogo != "Correndo"):
                    modo_painel = "IA_REPLAY"
                else:
                    modo_painel = "IA_GENETICO"
            else:
                modo_painel = "IA_REPLAY"

            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo=modo_painel,
                                       ag_instancia=ag_instancia)

        pygame.display.flip()
        relogio.tick(30)


if __name__ == "__main__":
    main()