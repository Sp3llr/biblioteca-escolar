# Verificação do projeto

Verificação feita em 22/10/2026.

## Integração com o banco

Ambiente: Python 3.12 e PostgreSQL 16.2.

Comando: `python -m pytest -q`, com `TEST_DATABASE_URL` definido para um banco exclusivo de testes.

Resultado: **17 testes aprovados em 4,19 segundos**.

Foram verificados login, acesso às telas, proteção de formulários, cadastro, pesquisa, alteração e exclusão de livros, validações de quantidade e datas, empréstimos, devoluções, histórico, ranking, CSV, cadastro de usuário e saída. Duas solicitações simultâneas para o último exemplar também foram testadas: apenas uma foi aceita.

## Navegador

Conferidas as seis telas em desktop e login, painel, livros e empréstimos em largura de celular. O botão Limpar do login apagou os campos.

Um fluxo com servidor e banco reais foi executado no navegador: login, cadastro de um livro, empréstimo do último exemplar, bloqueio da opção sem estoque, devolução, download do CSV e saída. O fluxo terminou sem falha.

## Documentação

Os cinco PDFs foram renderizados e revisados. O DER em imagem corresponde às tabelas do SQL. Os links internos do README e a presença das nove entregas foram conferidos.

## Limites da verificação

O comando Docker Compose foi preparado, mas não executado neste ambiente. O banco e a aplicação foram testados diretamente. Após a publicação, o GitHub Actions executou a suíte com sucesso no PostgreSQL 17. A execução pode ser consultada na aba Actions do repositório.
