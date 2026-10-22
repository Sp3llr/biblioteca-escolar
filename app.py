"""Rotas da biblioteca. As consultas usam parâmetros para receber os dados dos formulários."""
import csv
import io
import os
import secrets
from datetime import date
from functools import wraps

import psycopg
from psycopg.rows import dict_row
from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for, Response)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(32)),
    DATABASE_URL=os.environ.get('DATABASE_URL',
        'postgresql://biblioteca:biblioteca@localhost:5432/biblioteca'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


def conectar():
    return psycopg.connect(app.config['DATABASE_URL'], row_factory=dict_row)


def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('login'))
        return funcao(*args, **kwargs)
    return verificar


@app.before_request
def proteger_formularios():
    # O token impede que outro site envie um formulário usando nossa sessão.
    if 'csrf' not in session:
        session['csrf'] = secrets.token_hex(24)
    if request.method == 'POST':
        if not secrets.compare_digest(session['csrf'], request.form.get('csrf', '')):
            abort(400, 'Formulário expirado. Atualize a página e tente novamente.')


@app.get('/')
def inicio():
    return redirect(url_for('painel') if 'id_usuario' in session else url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        if not email or not senha:
            flash('Preencha o e-mail e a senha.', 'erro')
        else:
            with conectar() as con:
                usuario = con.execute('SELECT * FROM usuario WHERE email = %s', (email,)).fetchone()
            if usuario and check_password_hash(usuario['senha'], senha):
                session.clear()
                session.update(id_usuario=usuario['id_usuario'], nome=usuario['nome'],
                               csrf=secrets.token_hex(24))
                return redirect(url_for('painel'))
            flash('E-mail ou senha inválidos.', 'erro')
    return render_template('login.html')


@app.post('/sair')
@login_obrigatorio
def sair():
    session.clear()
    return redirect(url_for('login'))


@app.get('/painel')
@login_obrigatorio
def painel():
    with conectar() as con:
        numeros = con.execute('''SELECT
            (SELECT COUNT(*) FROM livro) AS livros,
            (SELECT COUNT(*) FROM emprestimo WHERE data_devolucao IS NULL) AS ativos,
            (SELECT COUNT(*) FROM usuario) AS usuarios''').fetchone()
        recentes = con.execute('''SELECT e.*, u.nome, l.titulo FROM emprestimo e
            JOIN usuario u USING(id_usuario) JOIN livro l USING(id_livro)
            ORDER BY id_emprestimo DESC LIMIT 5''').fetchall()
    return render_template('painel.html', numeros=numeros, recentes=recentes)


@app.route('/livros', methods=['GET', 'POST'])
@login_obrigatorio
def livros():
    if request.method == 'POST':
        campos = {chave: request.form.get(chave, '').strip()
                  for chave in ['titulo', 'autor', 'categoria', 'quantidade']}
        try:
            if not all(campos.values()):
                raise ValueError('Preencha todos os campos do livro.')
            quantidade = int(campos['quantidade'])
            if quantidade > 2147483647:
                raise ValueError('A quantidade ultrapassou o limite permitido.')
            if quantidade < 0:
                raise ValueError('A quantidade não pode ser negativa.')
            if any(len(campos[c]) > limite for c, limite in
                   [('titulo', 150), ('autor', 120), ('categoria', 60)]):
                raise ValueError('Um dos textos ultrapassou o tamanho permitido.')
            dados = (campos['titulo'], campos['autor'], campos['categoria'], quantidade)
            with conectar() as con:
                codigo = request.form.get('id_livro')
                if codigo:
                    if not codigo.isdigit():
                        abort(400)
                    resultado = con.execute('''UPDATE livro SET titulo=%s, autor=%s,
                        categoria=%s, quantidade=%s WHERE id_livro=%s''', dados + (int(codigo),))
                    if resultado.rowcount == 0:
                        abort(404)
                else:
                    con.execute('''INSERT INTO livro (titulo, autor, categoria, quantidade)
                        VALUES (%s, %s, %s, %s)''', dados)
            flash('Livro salvo.', 'sucesso')
            return redirect(url_for('livros'))
        except ValueError as erro:
            flash(str(erro) if not str(erro).startswith('invalid literal') else
                  'Informe uma quantidade inteira.', 'erro')
    busca = request.args.get('q', '').strip()
    with conectar() as con:
        lista = con.execute('''SELECT * FROM livro WHERE titulo ILIKE %s
            OR autor ILIKE %s OR categoria ILIKE %s ORDER BY titulo''',
            tuple(['%' + busca + '%'] * 3)).fetchall()
        editar = None
        codigo = request.args.get('editar', type=int)
        if codigo:
            editar = con.execute('SELECT * FROM livro WHERE id_livro=%s', (codigo,)).fetchone()
            if not editar:
                abort(404)
    # Conserva o que foi digitado quando uma validação falha.
    if request.method == 'POST':
        editar = dict(request.form)
    return render_template('livros.html', livros=lista, editar=editar, busca=busca)


@app.post('/livros/<int:codigo>/excluir')
@login_obrigatorio
def excluir_livro(codigo):
    try:
        with conectar() as con:
            resultado = con.execute('DELETE FROM livro WHERE id_livro=%s', (codigo,))
            if resultado.rowcount == 0:
                abort(404)
        flash('Livro excluído.', 'sucesso')
    except psycopg.errors.ForeignKeyViolation:
        flash('Este livro tem empréstimos no histórico e não pode ser excluído.', 'erro')
    return redirect(url_for('livros'))


@app.route('/usuarios', methods=['GET', 'POST'])
@login_obrigatorio
def usuarios():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        if not nome or not email or not senha:
            flash('Preencha todos os campos.', 'erro')
        elif len(nome) > 100 or len(email) > 150 or '@' not in email or '.' not in email.split('@')[-1]:
            flash('Confira o nome e o e-mail informado.', 'erro')
        elif len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'erro')
        else:
            try:
                with conectar() as con:
                    con.execute('INSERT INTO usuario (nome,email,senha) VALUES (%s,%s,%s)',
                                (nome, email, generate_password_hash(senha, method='pbkdf2:sha256')))
                flash('Usuário cadastrado.', 'sucesso')
                return redirect(url_for('usuarios'))
            except psycopg.errors.UniqueViolation:
                flash('Este e-mail já está cadastrado.', 'erro')
    with conectar() as con:
        lista = con.execute('SELECT id_usuario, nome, email FROM usuario ORDER BY nome').fetchall()
    return render_template('usuarios.html', usuarios=lista)


@app.route('/emprestimos', methods=['GET', 'POST'])
@login_obrigatorio
def emprestimos():
    if request.method == 'POST':
        try:
            usuario = int(request.form.get('id_usuario', ''))
            livro = int(request.form.get('id_livro', ''))
            emprestada = date.fromisoformat(request.form.get('data_emprestimo', ''))
            prevista = date.fromisoformat(request.form.get('data_prevista', ''))
            if prevista < emprestada:
                raise ValueError('A devolução prevista não pode ser anterior ao empréstimo.')
            if emprestada > date.today():
                raise ValueError('A data do empréstimo não pode estar no futuro.')
            with conectar() as con:
                # O bloqueio da linha evita que duas pessoas peguem o último exemplar.
                escolhido = con.execute('SELECT * FROM livro WHERE id_livro=%s FOR UPDATE',
                                        (livro,)).fetchone()
                if not escolhido:
                    raise ValueError('Livro não encontrado.')
                if escolhido['quantidade'] <= 0:
                    raise ValueError('Este livro está sem estoque disponível.')
                if not con.execute('SELECT 1 FROM usuario WHERE id_usuario=%s', (usuario,)).fetchone():
                    raise ValueError('Usuário não encontrado.')
                con.execute('''INSERT INTO emprestimo
                    (data_emprestimo, data_prevista, id_usuario, id_livro)
                    VALUES (%s,%s,%s,%s)''', (emprestada, prevista, usuario, livro))
                con.execute('UPDATE livro SET quantidade=quantidade-1 WHERE id_livro=%s', (livro,))
            flash('Empréstimo registrado.', 'sucesso')
            return redirect(url_for('emprestimos'))
        except ValueError as erro:
            mensagem = str(erro)
            if mensagem.startswith(('invalid literal', 'Invalid isoformat')):
                mensagem = 'Preencha usuário, livro e datas válidas.'
            flash(mensagem, 'erro')
    filtro = request.args.get('status', 'todos')
    where = {'ativos': 'WHERE e.data_devolucao IS NULL',
             'devolvidos': 'WHERE e.data_devolucao IS NOT NULL',
             'atrasados': 'WHERE e.data_devolucao IS NULL AND e.data_prevista < CURRENT_DATE'}.get(filtro, '')
    with conectar() as con:
        lista = con.execute('''SELECT e.*, u.nome, l.titulo FROM emprestimo e
            JOIN usuario u USING(id_usuario) JOIN livro l USING(id_livro) ''' + where +
            ' ORDER BY e.id_emprestimo DESC').fetchall()
        pessoas = con.execute('SELECT id_usuario,nome FROM usuario ORDER BY nome').fetchall()
        acervo = con.execute('SELECT id_livro,titulo,quantidade FROM livro ORDER BY titulo').fetchall()
    return render_template('emprestimos.html', emprestimos=lista, usuarios=pessoas,
                           livros=acervo, hoje=date.today(), filtro=filtro)


@app.post('/emprestimos/<int:codigo>/devolver')
@login_obrigatorio
def devolver(codigo):
    with conectar() as con:
        registro = con.execute('SELECT * FROM emprestimo WHERE id_emprestimo=%s FOR UPDATE',
                               (codigo,)).fetchone()
        if not registro:
            abort(404)
        if registro['data_devolucao']:
            flash('Este empréstimo já foi devolvido.', 'erro')
        else:
            con.execute('UPDATE emprestimo SET data_devolucao=CURRENT_DATE WHERE id_emprestimo=%s', (codigo,))
            con.execute('UPDATE livro SET quantidade=quantidade+1 WHERE id_livro=%s', (registro['id_livro'],))
            flash('Devolução registrada. Estoque atualizado.', 'sucesso')
    return redirect(url_for('emprestimos'))


@app.get('/relatorios')
@login_obrigatorio
def relatorios():
    with conectar() as con:
        ranking = con.execute('''SELECT l.titulo, l.autor, COUNT(e.id_emprestimo) AS total
            FROM livro l LEFT JOIN emprestimo e USING(id_livro)
            GROUP BY l.id_livro ORDER BY total DESC, l.titulo''').fetchall()
        historico = con.execute('''SELECT u.nome,l.titulo,e.data_emprestimo,e.data_prevista,e.data_devolucao
            FROM emprestimo e JOIN usuario u USING(id_usuario)
            JOIN livro l USING(id_livro) ORDER BY e.id_emprestimo DESC''').fetchall()
    if request.args.get('formato') == 'csv':
        arquivo = io.StringIO()
        escritor = csv.writer(arquivo, delimiter=';')
        escritor.writerow(['Livro', 'Autor', 'Total de empréstimos'])
        for linha in ranking:
            # Planilhas não devem interpretar títulos digitados como fórmulas.
            valores = [linha['titulo'], linha['autor'], linha['total']]
            escritor.writerow(["'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v
                               for v in valores])
        return Response('\ufeff' + arquivo.getvalue(), mimetype='text/csv; charset=utf-8',
                        headers={'Content-Disposition': 'attachment; filename=livros-mais-emprestados.csv'})
    return render_template('relatorios.html', ranking=ranking, historico=historico)


@app.template_filter('data_br')
def data_br(valor):
    return valor.strftime('%d/%m/%Y') if valor else '-'


@app.errorhandler(400)
@app.errorhandler(404)
def erro_requisicao(erro):
    return render_template('erro.html', codigo=erro.code, mensagem=erro.description), erro.code


@app.errorhandler(psycopg.Error)
def erro_banco(erro):
    app.logger.exception('Falha na operação do banco de dados')
    return render_template('erro.html', codigo=503,
        mensagem='Não foi possível concluir a operação. Confira a conexão com o banco e tente novamente.'), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
