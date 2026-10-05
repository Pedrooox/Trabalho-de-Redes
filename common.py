"""
Camada Física - Utilitários comuns de áudio
Comunicação acústica entre dispositivos usando a placa de som (meio: ondas sonoras).
"""

import numpy as np

# ---------------- Configurações globais ----------------
SAMPLE_RATE = 44100           # Hz
CANAIS = 1                    # mono

# Tom de sincronismo (marca o início de uma transmissão para os dois métodos)
PREAMBLE_FREQ = 3000           # Hz
PREAMBLE_DUR = 0.25             # s


def gerar_tom(freq, duracao, amplitude=0.8, fade=0.003):
    """Gera um tom senoidal puro com fade in/out para evitar estalos (cliques) indesejados."""
    t = np.linspace(0, duracao, int(SAMPLE_RATE * duracao), endpoint=False)
    onda = amplitude * np.sin(2 * np.pi * freq * t)
    n_fade = int(SAMPLE_RATE * fade)
    if n_fade > 0 and n_fade * 2 < len(onda):
        janela = np.linspace(0, 1, n_fade)
        onda[:n_fade] *= janela
        onda[-n_fade:] *= janela[::-1]
    return onda.astype(np.float32)


def gerar_silencio(duracao):
    return np.zeros(int(SAMPLE_RATE * duracao), dtype=np.float32)


import os
import queue
import sys
import time

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

def gerar_click(duracao=0.10, amplitude=1.0):
    """Gera um 'beep' curto e agudo para o Método 1 (melhor detecção)."""
    t = np.linspace(0, duracao, int(SAMPLE_RATE * duracao), endpoint=False)
    freq = 2500.0  # Frequência aguda (mas não ultra alta) para o beep/peep
    
    onda = np.sin(2 * np.pi * freq * t)
    
    # Envelope de amplitude para soar como um 'peep' e evitar estalos na caixa de som
    # Fade in rápido e fade out suave
    envelope = np.ones_like(t)
    fade_in_len = int(len(t) * 0.1)
    fade_out_len = int(len(t) * 0.5)
    
    if fade_in_len > 0:
        envelope[:fade_in_len] = np.linspace(0, 1, fade_in_len)
    if fade_out_len > 0:
        envelope[-fade_out_len:] = np.linspace(1, 0, fade_out_len)
        
    som = onda * envelope
    return (som * amplitude).astype(np.float32)


def tocar(sinal):
    """Reproduz o sinal na saída de áudio padrão (requer sounddevice + placa de som)."""
    import sounddevice as sd
    sd.play(sinal, SAMPLE_RATE)
    sd.wait()


def gravar(live_decode_func=None):
    """Grava do microfone padrão com controle manual.
    Pressione ENTER para começar e ENTER para parar.
    Mostra um histograma do som e os bits detectados ao vivo no terminal."""
    import sounddevice as sd
    os.system("") # Habilita sequências ANSI no cmd/PowerShell do Windows
    q = queue.Queue()
    dados_recentes = np.zeros(2048, dtype=np.float32)
    
    def callback(indata, frames, time_info, status):
        nonlocal dados_recentes
        if status:
            pass # Ignora warnings de underflow/overflow para não poluir a interface
        q.put(indata.copy())
        if len(indata) >= 2048:
            dados_recentes = indata[-2048:, 0]
        else:
            dados_recentes = np.roll(dados_recentes, -len(indata))
            dados_recentes[-len(indata):] = indata[:, 0]
        
    input("[AGUARDANDO] Pressione ENTER para INICIAR a gravação...")
    print("[GRAVANDO] Ouvindo... (Pressione ENTER para PARAR a gravação)")
    
    if HAS_MSVCRT:
        sys.stdout.write("\n" * 12)
        sys.stdout.flush()

    dados_acumulados = []

    # Abre o fluxo contínuo de áudio
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CANAIS, dtype='float32', callback=callback):
        if HAS_MSVCRT:
            while True:
                if msvcrt.kbhit():
                    if msvcrt.getch() in (b'\r', b'\n'):
                        time.sleep(0.5) # Aguarda meio segundo para garantir que capturou o som final da sala
                        break
                
                # Transfere os dados da fila para a lista acumulada
                while not q.empty():
                    dados_acumulados.append(q.get())
                
                bits_str = ""
                if live_decode_func and dados_acumulados:
                    sinal_atual = np.concatenate(dados_acumulados).flatten()
                    try:
                        bits = live_decode_func(sinal_atual)
                        bits_str = "".join(str(b) for b in bits)
                        if len(bits_str) > 70:
                            bits_str = "..." + bits_str[-67:]
                    except Exception:
                        bits_str = "Erro na decodificação ao vivo"

                fft_val = np.abs(np.fft.rfft(dados_recentes))
                vol = np.max(np.abs(dados_recentes))
                vol_bars = min(40, int(vol * 40))
                
                bandas = [
                    (0, 500, "0-500Hz  "),
                    (500, 1000, "500-1kHz "),
                    (1000, 2000, "1k-2kHz  "),
                    (2000, 3000, "2k-3kHz  "),
                    (3000, 4500, "3k-4.5kHz"),
                    (4500, 10000, "4.5k-10k ")
                ]
                
                linhas = [f"\033[KVolume: [{'#' * vol_bars}{' ' * (40 - vol_bars)}] {vol:.2f}"]
                linhas.append("\033[K--- Histograma de Frequências ---")
                for ini, fim, nome in bandas:
                    idx_ini = int(ini * len(fft_val) / (SAMPLE_RATE / 2))
                    idx_fim = int(fim * len(fft_val) / (SAMPLE_RATE / 2))
                    val = np.mean(fft_val[idx_ini:idx_fim]) if idx_fim > idx_ini else 0
                    val_norm = val / 15.0 # Sensibilidade
                    bars = min(30, int(val_norm * 30))
                    linhas.append(f"\033[K{nome}: {'█' * bars}")
                
                linhas.append("\033[K--- Decodificação ao Vivo ---")
                linhas.append(f"\033[KBits: {bits_str}")

                sys.stdout.write(f"\033[{len(linhas)}A") # Sobe X linhas
                sys.stdout.write("\n".join(linhas) + "\n")
                sys.stdout.flush()
                time.sleep(0.1) # Atualiza 10 vezes por segundo para evitar sobrecarga na decodificação ao vivo
        else:
            input()
            
    # Agrupa quaisquer blocos restantes
    while not q.empty():
        dados_acumulados.append(q.get())
        
    print("\nGravação finalizada.")
    return np.concatenate(dados_acumulados).flatten() if dados_acumulados else np.array([])


# ---------------- Conversão texto <-> bits ----------------

def texto_para_bits(texto):
    """Converte uma string (UTF-8) em lista de bits (0/1)."""
    bits = []
    for byte in texto.encode('utf-8'):
        bits.extend(int(b) for b in format(byte, '08b'))
    return bits


def bits_para_texto(bits):
    """Converte uma lista de bits (múltiplo de 8) de volta em string UTF-8."""
    n_bytes = len(bits) // 8
    valores = []
    for i in range(n_bytes):
        byte_bits = bits[i * 8:(i + 1) * 8]
        valores.append(int(''.join(map(str, byte_bits)), 2))
    return bytes(valores).decode('utf-8', errors='replace')


def bit_de_paridade_par(bits8):
    """Retorna o 9º bit (paridade PAR) para 8 bits de dados."""
    return sum(bits8) % 2
