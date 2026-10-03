CREATE TABLE IF NOT EXISTS metadata (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS variaveis (
    id_variavel TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    valor_real REAL,
    valor_texto TEXT,
    unidade_si TEXT NOT NULL,
    unidade_codigo TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('REAL', 'TEXT')),
    categoria TEXT NOT NULL,
    eh_saida INTEGER NOT NULL DEFAULT 0 CHECK (eh_saida IN (0, 1)),
    descricao TEXT,
    atualizado_em TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_variaveis_saida
ON variaveis(eh_saida);

CREATE INDEX IF NOT EXISTS idx_variaveis_categoria
ON variaveis(categoria);

CREATE TABLE IF NOT EXISTS calculos (
    id_calculo TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    versao TEXT NOT NULL,
    formula TEXT NOT NULL,
    unidade_saida TEXT,
    descricao TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dependencias_calculo (
    id_calculo TEXT NOT NULL,
    id_variavel TEXT NOT NULL,
    papel TEXT NOT NULL CHECK (papel IN ('entrada', 'saida')),
    ordem INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id_calculo, id_variavel, papel),
    FOREIGN KEY (id_calculo)
        REFERENCES calculos(id_calculo)
        ON DELETE CASCADE,
    FOREIGN KEY (id_variavel)
        REFERENCES variaveis(id_variavel)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_dependencias_calculo
ON dependencias_calculo(id_calculo, papel);

CREATE TABLE IF NOT EXISTS execucoes (
    id_execucao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_calculo TEXT NOT NULL,
    executado_em TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCESSO', 'ERRO')),
    mensagem TEXT,
    FOREIGN KEY (id_calculo)
        REFERENCES calculos(id_calculo)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_execucoes_calculo_data
ON execucoes(id_calculo, executado_em);

CREATE TABLE IF NOT EXISTS execucao_valores (
    id_execucao INTEGER NOT NULL,
    id_variavel TEXT NOT NULL,
    papel TEXT NOT NULL CHECK (papel IN ('entrada', 'saida')),
    valor_real REAL,
    valor_texto TEXT,
    unidade_si TEXT NOT NULL,
    PRIMARY KEY (id_execucao, id_variavel, papel),
    FOREIGN KEY (id_execucao)
        REFERENCES execucoes(id_execucao)
        ON DELETE CASCADE,
    FOREIGN KEY (id_variavel)
        REFERENCES variaveis(id_variavel)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS variaveis_legado (
    chave TEXT NOT NULL,
    valor TEXT,
    migrado_em TEXT NOT NULL
);
