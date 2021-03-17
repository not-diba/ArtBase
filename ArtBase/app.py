from flask import Flask,render_template, flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

from functools import wraps
from classes.forms import *
from stuff import stuff

app = Flask(__name__)
app.secret_key = 'my unobvious secret key'

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'newuser'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'ArtBase'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)


#Index
@app.route('/')
def index():
    return render_template('home.html')

#About
@app.route('/about')
def about():
    return render_template('about.html')


#Admin Register
@app.route('/admin_register',methods=['GET','POST'])
def admin_register():
    #passing in the form class that was created
    form = AdminRegister(request.form)
    if request.method == 'POST' and form.validate():

        stuff.admin_register(form)
        return redirect(url_for('admin_login'))

    #form = form passes in the form = RegisterForm from top
    return render_template('/admin/admin_register.html', form=form)


#AdminLogin
@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        #get Form fields
        admin_name = request.form['admin_name']
        password_candidate = request.form['password']

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get user by user_name
        result = cur.execute("SELECT * FROM admins WHERE admin_name = %s", [admin_name])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #Compare the Passwords
            if sha256_crypt.verify(password_candidate,password):
                app.logger.info('PASSWORD MATCHED')
                #Passed
                #creating session variables
                session['admin_logged_in'] = True
                session['admin_name'] = admin_name

                flash('You are now logged in','success')
                return redirect(url_for('admin_dashboard'))

            else:
                error = 'Invalid login'
                return render_template('/admin/admin_login.html',error=error)
            #Close connection
            cur.close()
        else:
            app.logger.info('No User')
            error = 'Invalid login'
            return render_template('/admin/admin_login.html',error=error)

    return render_template('/admin/admin_login.html')




#User Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #get Form fields
        user_name = request.form['user_name']
        password_candidate = request.form['password']

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get user by user_name
        result = cur.execute("SELECT * FROM users WHERE user_name = %s", [user_name])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #Compare the Passwords
            if sha256_crypt.verify(password_candidate,password):
                app.logger.info('PASSWORD MATCHED')
                #Passed
                #creating session variables
                session['logged_in'] = True
                session['user_name'] = user_name

                flash('You are now logged in','success')
                return redirect(url_for('users_dashboard'))

            else:
                error = 'Invalid login'
                return render_template('/users/login.html',error=error)
            #Close connection
            cur.close()
        else:
            app.logger.info('No User')
            error = 'Invalid login'
            return render_template('/users/login.html',error=error)

    return render_template('/users/login.html')


#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login','danger')
            return redirect(url_for('login'))
    return wrap

#Check if admin logged in
def is_adminlog_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login','danger')
            return redirect(url_for('admin_login'))
    return wrap

#Delete User
@app.route('/delete_user/<string:id>', methods = ['POST'])
@is_adminlog_in
def delete_user(id):
    stuff.delete_user(id)

    return redirect(url_for('admin_dashboard'))

#Register
@app.route('/register',methods=['GET','POST'])
def register():
    #passing in the form class that was created
    form = RegisterUser(request.form)
    if request.method == 'POST' and form.validate():

        stuff.user_register(form)
        return redirect(url_for('login'))
    #form = form passes in the form = RegisterForm from top
    return render_template('/users/register.html', form=form)


#LogOut
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out','success')
    return render_template('home.html')


#UsersDashboard
@app.route('/users_dashboard')
@is_logged_in
def users_dashboard():
    galleries = stuff.galleries()
    artists = stuff.artists()
    art_works = stuff.art_works()
    art_groups = stuff.art_groups()
    users = stuff.users()
    return render_template('/users/users_dashboard.html',galleries=galleries,artists=artists,art_works=art_works,art_groups=art_groups,users=users)



@app.route('/admin_dashboard')
@is_adminlog_in
def admin_dashboard():
    galleries = stuff.galleries()
    artists = stuff.artists()
    art_works = stuff.art_works()
    art_groups = stuff.art_groups()
    users = stuff.users()
    return render_template('/admin/admin_dashboard.html',galleries=galleries,artists=artists,art_works=art_works,art_groups=art_groups,users=users)

#add_gallery
@app.route('/add_gallery',methods=['GET','POST'])
@is_adminlog_in
def add_gallery():
    form = GalleryForm(request.form)

    if request.method == 'POST' and form.validate():
        stuff.add_gallery(form)
        return redirect(url_for('admin_dashboard'))

    return render_template('/gallery/add_gallery.html',form=form)

#Delete Gallery
@app.route('/delete_gallery/<string:id>', methods = ['POST'])
@is_adminlog_in
def delete_gallery(id):
    stuff.delete_gallery(id)

    return redirect(url_for('admin_dashboard'))



#add_artist
@app.route('/add_artist',methods=['GET','POST'])
@is_adminlog_in
def add_artist():
    form = ArtistForm(request.form)

    if request.method == 'POST' and form.validate():
        stuff.add_artist(form)
        return redirect(url_for('admin_dashboard'))

    return render_template('/artists/add_artist.html',form=form)

#Delete Artist
@app.route('/delete_artist/<string:id>', methods = ['POST'])
@is_adminlog_in
def delete_artist(id):
    stuff.delete_artist(id)

    return redirect(url_for('admin_dashboard'))



#add_artworks
@app.route('/add_artworks',methods=['GET','POST'])
@is_adminlog_in
def add_artworks():
    form = Art_WorksForm(request.form)

    if request.method == 'POST' and form.validate():
        stuff.add_artworks(form)
        return redirect(url_for('admin_dashboard'))

    return render_template('/art_works/add_artworks.html',form=form)

#Delete ArtWork
@app.route('/delete_art_works/<string:id>', methods = ['POST'])
@is_adminlog_in
def delete_art_works(id):
    stuff.delete_art_works(id)

    return redirect(url_for('admin_dashboard'))



#add_art Groups
@app.route('/add_artgroups',methods=['GET','POST'])
@is_adminlog_in
def add_artgroups():
    form = Art_GroupsForm(request.form)

    if request.method == 'POST' and form.validate():
        stuff.add_artgroups(form)
        return redirect(url_for('admin_dashboard'))

    return render_template('/art_groups/add_artgroups.html',form=form)

#Delete Art Groups
@app.route('/delete_art_groups/<string:id>', methods = ['POST'])
@is_adminlog_in
def delete_art_groups(id):
    stuff.delete_art_groups(id)

    return redirect(url_for('admin_dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
