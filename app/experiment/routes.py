from flask import render_template, flash, redirect, url_for,request
from flask_login import current_user,login_required



from app.experiment.forms import ExperimentParameters
from app.experiment import bp
from app.models import Dataset,Experiment
from app import db

########################################################################################################################
#FUNCTION
########################################################################################################################


########################################################################################################################
########################################################################################################################

@bp.route('/learn_predict', methods=['GET', 'POST'])
@login_required
def learn_predict(): 
    form = ExperimentParameters()
    user_datasets = Dataset.query.filter_by(user_id = current_user.id).all()
    lst = []
    for dataset in user_datasets: 
        lst.append((dataset.id,dataset.dataset_name))
    form.dataset_id.choices = lst
    if form.validate_on_submit():
        if len(current_user.get_experiments_in_progress())>4:
            flash(f'You have 5 experiments running; please wait for the completion of one experiment before starting another.')
        else: 
            current_user.launch_experiment(form.dataset_id.data, form.experiment_name.data,form.parameters_to_dct())
            #run_experiment(form.dataset_id.data,form.parameters_to_dct())
            db.session.commit()
            flash(f'Experiment: {form.experiment_name.data} is launched, an email will inform you of its completion.')
        return redirect(url_for('main.index'))
    return render_template('experiment/learn_predict.html',form =form)


@bp.route('/manage_experiments', methods=['GET','POST'])
@login_required
def manage_experiments(): 
    user_experiments = Experiment.query.filter_by(user_id = current_user.id).all()
    lst =[]
    for experiment in user_experiments: 
        lst.append(experiment.experiment_name)
    return render_template('experiment/manage_experiments.html', lst = lst)

@bp.route('/delete_experiment<experiment_name>', methods=['GET', 'POST'])
@login_required
def delete_experiment(experiment_name):
    experiment = Experiment.query.filter_by(experiment_name = experiment_name).first()
    db.session.delete(experiment)
    db.session.commit()
    return redirect(url_for('experiment.manage_experiments'))

@bp.route('/dowmload_experiment<experiment_name>', methods=['GET', 'POST'])
@login_required
def download_experiment(experiment_name):
    return redirect(url_for('experiment.manage_experiments'))