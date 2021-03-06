from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import argon2
from SQLRequest import SQLRequest
from rep_server import get_response
from time import sleep
from multiprocessing import Process

app = Flask(__name__)
app.config.from_object("secret_config")
app.secret_key = app.config['SECRET_KEY']
sql_obj = SQLRequest(app)


@app.route('/')
def index():
    sites = sql_obj.get_sites_group_by_id()
    return render_template('index.html', sites=sites)


@app.route('/site/<int:id_site>')
def one_site(id_site):
    all_request = sql_obj.get_request_where_id(id_site)
    return render_template('one_site.html', all_request=all_request)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form:
        username = request.form['username']
        password = request.form['password']

        try:
            true_password = sql_obj.get_user_password(username)
        except TypeError:
            flash('Error: Wrong username')
        else:
            if argon2.verify(password, true_password):
                session['is_login'] = True
                flash('You were successfully logged in')
                return redirect(url_for('admin'))
            else:
                flash('Error: Wrong password')

    if session.get('is_login'):
        return redirect(url_for('admin'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session['is_login'] = False
    flash('You were successfully log out')
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    check_login()
    sites = sql_obj.get_all_data_site()
    return render_template('admin/admin.html', sites=sites)


@app.route('/admin/newSite', methods=['GET', 'POST'])
def new_site():
    check_login()
    if request.form:
        url = request.form['url']
        sql_obj.new_site(url)
        flash('New site is create just wait 2 min')
        return redirect(url_for('admin'))

    return render_template('admin/new_site.html')


@app.route('/admin/site/<int:id_site>/change', methods=['GET', 'POST'])
def edit_site(id_site):
    check_login()
    site = sql_obj.get_url_where(id_site)

    if request.form:
        url = request.form['url']
        sql_obj.update_site(url, id_site)
        return redirect(url_for('admin'))

    return render_template('admin/edit_site.html', site=site)


@app.route('/admin/site/<int:id_site>/delete')
def delete_site(id_site):
    check_login()
    flash('Site id: {} has been delete'.format(id_site))
    sql_obj.delete_site(id_site)
    return redirect(url_for("admin"))


def check_login():
    if not session.get('is_login'):
        flash('Error: Login first')
        return redirect(url_for('login'))


def status():
    while True:
        sleep(120)
        print("===============================")
        dict_response = get_response(sql_obj.get_all_data_site())
        for key, value in dict_response.items():
            sql_obj.new_response(value, key)


p = Process(target=status)
p.start()

if __name__ == '__main__':
    app.run()
