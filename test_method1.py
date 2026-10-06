import numpy as np
import method1

def testar_metodo1(texto):
    print(f"\n--- Teste Método 1 (sucesso): {texto!r} ---")
    quadros = method1.montar_quadros(texto)
    sinal = np.concatenate([method1.bit_para_audio(b) for q in quadros for b in q])
    bits = method1.agrupar_em_bits(sinal)
    method1.validar_e_decodificar(bits)


def testar_metodo1_incompleto(texto):
    print(f"\n--- Teste Método 1 (quadro incompleto simulado): {texto!r} ---")
    quadros = method1.montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    
    # Pega apenas os primeiros 12 bits (deixando o 2º quadro com apenas 3 bits)
    bits_cortados = todos_bits[:12]
    sinal = np.concatenate([method1.bit_para_audio(b) for b in bits_cortados])
    
    bits = method1.agrupar_em_bits(sinal)
    method1.validar_e_decodificar(bits)