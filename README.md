# Resgate no Campo de Batalha: Agentes Inteligentes 🪖

Repositório para o estudo dirigido referente ao conteúdo da primeira VA da disciplina de Inteligência Artificial.

## 🎯 Sobre o Projeto (Estado Atual)

O projeto consiste na implementação de um ambiente virtual próprio, um campo de batalha, onde soldados (agentes IA) precisam atravessar um terreno hostil para resgatar um companheiro ferido. 
Atualmente, o projeto encontra-se **totalmente funcional e completo**, contando com três paradigmas de IA implementados (Busca Heurística, Algoritmo Genético e Q-Learning), além de um ambiente visual robusto com **Arena de Comparação** que permite observar os modelos operando simultaneamente no mesmo mapa gerado proceduralmente.

O ambiente apresenta:
- Desafios estáticos: minas terrestres (morte instantânea) e lama (diminuem a pontuação).
- Bônus: chocolates (aumentam a pontuação).
- Objetivo final de resgate e visibilidade parcial para o agente treinado.
- Geração procedural inteligente (Uma das funções do algoritmo A* é agir como "juiz" garantindo que nenhum mapa gerado seja impossível).

## 🧠 Paradigmas de IA e Agentes Implementados

Neste ambiente, estão integrados três paradigmas distintos, que o professor pode testar individualmente ou em conjunto:

1. **Agente A* (Busca Heurística):** O agente matemático que atua como nosso *baseline*. Ele calcula a rota antes da execução através de visão global.
   - **Perfis Implementados:** O A* possui 3 modos de atuação: **Focado**, **Equilibrado** e **Guloso** (priorizando diferentes pesos para exploração vs. custo).
2. **Algoritmo Genético (AG):** População de soldados que evoluem e passam seus "genes" adiante, baseados numa função de *fitness* (pontuação e distância percorrida). 
   - **Cérebros Pré-treinados:** Já disponibilizamos arquivos de cérebro campeão por dificuldade (Fácil, Médio, Difícil).
3. **Aprendizado por Reforço (Q-Learning):** Um agente que interage com o ambiente tomando decisões baseadas numa visão local do terreno (estado), aprendendo por tentativa e erro (recompensa e punição) e construindo uma matriz de qualidade (Q-Table).
   - **Q-Table Universal:** O projeto já acompanha uma Q-Table treinada com mais de 5MB contendo vasta experiência do agente.

## ⚙️ Instalação e Requisitos

**Pré-requisitos:** Python 3.10 ou superior.

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Estudo-dirigido-VA1.git
cd Estudo-dirigido-VA1
```

2. Instale as dependências. As bibliotecas principais são `pygame`, `numpy` e `matplotlib`:
```bash
pip install -r requirements.txt
```

3. Execute o programa principal:
```bash
python main.py
```

## 🎮 Maneiras de Rodar e Interagir (Comandos)

O sistema conta com um menu gráfico desenvolvido em Pygame. Quando rodar o sistema, você pode optar por:
- **Modo Manual:** Jogue você mesmo com as `Setas Direcionais` e experimente o desafio do terreno.
- **Modo IA Individual:** Selecione uma IA específica para vê-la resolvendo o labirinto.
- **Arena de Comparação:** A *feature* definitiva para testes. Selecione duas ou mais IAs para rodarem em clones do mesmo mapa e veja quem chega primeiro, de forma mais eficiente.

**Atalhos Úteis durante a visualização das IAs:**
- **A*:** Pressione `1`, `2` ou `3` para alternar entre os perfis Focado, Equilibrado e Guloso. Pressione `A` para rodar a IA.
- **Q-Learning:** Escolha treinar `[T]` ou usar a tabela existente `[U]`. Pressione `A` para executar.
- **Algoritmo Genético:** Pressione `T` para treinar um novo cérebro ou `C` para carregar um cérebro campeão (já existente na pasta do projeto).
- **Geral:** Pressione `M` para gerar um novo mapa inédito, `N` para avançar de nível (dificuldade) ou `ESC` para voltar ao menu.

## 📝 Observações válidas

1. **Dificuldade Dinâmica e A* como Juiz:** Tente rodar o projeto nas dificuldades Fácil, Médio e Difícil, e observe como o terreno escala e como o A* sempre garante um caminho acessível (Juiz de geração atestado em `environment.py`).
2. **Impacto das Funções Heurísticas (A*):** No modo do A*, teste os 3 perfis e avalie no relatório a quantidade de nós visitados em relação à rapidez e custo das rotas tomadas (Guloso vai direto ao ponto, enquanto Equilibrado desvia melhor da lama).
3. **Visão Local vs Visão Global:** Observe como o Q-Learning toma decisões apenas com base no seu raio de visão no terreno, e como ele pode ficar preso num ótimo local e como as recompensas/penalidades moldaram esse comportamento, em contraste com a visão onisciente do A*.
4. **Arena Simultânea:** A melhor forma de corrigir e avaliar a eficácia do trabalho é iniciar a "Arena de Comparação", marcar as 3 IAs (incluindo perfis variados do A*) e observar o comportamento empírico delas enfrentando o mesmo *seed* de mapa.
