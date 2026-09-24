import method1
import method2


def testar_metodo1(texto):
    print(f"\n--- Teste Método 1 (sucesso): {texto!r} ---")
    quadros = method1.montar_quadros(texto)
    sinal = __import__('numpy').concatenate(
        [method1.bit_para_audio(b) for q in quadros for b in q])
    bits = method1.agrupar_em_bits(sinal)
    method1.validar_e_decodificar(bits)


def testar_metodo2(texto):
    print(f"\n--- Teste Método 2 (sucesso): {texto!r} ---")
    quadros = method2.montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    sinal = method2.bits_para_audio(todos_bits)
    bits = method2.demodular_bits(sinal, len(todos_bits))
    method2.validar_e_decodificar(bits)


def testar_metodo2_com_erro(texto):
    print(f"\n--- Teste Método 2 (com corrupção simulada): {texto!r} ---")
    quadros = method2.montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    todos_bits[3] ^= 1  # corrompe 1 bit de dados do 1º quadro -> deve falhar no CRC
    sinal = method2.bits_para_audio(todos_bits)
    bits = method2.demodular_bits(sinal, len(todos_bits))
    method2.validar_e_decodificar(bits)


if __name__ == "__main__":
    testar_metodo1("Oi!")
    testar_metodo2("Ola, Equipe!")
    testar_metodo2_com_erro("Ola, Equipe!")