from rq import get_current_job
from flask import flash
import sys
import pickle

from app import create_app, db
from app.models import Experiment,Dataset
from tools.pipeline import Pipeline
from tools.clustering import EmptyClusterError
from app.auth.email import send_email

app = create_app()
app.app_context().push()

def run_experiment(dataset_id,parameter_dct): 
    
    #run the experiment. 
    job = get_current_job()
    experiment = Experiment.query.get(job.get_id())

    dataset = Dataset.query.filter_by(id = int(dataset_id)).first()
    data = pickle.loads(dataset.dataset)
    pipe = Pipeline(**parameter_dct)
    pipe.fit(data)
    experiment.experiment = pickle.dumps(pipe)
    experiment.complete = True
    db.session.commit()
    flash(f"Experiment: {experiment.experiment_name}, is complete.")
    #except EmptyClusterError: 
    #    flash('Experiment resumed because of an empty cluster. Please reduce ')
    #except : 
    #    flash('Unhandled Error. Please retry and if the error persists contact us.')
    #    app.logger.error('Unhandled exception', exc_info=sys.exc_info())

def test(a,b):
    flash('Hello')


