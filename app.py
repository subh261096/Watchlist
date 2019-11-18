from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify
from wtforms import Form, TextField, PasswordField, validators
from pymysql import escape_string as thwart
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from functools import wraps, partial
from sqlalchemy import DateTime
from datetime import timedelta
import datetime
import tmdb

app = Flask(__name__)




######################################### CONFIGRATION OF DATABSE ######################################
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nqlbjswtrhxigf:14771962fe16519adf61d5512a0523f6f41129ac2781c48ade4397495093cde2@ec2-54-204-35-248.compute-1.amazonaws.com:5432/dav5jvlvn91k2g'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'subh261096'
db = SQLAlchemy(app)

#########################################     END     #############################################





######################################### DATABSE TABLES ################################################


                  ########################## USER TABLE ######################
class UserData(db.Model):
    __tablename__ = 'UserData'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30))
    Password = db.Column(db.String(500))
    RegisterDate = db.Column(DateTime, default=datetime.datetime.utcnow)
                    ########################### END #########################


                    ######################### USER LIST ###################
class UserList(db.Model):
    __tablename__ = 'UserList'
    UserId = db.Column(db.Integer, primary_key=True)
    ListName=db.Column(db.String(50),primary_key=True)
    LastModifiedDate = db.Column(DateTime, default=datetime.datetime.utcnow)
                    ############################### END ##########################

class UserMovie(db.Model):
    __tablename__ = 'UserMovie'
    List = db.Column(db.String(50),primary_key=True)
    MovieId=db.Column(db.String(30),primary_key=True)
    MovieName = db.Column(db.String(30))
    PosterUrl = db.Column(db.String(80))
    LastModifiedDate = db.Column(DateTime, default=datetime.datetime.utcnow)    

############################################## END ######################################################







######################################### REGISTRATION FORM #########################################
class RegistrationForm(Form):
    '''Child of a WTForm Form object...'''
    username = TextField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm',
                                                             message="Passwords must match")])
    confirm = PasswordField('Confirm Password')
######################################### END #############################################








######################################### VERIFY LOGIN #############################################
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UnAuthorised!, Please Login First!', 'danger')
            return redirect(url_for('home'))
            ##important indentation
    return wrap
######################################### END #######################################################


def already_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash('Already Logged In!', 'danger')
            return redirect(url_for('home'))
            ##important indentation
    return wrap





######################################### HOME #######################################################
@app.route('/')
@app.route('/home')
def home():
    top_movies = tmdb.get_trending(timeframe='day')
    return render_template("home.html", top_movies=top_movies)

######################################### END ########################################################







######################################### SIGN UP #####################################################
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    session.pop('_flashes', None)
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():  # if the form info is valid
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))
        data_model = UserData(Name=username, Password=password)
        save_to_database = db.session
        if(UserData.query.filter_by(Name=username).count() == 0):
            try:
                save_to_database.add(data_model)
                save_to_database.commit()
                uid = UserData.query.filter_by(Name=username).first().Id
                flash('Registered Successfully!','success')
                return redirect(url_for('login'))
            except:
                save_to_database.rollback()
                save_to_database.flush()
                flash("can't Register Now!, please try again Later..")
            return render_template('signup.html', form=form)
        else:
            flash("User Already Exists! Please Enter Unique username!")
            return render_template('signup.html', form=form)
    if request.method == "POST" and form.validate() == False:  # if form info is invalid
        flash('Invalid password, please try again')
        return render_template('signup.html', form=form)
    return render_template("signup.html")
######################################### END #########################################################







######################################### LOG IN ######################################################
@app.route('/login', methods=['GET', 'POST'])
@already_logged_in
def login():
    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']

        if (UserData.query.filter_by(Name=attempted_username).count()) == 0:
            flash("Username not found. Try a different username, or create an account.")
            return render_template("login.html")
        data_model = UserData.query.filter_by(Name=attempted_username).first()
        try:
            if attempted_username == data_model.Name and sha256_crypt.verify(attempted_password, data_model.Password):
                session.permanent = True
                # setting session timeout
                app.permanent_session_lifetime = timedelta(minutes=5)
                session['logged_in'] = True
                session['uid'] = data_model.Id
                session['username'] = data_model.Name
                flash("Welcome %s!" % (data_model.Name),'')
                return redirect(url_for("home"))
            else:
                flash("Incorrect password, try again")
                return render_template("login.html")
        except Exception as e:
            return str(e)
    return render_template("login.html")

######################################### END #########################################################









######################################### LOG OUT ######################################################
@app.route('/logout', methods=['GET', 'POST'])
@is_logged_in
def logout():
    session.pop('logged_in', False)
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))
######################################### END ##########################################################









######################################### POPULAR ######################################################
@app.route('/popular')
def popular():
    top_movies = tmdb.get_trending(timeframe='day')
    return render_template("popular.html", top_movies=top_movies)
######################################### END ##########################################################








# ######################################### MOVIE BY ID ###################################################
# @app.route('/movie/<string:id>')
# def watch(id):
#     movie = tmdb.get_movie(mov_id=id)
#     wishlists = UserList.query.with_entities(UserList.ListName).distinct()
#     return render_template('single_movie.html', movie=movie,wls=wishlists)
######################################### END ###########################################################




######################################### MOVIE BY GENRE ###################################################
@app.route('/movie_genre/<int:genre_id>/<string:name>')
def watch_genre(genre_id,name):

    movie = tmdb.get_genre(genre_id=genre_id)
    wishlists = UserList.query.with_entities(UserList.ListName).distinct()
    return render_template('list_by_genre.html', top_movies=movie,genre=name)
######################################### END ###########################################################




######################################### SEARCH MOVIES ##################################################
@app.route('/search', methods=['GET','POST'])
def search():
    title = request.args.get('title')
    if title == "" or None:
        results = tmdb.get_trending(timeframe='day')
        flash("No value entered. Here are some Popular movies!")
        size = len(results)
        return render_template("search.html", results=results, size=size)
    results = tmdb.search_movie('+'.join(title.split()))
    size = len(results)
    return render_template("search.html", results=results, size=size)
######################################### END #########################################################







######################################### MY LISTS ####################################################
@app.route('/me', methods=['GET', 'POST'])
@is_logged_in
def me():
    return redirect(url_for("mylists"))
######################################### END #########################################################








######################################### MY MOVIE VIEW LISTING ########################################
@app.route('/movie/<string:id>', methods=['POST','GET'])
@is_logged_in
def film_view(id):
    movie = tmdb.get_movie(id)
    list_name = request.form.get("list_name")
    wls=UserList.query.with_entities(UserList.ListName).distinct()
    if(request.method=='POST'):
        movie = tmdb.get_movie(id)
        list_name = request.form.get("list_name")
        wls=UserList.query.with_entities(UserList.ListName).distinct()
        if list_name =='' or list_name is None :
            flash("You must select a choice from your watchlists")
            return render_template("single_movie.html", movie=movie,wls=wls)
        uid = session['uid']
        if (UserMovie.query.filter_by(List=list_name,MovieId=movie['id']).count()>0):
            flash("%s is already in %s list!" % (movie['title'],list_name))
            return redirect(url_for("film_view", id=movie['id']))
        data_model = UserMovie(List=list_name, MovieId=movie['id'], PosterUrl=movie['poster_path'],MovieName=movie['title'])
        save_to_database= db.session()
        try:
            save_to_database.add(data_model)
            save_to_database.commit()
        except:
            flash("Cant't add Now !")
            return redirect(url_for("film_view", id=movie['id']))
        flash("%s added to list" % (str(movie['title'])))
        return redirect(url_for("film_view",id=int(movie['id'])))
    else:   
        return render_template("single_movie.html", movie=movie,movie_added=0,wls=wls)
######################################### END ##########################################################

 




######################################### MY LISTING ####################################################
@app.route('/mylists', methods=['GET', 'POST'])
@is_logged_in
def mylists():
    lists_info = []
    listup = UserList.query.filter_by(UserId=session['uid'])
    if(listup.count()>0): 
        for tup in listup:
            tup.LastModifiedDate = tup.LastModifiedDate.strftime("%m-%d-%y")
            lists_info.append(tup)
        return render_template("mylists.html", lists_info=lists_info)
    else:
        return render_template('new_list.html')
######################################### END ###########################################################












######################################### CREATING NEW LIST #############################################
@app.route('/new_list', methods=['GET', 'POST'])
@is_logged_in
def new_list():
    try:
        if request.method == "POST":
            wlname = request.form['wlname']
            data_model = UserList(UserId=session['uid'], ListName=thwart(wlname))
            save_to_database = db.session
            try:
                save_to_database.add(data_model)
                save_to_database.commit()
                flash('"%s" list added!' % (wlname))
                return redirect(url_for("mylists"))
            except:
                save_to_database.rollback()
                save_to_database.flush()
                flash("can't Add Now!, please try again Later..")
        return render_template("new_list.html")
    except Exception as e:
        return str(e)
######################################### END ##########################################################

@app.route('/remove/<string:l_name>/<string:mov_id>',methods=['POST'])
@is_logged_in
def remove(l_name,mov_id):
    data=UserMovie.query.filter_by(List=l_name,MovieId=mov_id).first()
    dell=db.session()
    # try:
    dell.delete(data)
    dell.commit()
    flash("Movie deleted from listing!")
    return redirect(url_for('list_view',l_name=l_name))
    # except:
    #     flash("Can't Delete right now!")
    #     return redirect(url_for('list_view', name=l_name))










######################################### VIEW LIST ITEM #############################################
@app.route('/mylists/<string:l_name>')
def list_view(l_name):
    list_mov = UserMovie.query.filter_by(List=l_name)
    count=list_mov.count()
    return render_template("list_view.html",list_movies=list_mov,size=count,name=l_name)
######################################### END ##########################################################








######################################### MAIN ##########################################################
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
######################################### END ###########################################################
