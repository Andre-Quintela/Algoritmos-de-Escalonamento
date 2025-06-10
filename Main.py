import matplotlib.pyplot as plt
from matplotlib import cm

class Processo:
    def __init__(self, pid, chegada, duracao, prioridade):
        self.pid = pid
        self.chegada = int(chegada)
        self.duracao = int(duracao)
        self.restante = int(duracao)
        self.prioridade = int(prioridade)
        self.inicio = None
        self.termino = None
        self.tempo_espera = 0
        self.tempo_turnaround = 0
        self.tempo_resposta = None

def ler_entrada(path):
    with open(path, 'r') as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    num_processos = int(linhas[0])
    processos = []
    for linha in linhas[1:num_processos+1]:
        pid, chegada, duracao, prioridade = linha.split()
        processos.append(Processo(pid, chegada, duracao, prioridade))
    return processos

def fcfs(processos):
    processos_ordenados = sorted(processos, key=lambda p: p.chegada)
    tempo_atual = 0
    gantt = []
    for proc in processos_ordenados:
        if tempo_atual < proc.chegada:
            tempo_atual = proc.chegada
        proc.inicio = tempo_atual
        proc.termino = tempo_atual + proc.duracao
        proc.tempo_espera = proc.inicio - proc.chegada
        proc.tempo_turnaround = proc.termino - proc.chegada
        proc.tempo_resposta = proc.inicio - proc.chegada
        gantt.append({"name": proc.pid, "start": proc.inicio, "end": proc.termino})
        tempo_atual = proc.termino
    return gantt, processos_ordenados

def sjf_nao_preemptivo(processos):
    tempo_atual = 0
    gantt = []
    fila = []
    processos_restantes = processos[:]
    concluido = []

    while processos_restantes or fila:
        fila.extend([p for p in processos_restantes if p.chegada <= tempo_atual])
        processos_restantes = [p for p in processos_restantes if p.chegada > tempo_atual]
        if fila:
            fila.sort(key=lambda p: p.duracao)
            proc = fila.pop(0)
            if tempo_atual < proc.chegada:
                tempo_atual = proc.chegada
            proc.inicio = tempo_atual
            proc.termino = tempo_atual + proc.duracao
            proc.tempo_espera = proc.inicio - proc.chegada
            proc.tempo_turnaround = proc.termino - proc.chegada
            proc.tempo_resposta = proc.inicio - proc.chegada
            gantt.append({"name": proc.pid, "start": proc.inicio, "end": proc.termino})
            tempo_atual = proc.termino
            concluido.append(proc)
        else:
            tempo_atual += 1

    return gantt, concluido

def sjf_preemptivo(processos):
    tempo_atual = 0
    gantt = []
    fila = []
    processos_restantes = processos[:]
    em_execucao = None
    ultimo_tempo = 0

    while processos_restantes or fila or em_execucao:
        fila.extend([p for p in processos_restantes if p.chegada == tempo_atual])
        processos_restantes = [p for p in processos_restantes if p.chegada > tempo_atual]

        if em_execucao:
            fila.append(em_execucao)
            em_execucao = None

        if fila:
            fila.sort(key=lambda p: p.restante)
            proc = fila.pop(0)
            if proc.inicio is None:
                proc.inicio = tempo_atual
                proc.tempo_resposta = tempo_atual - proc.chegada
            proc.restante -= 1
            if gantt and gantt[-1]['name'] == proc.pid:
                gantt[-1]['end'] += 1
            else:
                gantt.append({"name": proc.pid, "start": tempo_atual, "end": tempo_atual + 1})

            if proc.restante == 0:
                proc.termino = tempo_atual + 1
                proc.tempo_turnaround = proc.termino - proc.chegada
                proc.tempo_espera = proc.tempo_turnaround - proc.duracao
            else:
                em_execucao = proc
        tempo_atual += 1

    return gantt, sorted(processos, key=lambda p: p.pid)

def plot_gantt_chart(gantt, ax):
    """
    Recebe uma lista de dicionários. Cada dicionário é composto por:
        name: Nome do Processo (string)
        start: Tempo que o processo inicia no gráfico (int)
        end: Tempo que o processo finaliza no gráfico (int)
    """
    process_names = list({task['name'] for task in gantt})
    process_names.sort()
    name_to_y = {name: i for i, name in enumerate(process_names)}

    colors = cm.get_cmap('Pastel1', len(process_names))
    name_to_color = {name: colors(i) for i, name in enumerate(process_names)}

    for task in gantt:
        y_pos = name_to_y[task['name']]
        ax.barh(y_pos, task['end'] - task['start'], left=task['start'], height=0.5,
                align='center', color=name_to_color[task['name']])

    max_time = max(task['end'] for task in gantt)
    ax.set_xlim(0, max_time + 1)
    ax.set_xticks(range(0, max_time + 1))
    ax.set_yticks(list(name_to_y.values()))
    ax.set_yticklabels(list(name_to_y.keys()))
    ax.set_xlabel('Time')
    ax.grid(True, axis='x', linestyle='--', alpha=0.3)

def gerar_gantt(gantt_data, filename, titulo):
    fig, ax = plt.subplots(figsize=(10, 4))
    plot_gantt_chart(gantt_data, ax)
    ax.set_title(titulo)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def exibir_metricas(processos):
    print("PID\tChegada\tDuração\tInício\tTérmino\tEspera\tTurnaround\tResposta")
    for p in processos:
        print(f"{p.pid}\t{p.chegada}\t\t{p.duracao}\t\t{p.inicio}\t{p.termino}\t{p.tempo_espera}\t{p.tempo_turnaround}\t\t{p.tempo_resposta}")

# Exemplo de uso:
caminho_entrada = "entradas/entrada_1.txt"  # Altere aqui para testar outro arquivo
processos = ler_entrada(caminho_entrada)

# FCFS
gantt_fcfs, proc_fcfs = fcfs([Processo(p.pid, p.chegada, p.duracao, p.prioridade) for p in processos])
gerar_gantt(gantt_fcfs, "gantt_fcfs.png", "Gráfico de Gantt - FCFS")
print("\n[FCFS]")
exibir_metricas(proc_fcfs)

# SJF Não Preemptivo
gantt_sjf_np, proc_sjf_np = sjf_nao_preemptivo([Processo(p.pid, p.chegada, p.duracao, p.prioridade) for p in processos])
gerar_gantt(gantt_sjf_np, "gantt_sjf_np.png", "Gráfico de Gantt - SJF Não Preemptivo")
print("\n[SJF Não Preemptivo]")
exibir_metricas(proc_sjf_np)

# SJF Preemptivo
gantt_sjf_p, proc_sjf_p = sjf_preemptivo([Processo(p.pid, p.chegada, p.duracao, p.prioridade) for p in processos])
gerar_gantt(gantt_sjf_p, "gantt_sjf_p.png", "Gráfico de Gantt - SJF Preemptivo")
print("\n[SJF Preemptivo]")
exibir_metricas(proc_sjf_p)
