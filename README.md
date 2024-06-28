# Trabalho de Análise Semântica T4 da Linguagem Algorítmica (LA)

Alexandra Floriano - 761771

## Pré-requisitos

Python 3.x

ANTLR

## Descrição

Este é um projeto que implementa um analisador semântico para a linguagem LA (Linguagem Algorítmica), utilizando a ferramenta ANTLR (ANother Tool for Language Recognition).

O analisador semântico desenvolvido é capaz de identificar erros semânticos no código fonte em LA, fornecendo mensagens de erro detalhadas para facilitar a correção por parte do usuário.Diferento do trabalho anterior, agora envolvendo também ponteiros, registros, funções.

## Estrutura do Projeto

* 'LAGrammar.g4': Arquivo contendo a gramática do analisador semântico em formato ANTLR.
* 'main.py': Script Python para executar o analisador semântico.
* 'entrada.txt': Arquivo de exemplo contendo um código fonte em LA para ser analisado.
* 'saida.txt': Arquivo de saída onde serão registradas as mensagens de erro semântico.
* 'teste.py': Arquivos para imprimir todos as saídas dos casos-testes.

## Como Executar

1. Instale o ANTLR seguindo as instruções em [antlr](https://www.antlr.org/).
2. Execute no seu terminal para poder utilizar em Python.

```Python3
pip install antlr4-python3-runtime
```

4. Execute o comando para gerar os analisadores léxico e sintático em Python.

```Python3
antlr4 -Dlanguage=Python3 -o output_dir LAGrammar.g4
```

3. Execute o analisador sintático com o comando, onde entrada.txt é o arquivo contendo o código fonte em LA a ser analisado e saida.txt é o arquivo de saída onde serão registradas as mensagens de erro.

```Python3
Python3 main.py entrada.txt saida.txt
```

## Casos de teste

O trabalho possui 9 casos de teste, para automatizar o processo de testar as saidas,o arquivo teste.py faz os arquivos saida.txt para todos casos de teste, como utilizar:

```Python3
Python3 teste.py
```
