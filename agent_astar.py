import heapq
import numpy as np


class AgenteAStar:
    def __init__(self, ambiente):
        self.env = ambiente
        self.modo_selecionado = "EQUILIBRADO"

    def heuristica(self, pos_atual, pos_objetivo):
        return abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1])

    def planejar_rota(self, mapa_customizado=None, modo="EQUILIBRADO"):
        if mapa_customizado is not None:
            mapa_alvo = mapa_customizado
        else:
            mapa_alvo = getattr(self.env, 'mapa', self.env.mapa_original)

        inicio = (self.env.largura // 2, 0)
        objetivo = (getattr(self.env, 'objetivo_x', self.env.largura // 2), self.env.comprimento - 1)

        # O Validador invisível usado na geração do mapa (ambiente)
        if modo == "VALIDADOR":
            return self._buscar_caminho(inicio, objetivo, mapa_alvo, 1, 1, 1)

        # Personalidade 1: Focado
        elif modo == "FOCADO":
            return self._buscar_caminho(inicio, objetivo, mapa_alvo, custo_vazio=1, custo_lama=3, custo_choco=1)

        # Personalidade 2: Equilibrado
        elif modo == "EQUILIBRADO":
            return self._buscar_caminho(inicio, objetivo, mapa_alvo, custo_vazio=1, custo_lama=6, custo_choco=0)

        # Personalidade 3: Guloso
        elif modo == "GULOSO":
            return self._planejar_rota_gulosa(inicio, objetivo, mapa_alvo)

        return []

    def _buscar_caminho(self, inicio, objetivo, mapa_alvo, custo_vazio, custo_lama, custo_choco):
        fila = []
        contador = 0
        h_inicial = self.heuristica(inicio, objetivo)
        heapq.heappush(fila, (h_inicial, 0, contador, inicio[0], inicio[1], []))
        visitados = {}

        while fila:
            f, g, _, x, y, caminho = heapq.heappop(fila)

            if (x, y) == objetivo or mapa_alvo[y][x] == self.env.OBJETIVO:
                return caminho

            if (x, y) in visitados and visitados[(x, y)] <= g:
                continue
            visitados[(x, y)] = g

            acoes = [
                (0, x, y + 1),
                (1, x - 1, y),
                (2, x + 1, y),
                (3, x, y - 1)
            ]

            for acao, nx, ny in acoes:
                if 0 <= nx < self.env.largura and 0 <= ny < self.env.comprimento:
                    terreno = mapa_alvo[ny][nx]

                    if terreno == self.env.MINA:
                        continue

                    custo_passo = custo_vazio
                    if terreno == self.env.LAMA:
                        custo_passo = custo_lama
                    elif terreno == self.env.CHOCOLATE:
                        custo_passo = custo_choco

                    novo_g = g + custo_passo
                    novo_h = self.heuristica((nx, ny), objetivo)
                    novo_f = novo_g + novo_h

                    novo_caminho = caminho + [acao]
                    contador += 1
                    heapq.heappush(fila, (novo_f, novo_g, contador, nx, ny, novo_caminho))

        return []

    def _planejar_rota_gulosa(self, inicio, objetivo_final, mapa_alvo):
        rota_completa = []
        pos_atual = inicio
        mapa_temp = np.copy(mapa_alvo)

        doces_coletados = 0
        limite_doces = 15  # Previne exaustão de bateria caçando doces infinitos

        while doces_coletados < limite_doces:
            chocolates = []
            for y in range(self.env.comprimento):
                for x in range(self.env.largura):
                    if mapa_temp[y][x] == self.env.CHOCOLATE:
                        # Caça doces que não exijam voltar mais de 6 blocos pra trás (eficiência)
                        if y >= pos_atual[1] - 6:
                            chocolates.append((x, y))

            if not chocolates:
                break

            # Ordena os chocolates pela proximidade
            chocolates.sort(key=lambda c: self.heuristica(pos_atual, c))
            alvo_choco = chocolates[0]

            # Roda A* até o doce (Custo Equilibrado: evita lama)
            rota_parcial = self._buscar_caminho(pos_atual, alvo_choco, mapa_temp, custo_vazio=1, custo_lama=6,
                                                custo_choco=0)

            if rota_parcial:
                rota_completa.extend(rota_parcial)
                # Atualiza a posição mental do agente
                for acao in rota_parcial:
                    if acao == 0:
                        pos_atual = (pos_atual[0], pos_atual[1] + 1)
                    elif acao == 1:
                        pos_atual = (pos_atual[0] - 1, pos_atual[1])
                    elif acao == 2:
                        pos_atual = (pos_atual[0] + 1, pos_atual[1])
                    elif acao == 3:
                        pos_atual = (pos_atual[0], pos_atual[1] - 1)

                    if mapa_temp[pos_atual[1]][pos_atual[0]] == self.env.CHOCOLATE:
                        mapa_temp[pos_atual[1]][pos_atual[0]] = self.env.VAZIO
                doces_coletados += 1
            else:
                # Inalcançável, ignora o doce e parte para o próximo
                mapa_temp[alvo_choco[1]][alvo_choco[0]] = self.env.VAZIO

        # Após limpar os doces possíveis, parte para o resgate
        rota_final = self._buscar_caminho(pos_atual, objetivo_final, mapa_temp, custo_vazio=1, custo_lama=6,
                                          custo_choco=0)
        if rota_final:
            rota_completa.extend(rota_final)

        return rota_completa