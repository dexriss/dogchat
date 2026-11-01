
#import hashlib
import os
import json
import itertools
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed

from flask import Flask, render_template, redirect, url_for, request,jsonify, session as sess_fl,flash,send_from_directory,abort
from flask import current_app
from sqlalchemy import create_engine,insert,or_
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from app.models import Base, Users, Pets, Posts,Volonteers,Profies,Chat,Pedigree
from flask_login import LoginManager, UserMixin, login_required,current_user, login_user,logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
#from app.form import RegistrationForm, patch_request_class

from config import DevelopmentConfig,RootPath
#struct



basedir = os.path.abspath(os.path.dirname(__file__))

engine = create_engine('sqlite:///app/database.db', echo=True)
Base.metadata.bind = engine
Base.metadata.create_all(engine)  # создаст недостающие таблицы (в т.ч. pedigree)

DBSession = sessionmaker(bind=engine)
sess_SA = DBSession()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(DevelopmentConfig)
app.secret_key = '1234456789' #'123456789'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

base_data = {}

# Определение класса пользователя
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(id):
  return sess_SA.get(Users, int(id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        print(username.data)
        user = sess_SA.query(Users).filter(Users.login == username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # def validate_email(self, email):
    #     user = db.session.scalar(sa.select(User).where(
    #         User.email == email.data))
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(form.username.data)
        user = Users(login=form.username.data,password = generate_password_hash(form.password.data))#, email=form.email.data 
       
        print(user.login,user.password,'pass')
        sess_SA.add(user) #execute(insert(Users),user)
        sess_SA.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Register', form=form)


app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # в форме питомца до 30 фото предков
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir,'static','uploads') 

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
# максимальный размер файла, по умолчанию 16MB
# patch_request_class(app) 

class UploadForm(FlaskForm):
    file = FileField('Select File', validators=[DataRequired()])  # File input
    submit = SubmitField('Upload')  # Optional submit button (we'll use AJAX instead)
    # photo = FileField(validators=[FileAllowed(photos, 'Image only!'), 
    #                   FileRequired('File was empty!')])
    # submit = SubmitField('Upload')
    
@app.route('/upload/<type>/<id>', methods=['GET', 'POST'])
def upload_file(type,id):
    print('begin',type,id)    
    form = UploadForm()
    # print('form.photo.data', form.validate_on_submit(),type,id)
    if request.method == 'POST': 
        if form.validate_on_submit():
            file = form.file.data  # Get the uploaded file
            filename = secure_filename(file.filename)  # Sanitize filename (prevents path traversal)
            user_img_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],str(current_user.login))
            if not os.path.isdir(user_img_dir):
                os.makedirs(user_img_dir)
            file.save(os.path.join(user_img_dir, filename))  # Save the file to UPLOAD_FOLDER
            if type == 'user':
                edit_val = sess_SA.query(Users).filter_by(id=id).one()
            elif type == 'pets':
                edit_val = sess_SA.query(Pets).filter_by(id=id).one()
            elif type == 'posts':
                edit_val = sess_SA.query(Posts).filter_by(id=id).one()
            elif type == 'profies':
                edit_val = sess_SA.query(Profies).filter_by(id=id).one()
                
            
            setattr(edit_val, 'image', filename)
            print('upload_file',edit_val.image)
            sess_SA.commit()            
            return jsonify({'success': True, 'filename': filename})
        else:
            # Return validation errors (including CSRF errors)
            return jsonify({'success': False, 'error': form.errors}), 400
    return render_template('upload.html', form=form,type = type,id=id)



@app.route('/')
def index():
    if 'link_to' not in sess_fl:
        sess_fl['link_to'] = ''
    
    user_id = current_user.id if current_user.is_authenticated else 0
    print('current_user',user_id)
    return render_template("aboutus.html", data = {"current_user_id":user_id,"s":user_id,"l":sess_fl['link_to'],"title":'main',"file_css":'fruk.css'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        user = sess_SA.scalar(sa.select(Users).where(Users.login == username))
        #user = sess_SA.query(Users).filter(Users.login == username).one()#sess_SA.query(Users).filter_by(Users.login == username).one()
        print(username,password,user.birth)
        print(user.login, user.name,user.password,check_password_hash(user.password, password))
        if user and check_password_hash(user.password, password):
            print(user)
            #load_user(user.id)
            login_user(user)
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():

    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.id:
        # output = {}
        # output['user']
        
        user = sess_SA.query(Users).filter(Users.id == current_user.id).one()
        if user:
            userdata = {}
            for key in Users.__table__.columns.keys():
                #print(key)
                if key != 'password':
                    userdata[key] = getattr(user, key)
        #достаём собак
            pets = sess_SA.query(Pets).filter(Pets.user_id == current_user.id).all()
           # print(Pets.__table__.columns.keys())
           # print(pets)
            userdata['dogs'] = []
            for dog in pets:
                dog_row = {}
                for key in Pets.__table__.columns.keys():
                    dog_row[key] = getattr(dog, key)
                userdata['dogs'].append(dog_row)
            #    print(dog_row)
            # userdata["dogs"] = [
            #         {"dogname":"Тилл","breed":"Ретвиер","dogage": 4,"cas":"не кастрирован","dogdescript":"Активный, любвеобильный песик, обожает гулять"},
            #     ]
            userdata["images"] = ["/static/img/5a56aad338b286407a28789e4309bc6a.jpg"]
        #волонтёр
            userdata['volonteers'] = {}
            volonteers = sess_SA.query(Volonteers).filter(Volonteers.user_id == current_user.id).first()
            if volonteers is not None:
                for key in Volonteers.__table__.columns.keys():
                    userdata['volonteers'][key] = getattr(volonteers, key)
            #print('volonteer',userdata['volonteers'],volonteers)
        #посты
            userdata['posts'] = []
            posts = sess_SA.query(Posts).filter(Posts.user_id == current_user.id).all()
            # print(Posts.__table__.columns.keys())
            # print(posts)
            if posts is not None:
                for post in posts:
                    post_row = {}
                    for key in Posts.__table__.columns.keys():
                        post_row[key] = getattr(post, key)
                    userdata['posts'].append(post_row)
        #услуги        
            userdata['profies'] = []
            profies = sess_SA.query(Profies).filter(Profies.user_id == current_user.id).all()
            # print(Profies.__table__.columns.keys())
            # print(profies)
            if profies is not None:
                for profy in profies:
                    profy_row = {}
                    for key in Profies.__table__.columns.keys():
                        profy_row[key] = getattr(profy, key)
                    userdata['profies'].append(profy_row)
        data = {}
        data['userdata'] = userdata
        data["title"] = 'Профиль'
        data["file_css"] = 'fruk.css'      
        return render_template("profile.html", data=data)
    sess_fl['link_to'] = 'profile'
    return redirect(url_for('login'))

# ---------- родословная ----------
# ключ = путь от питомца: f - отец, m - мать (f, m, ff, fm, ... до 4 символов)
PED_KEYS = [''.join(p) for n in range(1, 5) for p in itertools.product('fm', repeat=n)]
PED_EXT = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def _ped_remove_file(rel):
    if rel:
        try:
            os.remove(os.path.join(app.static_folder, rel))
        except OSError:
            pass

def save_pedigree(pet, form, files):
    """Сохраняет родословную питомца из полей ped_name_*, ped_breed_*,
    ped_photo_* и ped_delphoto_*. Вызывать до sess_SA.commit()."""
    if not any(k.startswith('ped_') for k in form):
        return  # форма пришла без блока родословной - ничего не трогаем
    login = pet.users.login if pet.users else str(pet.user_id)
    existing = {p.position: p for p in pet.pedigree_items}
    for k in PED_KEYS:
        name = form.get('ped_name_' + k, '').strip()[:100]
        breed = form.get('ped_breed_' + k, '').strip()[:100]
        row = existing.get(k)
        photo = row.image if row else None

        if form.get('ped_delphoto_' + k) == '1':
            _ped_remove_file(photo)
            photo = None

        f = files.get('ped_photo_' + k)
        if f and f.filename:
            ext = os.path.splitext(f.filename)[1].lower().lstrip('.')
            if ext in PED_EXT:
                rel = 'uploads/%s/pedigree/%s_%s_%s.%s' % (login, pet.id, k, uuid.uuid4().hex[:8], ext)
                full = os.path.join(app.static_folder, rel)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                f.save(full)
                _ped_remove_file(photo)
                photo = rel

        if name or breed or photo:
            if row is None:
                row = Pedigree(pet_id=pet.id, position=k)
                sess_SA.add(row)
            row.name, row.breed, row.image = name, breed, photo
        elif row is not None:
            sess_SA.delete(row)

@app.route("/edit/<int:id>/<type>/", methods=['GET', 'POST'])
def editItem(id, type):
           
    if type == 'user':
        edit_val = sess_SA.query(Users).filter_by(id=id).one()
    elif type == 'pets':
        edit_val = sess_SA.query(Pets).filter_by(id=id).one()
    elif type == 'posts':
        edit_val = sess_SA.query(Posts).filter_by(id=id).one()
    elif type == 'profies':
        edit_val = sess_SA.query(Profies).filter_by(id=id).one()
    elif type == 'volonteer':
        edit_val = sess_SA.query(Volonteers).filter_by(id=id).one() 
        # print('edit_val',edit_val.why_i,edit_val.i_can)
    if request.method == 'POST':
        if request.form:
            #edit_val.title = request.form['title']
            for key,value in request.form.items():                
                # print(key,'value',value)
                if key.startswith('ped_'):
                    continue  # поля родословной обрабатывает save_pedigree
                if type == 'profies' and key == 'why_i' and value not in SERVICE_TITLES and value != edit_val.why_i:
                    return jsonify(status='error', message='Выберите услугу из списка'), 400
                if key == 'neutered': 
                    # print('neutered',value)                    
                    setattr(edit_val, key, True if value=='True' else False)
                else:
                    setattr(edit_val, key, value)
            #    edit_val[key] = value #request.form['name']
            if type == 'pets':
                save_pedigree(edit_val, request.form, request.files)
            sess_SA.commit()
            return jsonify(status='ok') #redirect(url_for('showBooks'))
    #else:
    return render_template('editForm.html', edit_val=edit_val,type = type)

@app.route('/pedigree/<int:pet_id>')
@login_required
def pedigree_view(pet_id):
    pet = sess_SA.get(Pets, pet_id)
    if pet is None:
        abort(404)
    return render_template('pedigreeView.html', pet=pet)

@app.route('/new/<type>', methods=['GET', 'POST'])
def newItem(type):
    if request.method == 'POST':
        new_item = {}
        new_item['user_id'] = current_user.id
        for key,value in request.form.items():                
            # print(key,'value',value)
            if key.startswith('ped_'):
                continue  # поля родословной - отдельно, после создания питомца
            if value == 'True' or value == 'False':                     
                new_item[key] = True if value=='True' else False
            else:
                new_item[key] = value
        # print('value',new_item,type)
        if type == 'profies' and new_item.get('why_i') not in SERVICE_TITLES:
            return jsonify(status='error', message='Выберите услугу из списка'), 400

        if type == 'pets':
            res = sess_SA.execute(insert(Pets).values(**new_item))
            new_pet = sess_SA.get(Pets, res.inserted_primary_key[0])
            save_pedigree(new_pet, request.form, request.files)
        elif type == 'volonteer':
            sess_SA.execute(insert(Volonteers),[new_item])
        elif type == 'posts':
            sess_SA.execute(insert(Posts),[new_item])
        elif type == 'profies':
            sess_SA.execute(insert(Profies),[new_item])
        sess_SA.commit()
        return jsonify(status='ok') #redirect(url_for('showBooks'))
    else:
        edit_val = {}
        edit_val['id'] = -1
        return render_template('editForm.html', edit_val =edit_val,type =type)



@app.route('/send_message/<id_to>', methods=['GET', 'POST'])
@login_required
def send_message(id_to):
    if request.method == 'POST':
        print('request',request.data,current_user.id)
        newMessage = {}
        newMessage['id_from'] = current_user.id
        newMessage['id_to'] = id_to
        newMessage['message'] = json.loads(request.data)['message']
        sess_SA.execute(insert(Chat),[newMessage])
        print('request',request.data,newMessage)
        sess_SA.commit()
        return jsonify(status='ok',id_from = current_user.id,id_to = id_to,message = newMessage['message'])




    
@app.route('/volunteer')
@login_required
def volunteer():
    data = {"current_user_id":current_user.id if current_user.is_authenticated else 0,"file_css":'fruk.css',"title":'Волонтёры',"volonteers":[]}
    
    volonteers = sess_SA.query(Volonteers).all()
    for volonteer in volonteers:
        volonteer_row = {}
        for key in Volonteers.__table__.columns.keys():
            volonteer_row[key] = getattr(volonteer, key)
        userdata = sess_SA.query(Users).filter(Users.id == volonteer.user_id).first()
        volonteer_row["name"] = getattr(userdata, "name")
        volonteer_row["city"] = getattr(userdata, "city")
        volonteer_row["image"] = getattr(userdata, "image")
        volonteer_row["login"] = getattr(userdata, "login")
        
        data['volonteers'].append(volonteer_row)
        print('volonteer',len(data['volonteers']))
    return render_template("volunteer.html",data=data)

@app.route('/lenta')
@login_required
def post():
    data = {"current_user_id":current_user.id if current_user.is_authenticated else 0,"file_css":'fruk.css',"title":'Лента',"lenta":[]}
    

    
    lenta = sess_SA.query(Posts).all()
    for post in lenta:
        post_row = {}
        for key in Posts.__table__.columns.keys():
            post_row[key] = getattr(post, key)
        userdata = sess_SA.query(Users).filter(Users.id == post.user_id).first()
        post_row["name"] = getattr(userdata, "name")
        
        post_row["login"] = getattr(userdata, "login")
        print("name",post_row["name"])
        data['lenta'].append(post_row)
    return render_template("lenta.html",data=data)

@app.route('/meetings')
@login_required
def meetings():
    data = {"current_user_id":current_user.id if current_user.is_authenticated else 0,"file_css":'fruk.css',"title":'Знакомства',"meeting":[]}
    
    meeting = sess_SA.query(Users).all()
    for user in meeting:
        user_row = {}
        for key in Users.__table__.columns.keys():
            user_row[key] = getattr(user, key)
        userdata = sess_SA.query(Pets).filter(Pets.user_id == user.id).all()
        user_row["pets"]=[]
        for pet in userdata:
            pet_row={}

            pet_row["id"] = pet.id
            pet_row["has_pedigree"] = bool(pet.pedigree_items)
            pet_row["nickname"] = getattr(pet, "nikname")
            pet_row["age"] = getattr(pet, "age")
            pet_row["breed"] = getattr(pet, "breed")
            pet_row["neutered"] = getattr(pet, "neutered")
            pet_row["about"] = getattr(pet, "about")
            user_row["pets"].append(pet_row)
        data['meeting'].append(user_row)
    return render_template("znakomitsa.html",data=data)

@app.route('/chat/<id_chat>', methods=['GET'])
def get_messages(id_chat):
    print('get_messages',current_user.is_authenticated,current_user.id,id_chat)
    chats = sess_SA.query(Chat).filter(or_(Chat.id_from == current_user.id,Chat.id_to == current_user.id)).all()
    chat = {}
    print(len(chats))
    for mess in chats:
        current_opp = -1
        if mess.id_from == current_user.id:
            current_opp = mess.id_to            
            
        else:
            current_opp = mess.id_from 
        if int(current_opp) != current_user.id and current_opp not in chat.keys():
                chat[current_opp] = []
        mess_row = {}
        print('current_opp',current_opp,len(chat.keys()))
        for key in Chat.__table__.columns.keys():
            print(key,getattr(mess, key))
            mess_row[key] = getattr(mess, key)
        chat[current_opp].append(mess_row)
    print('chat len',len(chat.keys()),int(id_chat) != current_user.id,int(id_chat) not in chat.keys())
    if int(id_chat) != current_user.id and int(id_chat) not in chat.keys():
        chat[id_chat] = []
    print('chat len',len(chat.keys()))
    chat_num = 1
    if int(id_chat) == current_user.id:
        chat_num = len(chat.keys())
    else:
        for key in chat.keys(): 
            if int(key) == int(id_chat):
                break
            else:
                chat_num +=1
            print('key chat__',key,id_chat,chat_num, current_user.id,int(id_chat) != current_user.id) 
    print('chat len',len(chat.keys()),chat_num)
    return render_template('chat.html', chat = chat,chat_num = chat_num, current_chat = id_chat, current_user = current_user.id)

@app.route('/services')
@login_required
def services():
    data = {"current_user_id":current_user.id if current_user.is_authenticated else 0,"file_css":'fruk.css',"title":'Услуги',"lenta":[]}
    return render_template('uslugi.html', data=data)

# Типы услуг: один список на всё - выпадающий список в editForm.html,
# страница /services (uslugi.html) и фильтр на страницах /services/<slug>.
# В Profies.why_i хранится title выбранной услуги.
SERVICES = [
    {'slug': 'veterenar',     'title': 'Ветеринары',            'image': 'img/6758ad96d7c6f578075113.jpg'},
    {'slug': 'kinolog',       'title': 'Кинологи',              'image': 'img/depositphotos_768735950-stock-photo-pretty-young-woman-treat-training.jpg'},
    {'slug': 'grumer',        'title': 'Грумеры',               'image': 'img/blg-amazonian-trek-1024x682.jpg'},
    {'slug': 'vystavki',      'title': 'Организаторы выставок', 'image': 'img/азавак.jpg'},
    {'slug': 'zoopsiholog',   'title': 'Зоопсихолог',           'image': 'img/400101700389_368776.jpg'},
    {'slug': 'kanisterapevt', 'title': 'Канистерапевт',         'image': 'img/images.jpeg'},
]
SERVICES_BY_SLUG = {x['slug']: x for x in SERVICES}
SERVICE_TITLES = [x['title'] for x in SERVICES]

@app.context_processor
def inject_service_types():
    # доступно во всех шаблонах как service_types
    return {'service_types': SERVICES}

@app.route('/services/<slug>')
@login_required
def service_list(slug):
    service = SERVICES_BY_SLUG.get(slug)
    if service is None:
        abort(404)
    data = {"current_user_id": current_user.id, "file_css": 'fruk.css',
            "title": service['title'], "service": service, "profies": []}
    profies = sess_SA.query(Profies).filter(Profies.why_i == service['title']).all()
    for profi in profies:
        userdata = sess_SA.query(Users).filter(Users.id == profi.user_id).first()
        if userdata is None:
            continue
        profi_row = {}
        for key in Profies.__table__.columns.keys():
            profi_row[key] = getattr(profi, key)
        profi_row["name"] = userdata.name
        profi_row["city"] = userdata.city
        profi_row["login"] = userdata.login
        data['profies'].append(profi_row)
    return render_template("service_list.html", data=data)

@app.route('/services/veterenar')
@login_required
def veterenar():
    # старый адрес и endpoint сохранены (на них могут ссылаться другие шаблоны)
    return service_list('veterenar')
