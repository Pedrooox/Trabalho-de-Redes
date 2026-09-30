"""
Comunicação Acústica entre Dispositivos - Camada Física (Modelo ISO/OSI)
Ponto de entrada: escolha do método (1 ou 2) e do modo (transmissor/receptor).

Requisitos: pip install numpy sounddevice
"""

import sys
import method1
import method2


def menu():
    print("=== Comunicação Acústica - Camada Física ===")
    print("1) Transmitir mensagem")
    print("2) Receber mensagem")
    modo = input("Escolha o modo [1/2]: ").strip()

    print("\nMétodo:")
    print("1) Método 1 - (batidas sonoras, paridade)")
    print("2) Método 2 - (FSK + CRC-8)")
    metodo = input("Escolha o método [1/2]: ").strip()

    if modo == '1':
        texto = input("Digite a mensagem a transmitir: ")
        (method1 if metodo == '1' else method2).transmitir(texto)

    elif modo == '2':
        if metodo == '1':
            method1.receber()
        else:
            method2.receber()
    else:
        print("Opção inválida.")
        sys.exit(1)


if __name__ == "__main__":
    menu()
