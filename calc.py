def calculadora():
    print("Calculadora")
    print("1. Adição")
    print("2. Subtração")
    print("3. Multiplicação")
    print("4. Divisão")

    escolha = input("Escolha a operação: ")

    if escolha == "1":
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        resultado = num1 + num2
        print(f"Resultado: {num1} + {num2} = {resultado}")

    elif escolha == "2":
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        resultado = num1 - num2
        print(f"Resultado: {num1} - {num2} = {resultado}")

    elif escolha == "3":
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        resultado = num1 * num2
        print(f"Resultado: {num1} * {num2} = {resultado}")

    elif escolha == "4":
        num1 = float(input("Digite o primeiro número: "))
        num2 = float(input("Digite o segundo número: "))
        if num2 != 0:
            resultado = num1 / num2
            print(f"Resultado: {num1} / {num2} = {resultado}")
        else:
            print("Erro: Divisão por zero!")

    else:
        print("Opção inválida!")

calculadora()