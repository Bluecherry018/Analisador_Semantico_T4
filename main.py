import sys
from antlr4 import *
from LAGrammarLexer import LAGrammarLexer
from LAGrammarParser import LAGrammarParser
from antlr4.error.ErrorListener import ErrorListener
import re

class SemanticErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def add_error(self, line, msg):
        if (line, msg) not in self.errors:
            self.errors.append((line, msg))

    def has_errors(self):
        return len(self.errors) > 0

    def print_errors(self, output_file):
        self.errors.sort(key=lambda x: x[0])  # Ordena os erros pela linha
        with open(output_file, 'w') as f:
            for error in self.errors:
                f.write(f"Linha {error[0]}: {error[1]}\n")
            f.write("Fim da compilacao\n")

class LAGrammarSemanticAnalyzer(ParseTreeListener):
    def __init__(self, error_listener):
        self.symbol_table = {}
        self.local_symbol_table = {}
        self.current_scope = "global"
        self.error_listener = error_listener
        self.in_function = False
        self.in_procedure = False
        self.in_constante = False
        self.procedure_table = {}
        self.nome = {}
        self.function = {}
        self.var_procedimento = {}
        self.tipos = {}
        self.registros = {}
        self.declaracao = {}
        self.escreva = {}


    def enterDeclaracoes_variaveis(self, ctx: LAGrammarParser.Declaracoes_variaveisContext):
        for declaracao_var in ctx.declaracao_variavel():
            self.enterDeclaracao_variavel(declaracao_var)


    def enterDeclaracao_variavel(self, ctx: LAGrammarParser.Declaracao_variavelContext):
        tipo = ctx.tipo().getText()
        identificadores = ctx.identificadores().identificador()

        for identificador in identificadores:
            nome = identificador.getText()
            nome_lista = re.sub(r'\[\d+\]$', '', nome)
            self.declaracao = nome_lista  
            # print(self.declaracao)    

            # Verifica se o identificador já está na tabela de símbolos gerais
            if nome in self.symbol_table:
                self.error_listener.add_error(identificador.start.line, f"identificador {nome} ja declarado anteriormente")
            else:
                # Verifica se o identificador já está na tabela de procedimentos
                if nome in self.procedure_table:
                    self.error_listener.add_error(identificador.start.line, f"identificador {nome} ja declarado anteriormente")
                else:
                  
                    if tipo in self.tipos:
                        self.error_listener.add_error(identificador.start.line, f"identificador {nome} ja declarado como tipo")
                    else:
                        self.symbol_table[nome] = tipo
    


    def enterFuncoes(self, ctx: LAGrammarParser.FuncaoContext):
        for funcao_ctx in ctx.funcao():
            self.enterFuncao(funcao_ctx)
            
    def enterFuncao(self, ctx: LAGrammarParser.FuncaoContext):
        self.in_function = True

        nome_funcao = ctx.IDENT().getText()
        tipo_retorno = ctx.tipo().getText()
        parametros = ctx.parametros().parametro() if ctx.parametros() else []

        # Verifica se a função já foi declarada anteriormente
        if nome_funcao in self.symbol_table:
            self.error_listener.add_error(ctx.start.line, f"funcao {nome_funcao} já declarada anteriormente")
        else:
            # Adiciona a função à tabela de símbolos
            self.symbol_table[nome_funcao] = {
                'tipo_retorno': tipo_retorno,
                'parametros': [(param.identificador().getText(), param.tipo().getText()) for param in parametros]
            }


        self.local_symbol_table = {param.identificador().getText(): None for param in parametros}



    def enterProcedimentos(self, ctx: LAGrammarParser.ProcedimentoContext):
        for procediemento_ctx in ctx.procedimento():
            self.enterProcedimento(procediemento_ctx)

    def enterProcedimento(self, ctx: LAGrammarParser.ProcedimentoContext):
        self.in_procedure = True
        nome_procedimento = ctx.IDENT().getText()
        parametros = ctx.parametros().parametro() if ctx.parametros() else []

        # Verifica se o procedimento já foi declarado anteriormente
        if nome_procedimento in self.symbol_table:
            self.error_listener.add_error(ctx.start.line, f"procedimento {nome_procedimento} já declarado anteriormente")
        else:
            # Adiciona o procedimento à tabela de símbolos de procedimentos
            self.symbol_table[nome_procedimento] = {
                'parametros': [(param.identificador().getText(), param.tipo().getText()) for param in parametros]
            }
            self.local_symbol_table = {param.identificador().getText() for param in parametros}


    def exitProcedimento(self, ctx: LAGrammarParser.ProcedimentoContext):
        self.in_procedure = False

    def enterChamada_procedimento_cmd(self, ctx: LAGrammarParser.Chamada_procedimento_cmdContext):
        nome_procedimento = ctx.identificador().getText()
        argumentos = ctx.argumentos().expressao() if ctx.argumentos() else []

        if nome_procedimento in self.symbol_table:
            params_esperados = self.symbol_table[nome_procedimento]['parametros']
            params_fornecidos = [self.get_tipo_expressao(arg) for arg in argumentos]

            if len(params_esperados) != len(params_fornecidos):
                self.error_listener.add_error(ctx.start.line, f"incompatibilidade de parâmetros na chamada de {nome_procedimento}")
        else:
            self.error_listener.add_error(ctx.start.line, f"procedimento '{nome_procedimento}' não declarado")


    def enterConstante(self, ctx: LAGrammarParser.ConstanteContext):
        nome_constante = ctx.IDENT().getText()
        tipo_constante = ctx.tipo().getText()
        valor_constante = ctx.expressao().getText()

        if nome_constante in self.symbol_table:
            self.error_listener.add_error(ctx.start.line, f"Constante '{nome_constante}' já declarada anteriormente")
        else:
            self.symbol_table[nome_constante] = {
                'tipo': tipo_constante,
                'valor': valor_constante,
                'constante': True
            }
    def exitConstante(self, ctx: LAGrammarParser.ConstanteContext):
        self.in_procedure = False
    
    def enterDeclaracao_tipo_lista(self, ctx: LAGrammarParser.Declaracao_tipo_listaContext):
        nome_tipo = ctx.IDENT().getText()
        registro_ctx = ctx.registro()
        
        if nome_tipo in self.symbol_table:
            self.error_listener.add_error(ctx.start.line, f"Tipo '{nome_tipo}' ja declarado anteriormente")
        else:
            campos_registro = self.enterRegister(registro_ctx)
            self.symbol_table[nome_tipo] = {
                'tipo': 'registro',
                'campos': campos_registro
            }

    def enterRegister(self, ctx: LAGrammarParser.RegistroContext):
        campos = ctx.campos_registro().campo_registro()
        registro_campos = []
        registros = set()


        for campo in campos:
            identificadores_ctx = campo.identificadores().identificador()
            tipo = campo.tipo().getText()

            for ident_ctx in identificadores_ctx:
                ident = ident_ctx.getText()
                registro_campos.append((ident,tipo))
                registros.add(ident) 

        self.registros = registros

        return registro_campos


    def exitFuncao(self, ctx: LAGrammarParser.FuncaoContext):
        self.in_function = False

    def enterRetorno(self, ctx: LAGrammarParser.RetornoContext):
        if not self.in_function:
            self.error_listener.add_error(ctx.start.line, "comando retorne nao permitido nesse escopo")

    def enterChamada_funcao_cmd(self, ctx: LAGrammarParser.Chamada_funcao_cmdContext):
        nome_funcao = ctx.identificador().getText()
        argumentos = ctx.argumentos().expressao() if ctx.argumentos() else []

        

        if nome_funcao in self.symbol_table:
            funcao_info = self.symbol_table[nome_funcao]
            if isinstance(funcao_info, dict) and 'parametros' in funcao_info:
                params_esperados = funcao_info['parametros']
                params_fornecidos = [self.get_tipo_expressao(arg) for arg in argumentos]


                if len(params_esperados) != len(params_fornecidos):
                    self.error_listener.add_error(ctx.start.line, f"incompatibilidade de numero de parametros na chamada de {nome_funcao}")
                else:
                    for i, (esperado, fornecido) in enumerate(zip(params_esperados, params_fornecidos)):
                        if esperado[1] != fornecido and fornecido != 'indefinido':
                            self.error_listener.add_error(ctx.start.line, f"incompatibilidade de numero de parametros na chamada de {nome_funcao}")
            
    def enterIdentificador(self, ctx: LAGrammarParser.IdentificadorContext):
        nome = ctx.getText()

        if '.' in nome:
            registro, campo = nome.split('.')


            if campo in self.registros:
                return  
            else:
                if registro in self.symbol_table:
                    return
                else:
                    self.error_listener.add_error(ctx.start.line, f"identificador {nome} nao declarado")
                    

    def exitAtribuicao_cmd(self, ctx: LAGrammarParser.Atribuicao_cmdContext):
        identificador = ctx.identificador()
        expressao = ctx.expressao()

        if identificador is not None:
            self.processaAtribuicao(identificador, expressao)
        else:
            self.error_listener.add_error(ctx.start.line, f"atribuicao nao compativel para {ctx.getText().split('<-')[0]}")

    def processaAtribuicao(self, identificador, expressao):
        nome_identificador = identificador.getText() if identificador is not None else None
        
        if nome_identificador is not None:
            # Verifica se o identificador é uma função
            if nome_identificador in self.symbol_table and isinstance(self.symbol_table[nome_identificador], dict):
                self.error_listener.add_error(identificador.start.line, f"{nome_identificador} é uma função e não pode ser atribuída diretamente")
            else:
                self.enterIdentificador(identificador)  # Verifica se o identificador está na tabela de símbolos

                tipo_variavel = self.getTipoVariavel(nome_identificador)
                
                # Verifica se a expressão é um endereço (&)
                if expressao.getText().startswith('&'):
                    self.processaEnderecoAtribuicao(identificador, expressao)
                elif expressao.getText().startswith('-'):
                    self.processaAtribuicaoNegativa(identificador, expressao)
                else:
                    tipo_expressao = self.get_tipo_expressao(expressao)

                    if tipo_variavel is None and not tipo_expressao is not None:
                        self.error_listener.add_error(identificador.start.line, f"atribuicao nao compativel para {nome_identificador}")
                    elif tipo_expressao is None:
                        self.error_listener.add_error(identificador.start.line, f"atribuicao nao compativel para {nome_identificador}")
                    elif nome_identificador not in self.symbol_table :
                        if '.' in nome_identificador:
                            registro, campo = nome_identificador.split('.')
                            if campo in self.registros:
                                return  # Identificador dentro de um registro está corretamente declarado
                            else:
                                if registro in self.symbol_table:
                                    return
                                else:
                                    self.error_listener.add_error(identificador.start.line, f"identificador {nome_identificador} nao declarado")
                        else:
                            self.error_listener.add_error(identificador.start.line, f"identificador {nome_identificador} nao declarado")

        else:
            self.error_listener.add_error(identificador.start.line, "Identificador não encontrado para atribuição")

    def processaAtribuicaoNegativa(self, identificador, expressao):
        # Implementação específica para atribuições com expressão negativa
        nome_identificador = identificador.getText()

        # Remove o sinal "-" da expressão para obter o identificador correto
        identificador_negado = expressao.getText()[1:]

        # Verifica se o identificador está na tabela de símbolos
        if nome_identificador in self.symbol_table:
            tipo_variavel = self.symbol_table[nome_identificador]
            tipo_expressao = self.get_tipo_expressao(identificador_negado)

            if tipo_variavel and tipo_expressao:
                if not self.tipo_compativel(tipo_variavel, tipo_expressao):
                    self.error_listener.add_error(identificador.start.line, f"atribuicao nao compativel para {nome_identificador}")
            elif tipo_variavel is None:
                self.error_listener.add_error(identificador.start.line, f"atribuicao nao compativel para {nome_identificador}")
              
    def processaEnderecoAtribuicao(self, identificador, expressao):
        nome_identificador = identificador.getText()

        # Verifica se o identificador existe na tabela de símbolos
        if nome_identificador in self.symbol_table:
            tipo_variavel = self.symbol_table[nome_identificador]
            tipo_expressao = expressao.getText()[1:]  # Remove o '&'

            if tipo_variavel and tipo_expressao:
                if not self.tipo_compativel(tipo_variavel, tipo_expressao):
                    self.error_listener.add_error(identificador.start.line, f"atribuicao nao compativel para {nome_identificador}")
            elif tipo_variavel is None:
                self.error_listener.add_error(identificador.start.line, f"atribuicao nao compativel para {nome_identificador}")
        else:
            self.error_listener.add_error(identificador.start.line, f"identificador {nome_identificador} nao declarado")


    def getTipoVariavel(self, nome_identificador):
        # Verifica se é um campo de registro (ex: ponto1.x)
        if '.' in nome_identificador:
            registro, campo = nome_identificador.split('.')
            if registro in self.symbol_table and isinstance(self.symbol_table[registro], dict) and campo in self.symbol_table[registro]:
                return self.symbol_table[registro][campo]
            else:
                return None
        else:
            return self.symbol_table.get(nome_identificador)

        
    def verificar_tipo_variavel(self, identificador):
    # Verifica se o identificador existe na tabela de símbolos
        if identificador in self.symbol_table:
            # Verifica se há uma chave 'tipo' no dicionário associado ao identificador
            if 'tipo' in self.symbol_table[identificador]:
                return self.symbol_table[identificador]['tipo']  # Retorna o tipo da variável
            else:
                return None  # Ou retorne algo que indique que o tipo não está definido
        else:
            return None 

    def get_tipo_expressao(self, ctx: LAGrammarParser.ExpressaoContext):
        if isinstance(ctx, LAGrammarParser.ExpressaoContext):
        # Verifica se a expressão é um literal
            if ctx.literal():
                return self.getTipoVariavel(ctx.literal().getText())
            elif ctx.NUM_INT():
                return "inteiro"
            elif ctx.NUM_REAL():
                return "real"
            if ctx.IDENT():
                nome_identificador = ctx.IDENT().getText()
                if '[' in nome_identificador:
                    nome_base = nome_identificador.split('[')[0].strip()
                    if nome_base in self.symbol_table:
                        return self.symbol_table[nome_base]['tipo']
                    else:
                        self.error_listener.add_error(ctx.start.line, f"Identificadoooooor {nome_identificador} não declarado")
                        return "tipo_indefinido"
                elif nome_identificador in self.symbol_table:
                    return self.symbol_table[nome_identificador]['tipo']
                else:
                    self.error_listener.add_error(ctx.start.line, f"Identiiificador {nome_identificador} não declarado")
                    return "tipo_indefinido"

            elif ctx.identificador():
                ident_texto = ctx.identificador().getText()
                # Verificar se é um identificador de variável declarada
                tipo_variavel = self.verificar_tipo_variavel(ident_texto)
                if tipo_variavel:
                    return tipo_variavel  # Retorna o tipo da variável declarada
                else:
                    return "indefinido"
            elif ctx.chamada_funcao_cmd():
                # Lógica para determinar o tipo de retorno da função chamada
                nome_funcao = ctx.chamada_funcao_cmd().identificador().getText()
                if nome_funcao in self.symbol_table:
                    return self.symbol_table[nome_funcao]['tipo_retorno']
                else:
                    return "tipo_de_retorno_desconhecido"
            elif ctx.chamada_procedimento_cmd():
                nome_procedimento = ctx.chamada_procedimento_cmd().identificador().getText()
                if nome_procedimento in self.procedure_table:
                    return 'procedimento'
                else:
                    self.error_listener.add_error(ctx.start.line, f"procedimento '{nome_procedimento}' não declarado")
                    return 'desconhecido'
            elif ctx.identificador():
                nome_identificador = ctx.identificador().getText()
                return self.getTipoVariavel(nome_identificador)  # Retorna o tipo da variável na tabela de símbolos
            elif ctx.ponteiro():
                return "ponteiro"  # Verificar como tratar ponteiros
            elif ctx.getChild(0).getText() == '-':
                return self.get_tipo_expressao(ctx.expressao(0))  # Retorna o tipo do identificador após o "-"
            elif ctx.endereco():
                return "endereco"  # Verificar como tratar endereços
            elif ctx.getChild(1) and (ctx.getChild(1).getText() in ['+', '-', '*', '/', '>', '<', '>=', '<=', 'e', 'ou', '<>']):
                tipo_expr1 = self.get_tipo_expressao(ctx.expressao(0))
                tipo_expr2 = self.get_tipo_expressao(ctx.expressao(1))
                if tipo_expr1 == tipo_expr2:
                    return tipo_expr1
                else:
                    return "tipo_indefinido"
            else:
                return "tipo_indefinido"

    def tipo_compativel(self, tipo_var, tipo_expr):
        if tipo_var == tipo_expr:
            return True
        if (tipo_var == "real" and tipo_expr == "inteiro") or (tipo_var == "inteiro" and tipo_expr == "real"):
            return True
        return False

def main(input_file, output_file):
    input_stream = FileStream(input_file, encoding='utf-8')
    lexer = LAGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = LAGrammarParser(stream)
    
    # Remover o listener de erros padrão e adicionar o nosso customizado
    parser.removeErrorListeners()
    error_listener = SemanticErrorListener()
    parser.addErrorListener(error_listener)
    
    tree = parser.programa()

    analyzer = LAGrammarSemanticAnalyzer(error_listener)
    walker = ParseTreeWalker()
    walker.walk(analyzer, tree)

    error_listener.print_errors(output_file)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: Python3 main.py entrada.txt saida.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
