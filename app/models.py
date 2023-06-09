from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from time import time
import jwt
import json
import redis
import rq
from flask import current_app,flash
import json



from app import db
from app import login

def test(a,b):
    flash("hello")

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    dataset_uploaded = db.relationship('Dataset', foreign_keys = 'Dataset.user_id', backref ='user', lazy='dynamic')
    experiment_achivied = db.relationship('Experiment', foreign_keys = 'Experiment.user_id', backref = 'user', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    def launch_experiment(self,dataset_id,experiment_name,parameter_dct):
        #'app.experiment.test'
        rq_job = current_app.task_queue.enqueue(f = 'app.test' , args = (dataset_id,parameter_dct))
        experiement = Experiment(id=rq_job.get_id(),user = self ,dataset_id = dataset_id,experiment_name=experiment_name, experiment_parameters = json.dumps(parameter_dct))
        db.session.add(experiement)
        return experiement

    def get_experiments_in_progress(self):
        return Experiment.query.filter_by(user=self, complete=False).all()

    def get_experiment_in_progress(self, name):
        return Experiment.query.filter_by(experiment_name=name, user=self,complete=False).first()

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

        
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Dataset(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    dataset = db.Column(db.PickleType())
    label = db.Column(db.PickleType())
    dataset_name = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    experiment_linked = db.relationship('Experiment', foreign_keys = 'Experiment.dataset_id', backref = 'dataset', lazy='dynamic')

    def __repr__(self) -> str:
        return 'Dataset: {}'.format(self.dataset_name)

class Experiment(db.Model): 
    id = db.Column(db.String(36), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    experiment_name = db.Column(db.String(64), index=True, unique=True)
    experiment_parameters = db.Column(db.String())
    experiment = db.Column(db.PickleType(),default = None)
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return 'Experiment: {}'.format(self.experiment_name)

    def parameters_to_dict(self): 
        return json.loads(self.experiement_parameters)

    def get_parameter(self,parameter): 
        return json.loads(self.experiement_parameters)[parameter]
    
    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 'Experiment to be executed') if job is not None else 'Experiment Done'