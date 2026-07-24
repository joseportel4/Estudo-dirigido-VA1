import matplotlib.pyplot as plt
import os


def gerar_grafico(dificuldade):
    caminho_log = f"debug_treino_ag_{dificuldade}.log"
    if not os.path.exists(caminho_log):
        print(f"Log não encontrado para o modo {dificuldade} ({caminho_log}). Pulei.")
        return

    geracoes = []
    fitness = []

    print(f"Lendo o arquivo de log do modo {dificuldade}...")
    with open(caminho_log, "r", encoding="utf-8") as f:
        for linha in f:
            if "Ger:" in linha and "Fit Médio:" in linha:
                partes = linha.split("|")
                try:
                    ger = int(partes[0].split(":")[1].strip())
                    fit = float(partes[2].split(":")[1].strip())
                    geracoes.append(ger)
                    fitness.append(fit)
                except Exception:
                    continue

    if not geracoes:
        return

    # Plotagem do Gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(geracoes, fitness, color='#00b4ff', linewidth=2, label=f"Fitness Médio ({dificuldade})")
    plt.fill_between(geracoes, fitness, min(fitness), color='#00b4ff', alpha=0.1)

    # Customização Visual
    cor_titulo = '#1e2636'
    plt.title(f"Evolução do Algoritmo Genético - Modo {dificuldade}", fontsize=16, fontweight='bold', color=cor_titulo)
    plt.xlabel("Gerações", fontsize=12)
    plt.ylabel("Pontuação Média (Fitness)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    # Exportação
    plt.tight_layout()
    nome_arquivo_saida = f"grafico_evolucao_ag_{dificuldade}.png"
    plt.savefig(nome_arquivo_saida, dpi=300)
    plt.close()  # Limpa a memória para o próximo gráfico
    print(f"Sucesso! Gráfico salvo como '{nome_arquivo_saida}'.")


if __name__ == "__main__":
    modos = ["FACIL", "MEDIO", "DIFICIL"]
    print("Iniciando varredura de logs para geração de gráficos...\n")
    for modo in modos:
        gerar_grafico(modo)
    print("\nProcesso finalizado!")