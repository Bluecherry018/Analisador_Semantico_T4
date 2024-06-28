grammar LAGrammar;

programa: declaracoes 'algoritmo' corpo 'fim_algoritmo';

declaracoes: (decl_local_global)*;

decl_local_global: declaracao_global | declaracao_local | constante;

declaracao_local: 'declare' declaracao_variavel;

declaracao_global: declaracoes_variaveis | procedimento | funcao | declaracao_tipo;

declaracoes_variaveis: 'declare' declaracao_variavel (',' declaracao_variavel)* ('fim_declare' | ';')?;


declaracao_variavel: identificadores DOISPONTOS tipo;

identificadores: identificador (',' identificador)*;

corpo: (declaracao_local | comandos | funcao | procedimento | registro | declaracao_tipo)*;

comandos: comando (comando)*;

comando: leia_cmd
       | escreva_cdm
       | cmd_para
       | atribuicao_cmd
       | chamada_tipo_cdm
       | chamada_procedimento_cmd
       | chamada_funcao_cmd
       | cmd_condicional
       | cmd_enquanto
       | retorno;

leia_cmd: 'leia' '(' identificadores ')';

escreva_cdm: 'escreva' '(' (mensagem_literal | expressao) (',' (mensagem_literal | expressao))* ')';

mensagem_literal: CADEIA;

atribuicao_cmd: (identificador | ponteiro) '<-' expressao;

chamada_funcao_cmd: identificador '(' argumentos? ')';

chamada_tipo_cdm: identificador ':' registro;

chamada_procedimento_cmd: identificador '(' argumentos? ')';

argumentos: expressao (',' expressao)*;

cmd_condicional: 'se' expressao 'entao' corpo ('senao' corpo)? 'fim_se';

cmd_enquanto: 'enquanto' expressao 'faca' corpo 'fim_enquanto';

cmd_para: 'para' identificador '<-' expressao 'ate' expressao ('passo' expressao)? 'faca' corpo 'fim_para';

retorno: 'retorne' expressao;

expressao: literal
         | NUM_INT
         | NUM_REAL
         | IDENT
         | identificador
         | ponteiro
         |'-' identificador
         | endereco
         | chamada_funcao_cmd
         | chamada_tipo_cdm
         | chamada_procedimento_cmd
         | '(' expressao ')'
         | expressao ('+'|'-'|'*'|'/'|'>'|'<'|'>='|'<='|'<>'|'=') expressao
         | expressao logico expressao;

literal: CADEIA | LOGICO | endereco | IDENT;

tipo: 'literal'
    | 'inteiro'
    | 'real'
    | 'logico'
    | '^' tipo
    | 'registro'
    | 'endereco'
    | IDENT;

registro: 'registro' campos_registro 'fim_registro';

campos_registro: campo_registro (campo_registro)+;

campo_registro: identificadores ':' tipo;

declaracao_tipo: 'tipo' declaracoes_tipos;

declaracoes_tipos: (declaracao_tipo_lista)+;

declaracao_tipo_lista: IDENT ':' registro;

identificador: IDENT ('.' IDENT)* dimensao?;

constante: 'constante' IDENT DOISPONTOS tipo '=' expressao;


dimensao: ('[' expressao ']');

ponteiro: '^' tipo;

logico: 'e' | 'ou';

endereco: '&';


parametros: parametro (',' parametro)*;

parametro: 'var'? identificador ':' tipo;

procedimento: 'procedimento' IDENT '(' parametros? ')' bloco 'fim_procedimento';

funcao: 'funcao' IDENT '(' parametros? ')' ':' tipo bloco 'fim_funcao';

bloco: '{' corpo '}';

DOISPONTOS: ':';

DIFERENTE : '<>';

IDENT: [a-zA-Z] [a-zA-Z0-9_]*;

CADEIA: '"' (~('\n'|'"'))* '"';

LOGICO: 'verdadeiro' | 'falso';

NUM_INT: [0-9]+;

NUM_REAL: [0-9]+'.'[0-9]+;

WS: [ \t\r\n]+ -> skip;

COMMENTS: '{' ~('}')* '}' -> skip;

ErrorChar: .;
