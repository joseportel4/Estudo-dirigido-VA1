import random
import json
import os
import numpy as np


class Individuo:
    def __init__(self, tamanho_cromossomo):
        self.cromossomo = [random.uniform(-1.0, 1.0) for _ in range(tamanho_cromossomo)]
        self.fitness = -999999
        self.chegou_objetivo = False
        self.taxa_vitoria = 0.0


class AlgoritmoGenetico:
    def __init__(self, env, tamanho_populacao=200):
        self.env_base = env
        self.tamanho_populacao = tamanho_populacao

        self.num_inputs = 26
        self.num_acoes = 4
        self.tamanho_cromossomo = self.num_inputs * self.num_acoes

        self.populacao = []
        self.geracao_atual = 1
        self.melhor_fitness_global = -999999
        self.geracoes_sem_melhora = 0

        self.melhor_individuo_global = None
        self.geracao_melhor_global = 1
        self.num_lotes = 3

    def inicializar_populacao(self):
        self.populacao = [Individuo(self.tamanho_cromossomo) for _ in range(self.tamanho_populacao)]
        self.geracao_atual = 1
        self.melhor_fitness_global = -999999
        self.geracoes_sem_melhora = 0
        self.melhor_individuo_global = None
        self.geracao_melhor_global = 1

    def carregar_cerebro(self):
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(pasta_atual, f"cerebro_campeao_{self.env_base.dificuldade}.json")

        try:
            if not os.path.exists(caminho_arquivo): return False
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            if len(dados["cromossomo"]) != self.tamanho_cromossomo:
                return False

            return dados["cromossomo"]
        except:
            return False

    def salvar_cerebro_campeao(self, individuo=None, geracao=None):
        ind = individuo if individuo else self.melhor_individuo_global
        gen = geracao if geracao else self.geracao_melhor_global

        if ind is None: return

        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(pasta_atual, f"cerebro_campeao_{self.env_base.dificuldade}.json")
        dados = {
            "geracao_vencedora": gen,
            "dificuldade": self.env_base.dificuldade,
            "fitness_medio": ind.fitness,
            "cromossomo": ind.cromossomo
        }
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4)
        except Exception as e:
            pass

    def continuar_treinamento_do_cerebro(self):
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(pasta_atual, f"cerebro_campeao_{self.env_base.dificuldade}.json")

        try:
            if not os.path.exists(caminho_arquivo): return False
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            dna_base = dados["cromossomo"]
            if len(dna_base) != self.tamanho_cromossomo:
                return False

            self.populacao = []
            campeao = Individuo(self.tamanho_cromossomo)
            campeao.cromossomo = list(dna_base)
            self.populacao.append(campeao)

            while len(self.populacao) < self.tamanho_populacao:
                clone = Individuo(self.tamanho_cromossomo)
                clone.cromossomo = list(dna_base)
                self._mutacao_pesos(clone, estagnado=True)
                self.populacao.append(clone)

            self.geracao_atual = dados.get("geracao_vencedora", 1) + 1
            self.melhor_fitness_global = dados.get("fitness_medio", -999999)
            self.geracoes_sem_melhora = 0

            self.melhor_individuo_global = campeao
            self.geracao_melhor_global = dados.get("geracao_vencedora", 1)

            return True
        except:
            return False

    def _decidir_acao(self, pesos, visao_local, env_ref, modo_treino=True, visitados=None):
        visao_flat = visao_local.flatten()
        visao_flat = np.delete(visao_flat, 12)

        visao_processada = np.zeros_like(visao_flat, dtype=float)
        visao_processada[visao_flat == -1] = -1.0
        visao_processada[visao_flat == 0] = 0.0
        visao_processada[visao_flat == 1] = -0.5
        visao_processada[visao_flat == 2] = 1.0
        visao_processada[visao_flat == 3] = -1.0
        visao_processada[visao_flat == 4] = 2.0

        dist_y = (env_ref.comprimento - 1 - env_ref.posicao_y) / float(env_ref.comprimento)
        dist_x = (env_ref.objetivo_x - env_ref.posicao_x) / float(env_ref.largura)

        inputs = np.concatenate([visao_processada, [dist_y, dist_x]])
        matriz_pesos = np.array(pesos).reshape(self.num_inputs, self.num_acoes)
        outputs = np.dot(inputs, matriz_pesos)

        # === 1. INSTINTO SUPERIOR SUPREMO AVANÇADO IMPLACÁVEL INDOMÁVEL SANGUINÁRIO===
        obstaculos = [env_ref.MINA, env_ref.LAMA, -1]
        fila = [(2, 2, [])]
        visitados_bfs = {(2, 2)}
        atracoes = [0.0, 0.0, 0.0, 0.0]

        acoes_delta = {
            0: (1, 0),  # Avançar
            1: (0, -1),  # Esquerda
            2: (0, 1),  # Direita
            3: (-1, 0)  # Recuar
        }

        while fila:
            cy, cx, caminho = fila.pop(0)
            terreno = visao_local[cy][cx]

            if caminho:
                primeira_acao = caminho[0]
                if terreno == env_ref.OBJETIVO:
                    atracoes[primeira_acao] += 50000.0 / len(caminho)
                elif terreno == env_ref.CHOCOLATE:
                    atracoes[primeira_acao] += 500.0 / len(caminho)

            if len(caminho) < 4:
                for acao_id, (dy, dx) in acoes_delta.items():
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < 5 and 0 <= nx < 5:
                        if (ny, nx) not in visitados_bfs:
                            if visao_local[ny][nx] not in obstaculos:
                                visitados_bfs.add((ny, nx))
                                fila.append((ny, nx, caminho + [acao_id]))

        outputs[0] += atracoes[0]
        outputs[1] += atracoes[1]
        outputs[2] += atracoes[2]
        outputs[3] += atracoes[3]

        # === 2. INSTINTO DE SOBREVIVÊNCIA ===
        if not modo_treino:
            # Trava Anti-Suicídio
            if visao_local[3][2] in [env_ref.MINA, -1]: outputs[0] -= 99999.0
            if visao_local[2][1] in [env_ref.MINA, -1]: outputs[1] -= 99999.0
            if visao_local[2][3] in [env_ref.MINA, -1]: outputs[2] -= 99999.0
            if visao_local[1][2] in [env_ref.MINA, -1]: outputs[3] -= 99999.0

            # Memória Anti-Looping
            if visitados is not None:
                acoes_ordenadas = np.argsort(outputs)[::-1]
                for acao_cand in acoes_ordenadas:
                    if outputs[acao_cand] <= -90000: continue
                    if (env_ref.posicao_x, env_ref.posicao_y, acao_cand) not in visitados:
                        return int(acao_cand)
                for acao_cand in acoes_ordenadas:
                    if outputs[acao_cand] > -90000: return int(acao_cand)

        return int(np.argmax(outputs))

    def avaliar_em_lote(self, cromossomo, sementes_lote):
        fitness_total = 0
        vitorias = 0

        for semente in sementes_lote:
            env_teste = self.env_base.__class__(dificuldade=self.env_base.dificuldade, seed=semente)
            random.seed(semente)
            np.random.seed(semente)
            visao_local = env_teste.reset()

            pontuacao_total = 0
            maior_y_alcancado = env_teste.posicao_y
            visitados = set()
            visitados.add((env_teste.posicao_x, env_teste.posicao_y))

            penalidade_loop = 0
            passos_dados = 0
            passos_sem_progresso = 0

            while True:
                acao = self._decidir_acao(cromossomo, visao_local, env_teste, modo_treino=True)
                visao_local, recompensa, done, _ = env_teste.step(acao)
                passos_dados += 1
                passos_sem_progresso += 1

                x, y = env_teste.posicao_x, env_teste.posicao_y
                if (x, y) in visitados: penalidade_loop += 5
                visitados.add((x, y))

                if y > maior_y_alcancado:
                    maior_y_alcancado = y
                    passos_sem_progresso = 0

                pontuacao_total += recompensa

                if passos_sem_progresso >= 35:
                    done = True
                    penalidade_loop += 4000

                if done:
                    if recompensa == 100: vitorias += 1
                    break

            dist_manhattan = abs(env_teste.objetivo_x - env_teste.posicao_x) + abs(
                (env_teste.comprimento - 1) - env_teste.posicao_y)
            dist_maxima = env_teste.largura + env_teste.comprimento
            score_distancia = ((dist_maxima - dist_manhattan) / dist_maxima) * 10000

            fit_mapa = score_distancia + (pontuacao_total * 2) - penalidade_loop

            if recompensa == 100:
                bonus_velocidade = (env_teste.limite_passos - passos_dados) * 5
                fit_mapa += 50000 + bonus_velocidade

            fitness_total += fit_mapa

        return fitness_total / self.num_lotes, vitorias

    def log_depuracao(self, geracao, fit, sucesso, estagnacao, acao="Treino"):
        nome_arquivo = f"debug_treino_ag_{self.env_base.dificuldade}.log"
        caminho_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arquivo)

        log_str = f"Ger: {geracao:04d} | Modo: {self.env_base.dificuldade} | Fit Médio: {fit:7.1f} | Tx Vitória Campeão: {sucesso:5.1%} | Estagnação: {estagnacao:02d} | Status: {acao}\n"
        with open(caminho_log, "a", encoding="utf-8") as f:
            f.write(log_str)

    def treinar_uma_geracao(self):
        sementes_lote = [random.randint(10000, 99999) for _ in range(self.num_lotes)]

        melhor_individuo = None
        melhor_fitness_geracao = -999999

        for ind in self.populacao:
            fit_medio, vitorias = self.avaliar_em_lote(ind.cromossomo, sementes_lote)
            ind.fitness = fit_medio
            ind.taxa_vitoria = vitorias / self.num_lotes

            if fit_medio > melhor_fitness_geracao:
                melhor_fitness_geracao = fit_medio
                melhor_individuo = ind

        terminou = False
        taxa_sucesso_campeao = melhor_individuo.taxa_vitoria

        if melhor_individuo.taxa_vitoria == 1.0:
            status_acao = "OBJETIVO DE GENERALIZAÇÃO ATINGIDO!"
            terminou = True

            clone_campeao = Individuo(self.tamanho_cromossomo)
            clone_campeao.cromossomo = list(melhor_individuo.cromossomo)
            clone_campeao.fitness = melhor_individuo.fitness
            self.melhor_individuo_global = clone_campeao
            self.geracao_melhor_global = self.geracao_atual

            self.salvar_cerebro_campeao(melhor_individuo, self.geracao_atual)
            self.log_depuracao(self.geracao_atual, melhor_fitness_geracao, taxa_sucesso_campeao,
                               self.geracoes_sem_melhora, status_acao)
        else:
            if melhor_fitness_geracao > self.melhor_fitness_global:
                self.melhor_fitness_global = melhor_fitness_geracao
                self.geracao_melhor_global = self.geracao_atual

                clone_campeao = Individuo(self.tamanho_cromossomo)
                clone_campeao.cromossomo = list(melhor_individuo.cromossomo)
                clone_campeao.fitness = melhor_individuo.fitness
                self.melhor_individuo_global = clone_campeao

                self.geracoes_sem_melhora = 0
                status_acao = "Novo Recorde de Adaptação"
            else:
                self.geracoes_sem_melhora += 1
                status_acao = "Estagnado"
            self.log_depuracao(self.geracao_atual, melhor_fitness_geracao, taxa_sucesso_campeao,
                               self.geracoes_sem_melhora, status_acao)

        dados_retorno = {
            "geracao": self.geracao_atual,
            "dificuldade": self.env_base.dificuldade,
            "fitness_campeao": melhor_fitness_geracao,
            "taxa_sucesso": taxa_sucesso_campeao
        }

        if not terminou:
            if self.geracoes_sem_melhora >= 40:
                self.log_depuracao(self.geracao_atual, melhor_fitness_geracao, taxa_sucesso_campeao,
                                   self.geracoes_sem_melhora, "CATACLISMO (Reboot Parcial)")

                nova_populacao = []
                campeao_sobrevivente = Individuo(self.tamanho_cromossomo)
                campeao_sobrevivente.cromossomo = list(self.melhor_individuo_global.cromossomo)
                campeao_sobrevivente.fitness = self.melhor_individuo_global.fitness
                nova_populacao.append(campeao_sobrevivente)

                while len(nova_populacao) < self.tamanho_populacao:
                    ind_novo = Individuo(self.tamanho_cromossomo)
                    if random.random() < 0.5:
                        ind_novo.cromossomo = list(self.melhor_individuo_global.cromossomo)
                        self._mutacao_pesos(ind_novo, estagnado=True)
                    nova_populacao.append(ind_novo)

                self.populacao = nova_populacao
                self.geracoes_sem_melhora = 0
                self.geracao_atual += 1
                return terminou, dados_retorno

            num_elite = max(1, int(self.tamanho_populacao * 0.10))
            elite = sorted(self.populacao, key=lambda ind: ind.fitness, reverse=True)[:num_elite]

            nova_populacao = [Individuo(self.tamanho_cromossomo) for _ in range(num_elite)]
            for i in range(num_elite):
                nova_populacao[i].cromossomo = list(elite[i].cromossomo)

            estagnado = self.geracoes_sem_melhora > 15

            while len(nova_populacao) < self.tamanho_populacao:
                pai1 = self._selecao_torneio()
                pai2 = self._selecao_torneio()
                filho1, filho2 = self._crossover(pai1, pai2)

                self._mutacao_pesos(filho1, estagnado)
                self._mutacao_pesos(filho2, estagnado)

                nova_populacao.extend([filho1, filho2])

            self.populacao = nova_populacao[:self.tamanho_populacao]
            self.geracao_atual += 1

        return terminou, dados_retorno

    def _selecao_torneio(self, k=3):
        torneio = random.sample(self.populacao, k)
        return max(torneio, key=lambda ind: ind.fitness)

    def _crossover(self, pai1, pai2):
        pt1 = random.randint(1, self.tamanho_cromossomo - 2)
        pt2 = random.randint(pt1 + 1, self.tamanho_cromossomo - 1)

        filho1 = Individuo(self.tamanho_cromossomo)
        filho2 = Individuo(self.tamanho_cromossomo)

        filho1.cromossomo = pai1.cromossomo[:pt1] + pai2.cromossomo[pt1:pt2] + pai1.cromossomo[pt2:]
        filho2.cromossomo = pai2.cromossomo[:pt1] + pai1.cromossomo[pt1:pt2] + pai2.cromossomo[pt2:]
        return filho1, filho2

    def _mutacao_pesos(self, individuo, estagnado):
        taxa_micro = 0.10 if not estagnado else 0.30
        taxa_macro = 0.02 if not estagnado else 0.10
        for i in range(self.tamanho_cromossomo):
            if random.random() < taxa_macro:
                individuo.cromossomo[i] = random.uniform(-1.0, 1.0)
            elif random.random() < taxa_micro:
                individuo.cromossomo[i] += random.gauss(0, 0.2)
                individuo.cromossomo[i] = max(-1.0, min(1.0, individuo.cromossomo[i]))