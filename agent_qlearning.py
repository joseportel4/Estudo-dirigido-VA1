import random
import numpy as np
import json
import os
import ast

from environment import CampoBatalhaEnv

CAMINHO_QTABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qtable_universal.json")

# Intervalo de episódios entre salvamentos automáticos
INTERVALO_SAVE = 500


class AgenteQLearning:

    def __init__(
            self,
            env,
            alpha=None,
            gamma=None,
            epsilon_inicial=1.0,
            epsilon_min=0.05,
            epsilon_decay=None,
            episodios_totais=None
    ):
        self.env = env

        # Hiperparâmetros ajustados por dificuldade
        config_defaults = {
            "FACIL":   {"alpha": 0.30, "gamma": 0.95, "decay": 0.994,  "episodios": 800,  "troca_mapa": 5},
            "MEDIO":   {"alpha": 0.20, "gamma": 0.97, "decay": 0.997,  "episodios": 2000, "troca_mapa": 5},
            "DIFICIL": {"alpha": 0.15, "gamma": 0.99, "decay": 0.9985, "episodios": 4000, "troca_mapa": 3},
        }

        dificuldade = getattr(self.env, "dificuldade", "MEDIO").upper()
        if dificuldade not in config_defaults:
            dificuldade = "MEDIO"

        cfg = config_defaults[dificuldade]

        self.alpha               = alpha            if alpha            is not None else cfg["alpha"]
        self.gamma               = gamma            if gamma            is not None else cfg["gamma"]
        self.epsilon             = epsilon_inicial
        self.epsilon_min         = epsilon_min
        self.epsilon_decay       = epsilon_decay    if epsilon_decay    is not None else cfg["decay"]
        self.episodios_totais    = episodios_totais if episodios_totais is not None else cfg["episodios"]
        self.intervalo_troca_mapa = cfg["troca_mapa"]

        self.q_tabela = {}
        self._carregar_qtable()

        self.env_treino = env

        self.historico      = []
        self.episodio_atual = 0
        self.treinado       = False

    # ════════════════════════════════════════════════════════════════════════
    # PERSISTÊNCIA DA TABELA Q
    # ════════════════════════════════════════════════════════════════════════

    def _carregar_qtable(self):
        """Carrega a Tabela Q Universal do arquivo JSON, se existir."""
        if os.path.exists(CAMINHO_QTABLE):
            try:
                with open(CAMINHO_QTABLE, 'r') as f:
                    dados = json.load(f)
                #converte de volta para tuplas com ast.literal_eval
                self.q_tabela = {ast.literal_eval(k): v for k, v in dados.items()}
                print(f"[Q-Learning] Tabela Q carregada: {len(self.q_tabela)} estados conhecidos.")
            except Exception as e:
                print(f"[Q-Learning] Aviso: erro ao carregar tabela Q ({e}). Iniciando vazia.")
                self.q_tabela = {}

    def _salvar_qtable(self):
        """Persiste a Tabela Q Universal no arquivo JSON."""
        try:
            # Converte chaves tupla para string 
            dados = {str(k): v for k, v in self.q_tabela.items()}
            with open(CAMINHO_QTABLE, 'w') as f:
                json.dump(dados, f, indent=2)
            print(f"[Q-Learning] Tabela Q salva: {len(self.q_tabela)} estados.")
        except Exception as e:
            print(f"[Q-Learning] Aviso: erro ao salvar tabela Q ({e}).")

    # ════════════════════════════════════════════════════════════════════════
    # REPRESENTAÇÃO DE ESTADO — VISÃO 5×5 (RAIO 2)
    # ════════════════════════════════════════════════════════════════════════

    def get_estado(self, visao_local, env=None, ultima_acao=-1):
        """
        Composição do estado:
          (av, rec, esq, dir)              — raio 1: terreno nos 4 destinos imediatos (5 categorias)
          (av2, esq2, dir2)                — raio 2: perigo a 2 passos nas 3 direções úteis (binário)
          (choco_av, choco_esq, choco_dir) — raio 2: migalhas de chocolate nas 3 direções (binário)
          (dir_x, dir_y)                   — vetor de orientação para o objetivo (-1, 0, +1)
          (dist_x_disc)                    — distância horizontal discreta até objetivo_x (0, 1, 2)
          (ultima_acao)                    — ação anterior (-1=início, 0-3=ação) → quebra oscilações
        """
        if env is None:
            env = self.env

        def cat(v):
            """Categoriza célula do raio 1 em 5 classes de terreno."""
            if v == -1 or v == env.MINA:  return 2  # PERIGO (borda ou mina)
            if v == env.LAMA:              return 1  # LENTO
            if v == env.CHOCOLATE:         return 3  # BÔNUS 
            if v == env.OBJETIVO:          return 4  # META
            return 0                                 # SEGURO 

        def perigo(v):
            """Binário: borda ou mina detectada no raio 2."""
            return 1 if (v == -1 or v == env.MINA) else 0

        def choco(v):
            """Binário: migalha de chocolate detectada no raio 2."""
            return 1 if v == env.CHOCOLATE else 0

        # ── Raio 1: percepção tática dos 4 destinos imediatos ────────────────
        av  = cat(visao_local[3][2])   # destino de avançar  (ação 0)
        rec = cat(visao_local[1][2])   # destino de recuar   (ação 3)
        esq = cat(visao_local[2][1])   # destino de esquerda (ação 1)
        dir = cat(visao_local[2][3])   # destino de direita  (ação 2)

        av2  = perigo(visao_local[4][2])   # 2 passos avançar
        esq2 = perigo(visao_local[2][0])   # 2 passos esquerda
        dir2 = perigo(visao_local[2][4])   # 2 passos direita

        choco_av  = choco(visao_local[4][2])
        choco_esq = choco(visao_local[2][0])
        choco_dir = choco(visao_local[2][4])

        dir_x       = int(np.sign(env.objetivo_x - env.posicao_x))
        dir_y       = int(np.sign((env.comprimento - 1) - env.posicao_y))

        dist_x      = abs(env.objetivo_x - env.posicao_x)
        dist_x_disc = 0 if dist_x == 0 else (1 if dist_x <= 3 else 2)

        return (av, rec, esq, dir,
                av2, esq2, dir2,
                choco_av, choco_esq, choco_dir,
                dir_x, dir_y, dist_x_disc,
                ultima_acao)

    # ════════════════════════════════════════════════════════════════════════
    # TABELA Q
    # ════════════════════════════════════════════════════════════════════════

    def get_q_valores(self, estado):
        """
        Retorna [Q(av), Q(esq), Q(dir), Q(rec)] para o estado.
        Inicialização otimista: incentiva avançar (+2.0) e penaliza recuar (-1.0) por padrão.
        Laterais iniciam neutras (0.0) — moldadas pelas recompensas do ambiente.
        """
        if estado not in self.q_tabela:
            # [avançar, esquerda, direita, recuar]
            self.q_tabela[estado] = [2.0, 0.0, 0.0, -1.0]
        return self.q_tabela[estado]

    def escolher_acao(self, estado, explorando=True):
        """Política epsilon-greedy: explora aleatoriamente ou segue a melhor ação conhecida."""
        if explorando and random.random() < self.epsilon:
            return random.randint(0, 3)
        q = self.get_q_valores(estado)
        max_q = max(q)
        # Desempate aleatório entre ações com o mesmo Q máximo
        melhores = [i for i, v in enumerate(q) if v == max_q]
        return random.choice(melhores)

    # ════════════════════════════════════════════════════════════════════════
    # REWARD SHAPING
    # ════════════════════════════════════════════════════════════════════════

    def _reward_shaping(self, acao, ultima_acao, pos_y_ant, pos_y_atual, recompensa_nativa, recorde_y, env, pos_revisitada=False):
        # Terminais e chocolate: preserva sem alteração
        if abs(recompensa_nativa) >= 50 or recompensa_nativa == 14:
            return recompensa_nativa

        # Lama: mantém a penalidade nativa (-6) para que o agente aprenda a evitá-la
        if recompensa_nativa == -6:
            return -6

        # Ação reversa: desfaz o passo anterior (ex: direita→esquerda, frente→trás)
        # É o principal causador da oscilação — punição forte para erradicar o hábito
        reversos = {0: 3, 3: 0, 1: 2, 2: 1}
        if ultima_acao != -1 and acao == reversos.get(ultima_acao):
            return -6.0  # Mesma magnitude da lama — oscilar é tão ruim quanto lama

        # Revisita de posição: o agente já esteve aqui neste episódio
        # Ensina que andar em círculos desperdiça passos (que são limitados)
        if pos_revisitada:
            return -4.0

        # Nas últimas linhas do mapa: incentiva alinhamento horizontal com objetivo_x
        if pos_y_atual >= env.comprimento - 6:
            dist_obj = abs(env.posicao_x - env.objetivo_x)
            if dist_obj == 0:
                return 5.0   # Alinhado perfeitamente com o objetivo!
            elif dist_obj <= 2:
                return 2.0   # Muito próximo do alinhamento

        # Progressão vertical
        if pos_y_atual > pos_y_ant:
            return 5.0 if pos_y_atual > recorde_y else 2.0  # Desbrava ou avança em rota conhecida
        elif pos_y_atual < pos_y_ant:
            return -3.0   # Recuou — desincentivado
        else:
            return -1.5   # Lateral com custo real: permite contornar, mas não é de graça

    # ════════════════════════════════════════════════════════════════════════
    # TREINAMENTO
    # ════════════════════════════════════════════════════════════════════════

    def treinar_um_episodio(self):
        """
        Executa um episódio completo de treinamento.

        Multi-mapa: a cada `intervalo_troca_mapa` episódios, gera um novo CampoBatalhaEnv
        com a mesma dificuldade mas semente diferente. O self.env permanece intocado.

        Persistência: salva a tabela Q a cada INTERVALO_SAVE episódios e obrigatoriamente ao concluir o treinamento.
        """
        # Rotaciona o ambiente de treino periodicamente para generalização multi-mapa
        if self.episodio_atual > 0 and self.episodio_atual % self.intervalo_troca_mapa == 0:
            self.env_treino = CampoBatalhaEnv(dificuldade=self.env.dificuldade)

        env = self.env_treino
        visao_local  = env.reset()

        ultima_acao     = -1  # Sem ação anterior no início do episódio
        estado_atual    = self.get_estado(visao_local, env, ultima_acao=ultima_acao)

        pontuacao_total  = 0
        chegou_objetivo  = False
        recorde_y        = 0
        passos           = 0
        posicoes_visitadas = set() 

        while passos < env.limite_passos:
            passos += 1
            pos_y_ant = env.posicao_y

            acao = self.escolher_acao(estado_atual, explorando=True)
            visao_nova, recompensa_nativa, done, _ = env.step(acao)

            # Verifica se a nova posição já foi visitada antes de registrá-la
            nova_pos = (env.posicao_x, env.posicao_y)
            pos_revisitada = nova_pos in posicoes_visitadas
            posicoes_visitadas.add(nova_pos)

            pos_y_atual = env.posicao_y
            if pos_y_atual > recorde_y:
                recorde_y = pos_y_atual

            recompensa = self._reward_shaping(
                acao, ultima_acao, pos_y_ant, pos_y_atual,
                recompensa_nativa, recorde_y, env, pos_revisitada
            )
            pontuacao_total += recompensa_nativa  # Histórico usa recompensa real do ambiente

            # Próximo estado carrega a ação atual como memória (quebra simetria de oscilação)
            proximo_estado = self.get_estado(visao_nova, env, ultima_acao=acao)
            q_atual        = self.get_q_valores(estado_atual)[acao]

            # Equação de Bellman
            if done:
                alvo = recompensa
                if recompensa_nativa == 100:
                    chegou_objetivo = True
            else:
                max_q_prox = max(self.get_q_valores(proximo_estado))
                alvo = recompensa + self.gamma * max_q_prox

            self.q_tabela[estado_atual][acao] += self.alpha * (alvo - q_atual)
            estado_atual = proximo_estado
            ultima_acao  = acao  # Atualiza memória para o próximo passo

            if done:
                break

        # Decaimento de epsilon após cada episódio
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.episodio_atual += 1

        # Salvamento periódico automático (protege progresso em caso de interrupção)
        if self.episodio_atual % INTERVALO_SAVE == 0:
            self._salvar_qtable()

        dados_episodio = {
            "episodio":        self.episodio_atual,
            "dificuldade":     env.dificuldade,
            "semente_mapa":    env.seed_atual,
            "pontuacao_real":  pontuacao_total,
            "chegou_objetivo": chegou_objetivo,
            "passos":          passos,
            "epsilon":         round(self.epsilon, 4),
            "estados_q":       len(self.q_tabela),
        }
        self.historico.append(dados_episodio)

        if self.episodio_atual >= self.episodios_totais:
            self.treinado = True
            self._salvar_qtable()  # Salvamento final obrigatório

        return done, dados_episodio

    def treinar(self, num_episodios=None, verbose=True):
        """Treina o agente sequencialmente em modo batch/console."""
        total    = num_episodios if num_episodios is not None else self.episodios_totais
        sucessos = 0

        for ep in range(1, total + 1):
            _, dados = self.treinar_um_episodio()
            if dados["chegou_objetivo"]:
                sucessos += 1

            if verbose and (ep % (total // 10 or 1) == 0 or ep == total):
                taxa = (sucessos / ep) * 100
                print(f"[Q-Learning | {self.env.dificuldade}] Ep {ep}/{total} | "
                      f"e={dados['epsilon']} | Estados Q: {dados['estados_q']} | "
                      f"Sucessos: {taxa:.1f}%")

        self.treinado = True
        self._salvar_qtable()
        return self.historico

    # ════════════════════════════════════════════════════════════════════════
    # INFERÊNCIA
    # ════════════════════════════════════════════════════════════════════════

    def obter_melhor_acao(self, estado=None, visao_local=None):
        """Retorna a ação greedy (sem exploração) para o estado ou visão fornecidos."""
        if estado is None and visao_local is not None:
            estado = self.get_estado(visao_local, self.env)
        return self.escolher_acao(estado, explorando=False)

    def planejar_rota(self):
        """
        executa a política greedy sobre a Tabela Q aprendida.

        Dois mecanismos de segurança:
          - Máscara de Sobrevivência Raio 1: bloqueia (-99999) ações que levariam o agente
            diretamente a uma mina ou borda detectada na visão imediata.
          - Anti-loop por contagem de visitas: penaliza ações cujo destino já foi visitado
            3 ou mais vezes, forçando o agente a buscar rotas alternativas.
        """
        visao_local = self.env.reset()
        caminho_acoes = []
        done      = False
        passos    = 0
        ultima_acao = -1

        contagem_pos = {} 

        while not done and passos < self.env.limite_passos:
            passos += 1
            pos = (self.env.posicao_x, self.env.posicao_y)
            contagem_pos[pos] = contagem_pos.get(pos, 0) + 1

            estado_atual = self.get_estado(visao_local, self.env, ultima_acao=ultima_acao)
            valores_q    = list(self.get_q_valores(estado_atual))

            # ── Máscara de Sobrevivência Raio 1 ──────────────────────────────
            # Mapeamento correto: ação → célula imediata correspondente na visao_local
            # Ação 0 (avançar,  y+1): imediato = visao[3][2]
            if visao_local[3][2] in [self.env.MINA, -1]: valores_q[0] = -99999
            # Ação 1 (esquerda, x-1): imediato = visao[2][1]
            if visao_local[2][1] in [self.env.MINA, -1]: valores_q[1] = -99999
            # Ação 2 (direita,  x+1): imediato = visao[2][3]
            if visao_local[2][3] in [self.env.MINA, -1]: valores_q[2] = -99999
            # Ação 3 (recuar,   y-1): imediato = visao[1][2]
            if visao_local[1][2] in [self.env.MINA, -1]: valores_q[3] = -99999

            # ── Penalidade Anti-loop Progressiva ──────────────
            destinos = {
                0: (self.env.posicao_x,     self.env.posicao_y + 1),
                1: (self.env.posicao_x - 1, self.env.posicao_y),
                2: (self.env.posicao_x + 1, self.env.posicao_y),
                3: (self.env.posicao_x,     self.env.posicao_y - 1),
            }
            for a, prox_pos in destinos.items():
                visitas = contagem_pos.get(prox_pos, 0)
                if visitas > 0:
                    if valores_q[a] > -99999:
                        valores_q[a] -= (visitas * 2.5)

            max_q = max(valores_q)
            if max_q <= -99999:
                break  # Todas as saídas bloqueadas — encerra a rota

            melhores = [i for i, v in enumerate(valores_q) if v == max_q]
            acao = random.choice(melhores)

            caminho_acoes.append(acao)
            visao_local, _, done, _ = self.env.step(acao)
            ultima_acao = acao  # Atualiza memória para o próximo passo

        return caminho_acoes