
"""Script de demonstração de loopback (sem áudio real).
Permite rodar um teste por vez para não poluir o terminal,
ou rodar todos juntos para o relatório final."""


import test_method1
import test_method2


def menu():
    print("\n============================================")
    print("         MENU DE TESTES (LOOPBACK)          ")
    print("============================================")
    print("1) Método 1 - Sucesso ('Oi!')")
    print("2) Método 1 - Quadro Incompleto")
    print("3) Método 2 - Sucesso ('Ola, Equipe!')")
    print("4) Método 2 - Com Corrupção de Bit (CRC Falha)")
    print("5) Método 2 - Quadro Incompleto")
    print("6) Rodar TODOS os testes de uma vez")
    print("0) Sair")
    print("============================================")
    
    opcao = input("Escolha o teste que deseja rodar [0-6]: ").strip()

    if opcao == '1':
        test_method1.testar_metodo1("Oi!")
    elif opcao == '2':
        test_method1.testar_metodo1_incompleto("Oi!")
    elif opcao == '3':
        test_method2.testar_metodo2("Ola, Equipe!")
    elif opcao == '4':
        test_method2.testar_metodo2_com_erro("Ola, Equipe!")
    elif opcao == '5':
        test_method2.testar_metodo2_incompleto("Ola, Equipe!")
    elif opcao == '6':
        print("\n--- EXECUTANDO BATERIA COMPLETA ---")
        test_method1.testar_metodo1("Oi!")
        test_method1.testar_metodo1_incompleto("Oi!")
        test_method2.testar_metodo2("Ola, Equipe!")
        test_method2.testar_metodo2_com_erro("Ola, Equipe!")
        test_method2.testar_metodo2_incompleto("Ola, Equipe!")
        print("\n--- FIM DA BATERIA DE TESTES ---")
    elif opcao == '0':
        print("Saindo dos testes...")
    else:
        print("Opção inválida! Tente novamente.")


if __name__ == "__main__":
    menu()


