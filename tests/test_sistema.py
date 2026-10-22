"""Testes de integração: usam um banco PostgreSQL exclusivo para testes."""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import psycopg
import pytest
from app import app


@pytest.fixture(autouse=True)
def banco():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url:
        pytest.skip('Defina TEST_DATABASE_URL apontando para um banco exclusivo de testes.')
    app.config.update(TESTING=True, DATABASE_URL=url, SECRET_KEY='chave-dos-testes')
    with psycopg.connect(url, autocommit=True) as con:
        con.execute('DROP TABLE IF EXISTS emprestimo, livro, usuario CASCADE')
        con.execute((Path(__file__).parents[1] / 'banco/biblioteca.sql').read_text())
    yield


@pytest.fixture
def cliente():
    return app.test_client()


def postar(cliente, rota, **dados):
    cliente.get('/login')
    with cliente.session_transaction() as sessao:
        token = sessao['csrf']
    return cliente.post(rota, data={'csrf': token, **dados}, follow_redirects=True)


def entrar(cliente):
    return postar(cliente, '/login', email='ana@escola.com', senha='Biblioteca123')


def consultar(sql, dados=()):
    with psycopg.connect(app.config['DATABASE_URL']) as con:
        return con.execute(sql, dados).fetchone()[0]


def emprestar(cliente, livro=1, usuario=1, **extras):
    dados = dict(id_usuario=usuario, id_livro=livro,
                 data_emprestimo=str(date.today()),
                 data_prevista=str(date.today() + timedelta(days=7)))
    dados.update(extras)
    return postar(cliente, '/emprestimos', **dados)


def test_login_valido_e_telas(cliente):
    assert 'Um dia de cada leitura' in entrar(cliente).text
    for rota in ['/painel','/livros','/emprestimos','/usuarios','/relatorios']:
        assert cliente.get(rota).status_code == 200


def test_login_invalido_e_obrigatorios(cliente):
    assert 'inválidos' in postar(cliente, '/login', email='ana@escola.com', senha='errada').text
    assert 'Preencha' in postar(cliente, '/login', email='', senha='').text
    assert cliente.get('/painel').status_code == 302


def test_rotas_protegidas_e_csrf(cliente):
    for rota in ['/painel','/livros','/emprestimos','/usuarios','/relatorios']:
        assert cliente.get(rota).status_code == 302
    entrar(cliente)
    assert cliente.post('/livros', data={}).status_code == 400


def test_crud_e_pesquisa(cliente):
    entrar(cliente)
    assert 'Livro salvo' in postar(cliente, '/livros', titulo='Livro Teste', autor='Autor', categoria='Teste', quantidade=2).text
    codigo = consultar("SELECT id_livro FROM livro WHERE titulo='Livro Teste'")
    assert 'Livro Teste' in cliente.get('/livros?q=Teste').text
    assert 'Dom Casmurro' not in cliente.get('/livros?q=Teste').text
    postar(cliente, '/livros', id_livro=codigo, titulo='Livro Alterado', autor='Autor', categoria='Teste', quantidade=4)
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=%s', (codigo,)) == 4
    postar(cliente, f'/livros/{codigo}/excluir')
    assert consultar('SELECT COUNT(*) FROM livro WHERE id_livro=%s', (codigo,)) == 0


@pytest.mark.parametrize('quantidade', [-1, '1.5', 'abc', ''])
def test_quantidade_invalida(cliente, quantidade):
    entrar(cliente)
    postar(cliente, '/livros', titulo='Inválido', autor='Autor', categoria='Teste', quantidade=quantidade)
    assert consultar('SELECT COUNT(*) FROM livro') == 5


def test_campos_obrigatorios_e_zero(cliente):
    entrar(cliente)
    postar(cliente, '/livros', titulo=' ', autor='Autor', categoria='Teste', quantidade=1)
    assert consultar('SELECT COUNT(*) FROM livro') == 5
    postar(cliente, '/livros', titulo='Sem estoque', autor='Autor', categoria='Teste', quantidade=0)
    assert consultar('SELECT COUNT(*) FROM livro') == 6


def test_emprestimo_com_estoque(cliente):
    entrar(cliente)
    assert 'Empréstimo registrado' in emprestar(cliente).text
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=1') == 2
    assert consultar('SELECT COUNT(*) FROM emprestimo') == 6


def test_sem_estoque(cliente):
    entrar(cliente)
    assert 'sem estoque disponível' in emprestar(cliente, livro=5).text
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=5') == 0
    assert consultar('SELECT COUNT(*) FROM emprestimo') == 5


def test_devolucao_unica(cliente):
    entrar(cliente)
    assert 'Devolução registrada' in postar(cliente, '/emprestimos/5/devolver').text
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=5') == 1
    assert 'já foi devolvido' in postar(cliente, '/emprestimos/5/devolver').text
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=5') == 1


def test_datas_e_usuario_invalidos(cliente):
    entrar(cliente)
    assert 'anterior' in emprestar(cliente, data_prevista=str(date.today()-timedelta(days=1))).text
    assert 'futuro' in emprestar(cliente, data_emprestimo=str(date.today()+timedelta(days=1))).text
    assert 'não encontrado' in emprestar(cliente, usuario=9999).text
    assert consultar('SELECT COUNT(*) FROM emprestimo') == 5
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=1') == 3


def test_preservar_historico(cliente):
    entrar(cliente)
    assert 'histórico' in postar(cliente, '/livros/1/excluir').text
    assert consultar('SELECT COUNT(*) FROM livro') == 5


def test_relatorio_e_filtros(cliente):
    entrar(cliente)
    html = cliente.get('/relatorios').text
    assert html.index('O Pequeno Príncipe') < html.index('Dom Casmurro')
    csv = cliente.get('/relatorios?formato=csv')
    assert csv.status_code == 200
    assert 'O Pequeno Príncipe;Antoine de Saint-Exupéry;2' in csv.text
    assert '<b>Bruno Lima</b>' not in cliente.get('/emprestimos?status=devolvidos').text
    assert '<b>Carla Santos</b>' in cliente.get('/emprestimos?status=atrasados').text


def test_usuario_e_logout(cliente):
    entrar(cliente)
    postar(cliente, '/usuarios', nome='Davi', email='davi@escola.com', senha='Senha123')
    assert consultar('SELECT COUNT(*) FROM usuario') == 4
    assert 'já está cadastrado' in postar(cliente, '/usuarios', nome='Davi', email='davi@escola.com', senha='Senha123').text
    postar(cliente, '/sair')
    assert cliente.get('/painel').status_code == 302
    assert 'Um dia de cada leitura' in postar(cliente, '/login', email='davi@escola.com', senha='Senha123').text


def test_ultimo_exemplar_simultaneo():
    def solicitar():
        with app.test_client() as cliente:
            entrar(cliente)
            return emprestar(cliente, livro=3).text
    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(lambda _: solicitar(), range(2)))
    assert sum('Empréstimo registrado' in html for html in respostas) == 1
    assert sum('sem estoque disponível' in html for html in respostas) == 1
    assert consultar('SELECT quantidade FROM livro WHERE id_livro=3') == 0
    assert consultar('SELECT COUNT(*) FROM emprestimo') == 6
