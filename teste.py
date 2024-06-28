import os
import subprocess

def run_trabalho(input_file, output_file):
    # Chamando o programa trabalho1.py com a entrada especificada e salvando a saída em um arquivo
    with open(output_file, 'w') as f:
        subprocess.run(["python3", "main.py", input_file, output_file])
def main():
    input_folder = "entrada"
    output_folder = "saida"

    # Certifique-se de que a pasta de saída existe, se não, crie-a
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = os.listdir(input_folder)

    # Iterando sobre os arquivos de entrada
    for input_file in input_files:
        if input_file.endswith(".txt"):
            input_path = os.path.join(input_folder, input_file)
            output_path = os.path.join(output_folder, os.path.splitext(input_file)[0] + "_saida.txt")

            # Executando o programa trabalho1.py com os arquivos de entrada e saída especificados
            run_trabalho(input_path, output_path)

if __name__ == "__main__":
    main()
