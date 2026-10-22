# Biblioteca Escolar

Sistema para organizar os livros, os usuários e os empréstimos de uma biblioteca escolar. O projeto usa páginas HTML com Flask e grava os dados no PostgreSQL.

## O que dá para fazer

- Entrar com e-mail e senha e sair da conta.
- Ver o total de títulos, empréstimos ativos e usuários.
- Cadastrar, pesquisar, alterar e excluir livros.
- Cadastrar usuários e impedir e-mails repetidos.
- Registrar empréstimos e devoluções com atualização do estoque.
- Consultar o histórico e filtrar ativos, devolvidos e atrasados.
- Ver os livros mais emprestados e baixar o ranking em CSV (desafio extra).

## Como executar com Docker (opção mais simples)

É necessário instalar o Docker com Docker Compose. No Windows, abra o Docker Desktop e espere ele iniciar. Extraia o ZIP e abra um terminal **dentro da pasta que contém este README**.

```bash
docker compose up --build
```

Depois abra **http://localhost:5000**. Na primeira execução o banco é criado e recebe os exemplos automaticamente. Aguarde aparecer no terminal a mensagem de que o Flask iniciou. O banco fica salvo em um volume: parar e iniciar os serviços mantém os dados.

Conta para apresentação:

| Campo | Valor |
| --- | --- |
| E-mail | ana@escola.com |
| Senha | Biblioteca123 |

As outras contas fictícias são `bruno@escola.com` e `carla@escola.com`, com a mesma senha. As senhas do banco estão em formato de hash, sem texto puro. Para parar, use `Ctrl+C`; para iniciar de novo, use `docker compose up`.

> O script de população só roda quando o volume do banco ainda está vazio. Depois da primeira execução os números do painel mudam conforme você usa o sistema.

## Como executar sem Docker

Instale **Python 3.12** e **PostgreSQL 16 ou superior**. O banco foi verificado no PostgreSQL 16.2 e o Compose usa a versão 17. No pgAdmin ou no psql, crie uma conta local e o banco, se ainda não existirem:

```sql
CREATE USER biblioteca WITH PASSWORD 'biblioteca';
CREATE DATABASE biblioteca OWNER biblioteca;
```

Importe `banco/biblioteca.sql` no banco `biblioteca`, pelo Query Tool do pgAdmin ou pelo terminal:

```bash
psql -h localhost -U biblioteca -d biblioteca -f banco/biblioteca.sql
```

O SQL é para um banco vazio. Ele cria 3 usuários, 5 livros e 5 empréstimos. No terminal da pasta do projeto:

```bash
python -m venv .venv
```

No **Windows (PowerShell)**:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://biblioteca:biblioteca@localhost:5432/biblioteca"
$env:SECRET_KEY="chave-local-para-apresentacao"
python app.py
```

No **Linux/macOS**:

```bash
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql://biblioteca:biblioteca@localhost:5432/biblioteca'
export SECRET_KEY='chave-local-para-apresentacao'
python app.py
```

Abra **http://localhost:5000**. As variáveis são lidas do ambiente. O arquivo `.env.example` serve como modelo; o Flask não o carrega automaticamente. No Compose, o `.env` pode definir a `SECRET_KEY`.

## Entregas da avaliação

| Item | Arquivo ou tela |
| --- | --- |
| 1. Requisitos funcionais | [PDF](docs/01-requisitos-funcionais.pdf) e [texto editável](docs/01-requisitos-funcionais.md) |
| 2. DER | [Imagem](docs/02-der.png), [PDF](docs/02-der.pdf) e [Mermaid](docs/02-der.md) |
| 3. Criação e população do banco | [biblioteca.sql](banco/biblioteca.sql) |
| 4. Casos de teste | [PDF](docs/03-casos-de-teste.pdf) e [texto](docs/03-casos-de-teste.md) |
| 5. Infraestrutura | [PDF](docs/04-infraestrutura.pdf) e [texto](docs/04-infraestrutura.md) |
| 6. Login | [login.html](templates/login.html) — rota `/login` |
| 7. Tela principal | [painel.html](templates/painel.html) — rota `/painel` |
| 8. Cadastro de livros | [livros.html](templates/livros.html) — rota `/livros` |
| 9. Gestão de empréstimos | [emprestimos.html](templates/emprestimos.html) — rota `/emprestimos` |
| Desafio extra | [relatorios.html](templates/relatorios.html) e [SQL do ranking](banco/relatorios.sql) |
| Documentação técnica | [Guia em PDF](docs/05-guia-tecnico.pdf) e este README |

## Como o código foi organizado

- `app.py`: recebe os formulários, valida os dados e faz as consultas no banco.
- `templates/`: páginas HTML. O Jinja preenche as tabelas com os dados recebidos do Python.
- `static/estilo.css`: aparência e adaptação das páginas para telas menores.
- `banco/`: SQL de criação, dados de exemplo e consultas dos relatórios.
- `docs/`: requisitos, DER, testes, infraestrutura e guia técnico.
- `tests/`: testes de integração com PostgreSQL.
- `.github/workflows/testes.yml`: executa os testes quando o projeto está no GitHub.

As páginas são renderizadas no servidor. Não é necessário um frontend separado, Node.js ou uma API para este projeto. O JavaScript é usado apenas para limpar o login e confirmar exclusões e devoluções.

## Decisões do projeto

1. `quantidade` é a quantidade **disponível**, sem os exemplares emprestados. O painel conta **títulos**, não a soma de exemplares.
2. `data_prevista` guarda o prazo e `data_devolucao` guarda a devolução real. Enquanto o livro está emprestado, `data_devolucao` é `NULL`.
3. Cada empréstimo corresponde a um exemplar de um livro para um usuário.
4. A retirada e a baixa no estoque ficam na mesma transação. Se uma parte falhar, a outra também é desfeita. A linha do livro é bloqueada durante a operação.
5. Uma devolução só pode aumentar o estoque uma vez. O histórico fica preservado.
6. Livros com qualquer empréstimo no histórico não podem ser excluídos. Para testar exclusão, cadastre um livro novo sem empréstimos.
7. Todos os usuários autenticados têm as mesmas permissões, pois a atividade não pediu perfis diferentes. O cadastro de usuários fica dentro do sistema.
8. O ranking conta empréstimos ativos e devolvidos; em empate, ordena pelo título.

## Testes automatizados

Os testes apagam e recriam as três tabelas do banco indicado. Use **somente um banco exclusivo para testes**, nunca o banco de apresentação. No PostgreSQL, crie `biblioteca_testes` com a conta `biblioteca` como dona:

```sql
CREATE DATABASE biblioteca_testes OWNER biblioteca;
```

Com o ambiente Python ativado, no PowerShell:

```powershell
$env:TEST_DATABASE_URL="postgresql://biblioteca:biblioteca@localhost:5432/biblioteca_testes"
python -m pytest -q
```

No Linux/macOS:

```bash
TEST_DATABASE_URL='postgresql://biblioteca:biblioteca@localhost:5432/biblioteca_testes' python -m pytest -q
```

Sem `TEST_DATABASE_URL` os testes são marcados como ignorados. Os cenários manuais estão no documento de casos de teste.

## Roteiro rápido para apresentar

1. Tente entrar com senha errada e depois use a conta de demonstração.
2. Mostre os totais iniciais: **5 títulos, 3 empréstimos ativos e 3 usuários**.
3. Cadastre um livro com 1 exemplar, pesquise e altere a categoria.
4. Empreste o exemplar: o estoque passa para 0 e o livro fica indisponível na seleção.
5. Registre a devolução: o estoque volta para 1. Mostre o histórico e o filtro de atrasados.
6. Mostre o relatório: inicialmente **O Pequeno Príncipe** aparece com 2 empréstimos. Baixe o CSV.
7. Cadastre outro livro sem empréstimos e exclua, para demonstrar essa função.

## Repositório no GitHub

O projeto está disponível em https://github.com/Sp3llr/biblioteca-escolar.

Para baixar pelo Git:

```bash
git clone https://github.com/Sp3llr/biblioteca-escolar.git
cd biblioteca-escolar
docker compose up --build
```

Também dá para usar **Code > Download ZIP** no GitHub, extrair a pasta e seguir as instruções de execução acima.

## Escopo

Projeto didático para avaliação. A chave e as credenciais do Compose são de demonstração. Uma implantação pública precisaria de configuração própria de servidor, HTTPS, permissões por perfil e rotina de backup. Não há recuperação de senha nem multas, pois não fazem parte do enunciado.
