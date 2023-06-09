from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from zipfile import ZipFile
import pickle as pkl


from app.load_data.forms import UploadData
from app.load_data import bp
from app.models import Dataset
from app import db
from app.load_data.upload import from_zip_dataset_to_numpy, from_labels_to_dataframe


@bp.route('/upload_data', methods=['GET','POST'])
@login_required
def upload_data(): 
    form = UploadData()
    if form.validate_on_submit():
        dataset = form.dataset.data
        #dataset without name
        if dataset.filename == "":
            flash('The dataset has no name.')
            return render_template('upload_data.html', form =form)

        #transform the dataset in an array 
        try:
            dataset_arr = from_zip_dataset_to_numpy(ZipFile(dataset._file))
        except: 
            flash('Issue with the dataset zip file.')
            return render_template('load_data/upload_data.html', form =form)

        #transform the labels in an dataframe
        labels = form.labels.data
        if labels is not None:
            try: 
                labels_df = from_labels_to_dataframe(labels._file)
            except: 
                flash('Issue with the labels file.')
                return render_template('upload_data.html', form =form)

            if dataset_arr.shape[0] != labels_df.values.shape[0]: 
                flash(f'The number of files and the number of labels are not matching.')
                return render_template('load_data/upload_data.html', form =form)
            else: 
                labels_pkl = pkl.dumps(labels_df)
        else: 
            labels_pkl = None

        dataset_pkl = pkl.dumps(dataset_arr)

        dataset = Dataset(dataset = dataset_pkl, label = labels_pkl, dataset_name = form.dataset_name.data, user_id = current_user.id)
        db.session.add(dataset)
        db.session.commit()
        flash('Dataset Successfully uploaded!')
        return redirect(url_for('main.index'))
    return render_template('load_data/upload_data.html', form =form)

@bp.route('/manage_data', methods=['GET', 'POST'])
@login_required
def manage_data(): 
    user_datasets = Dataset.query.filter_by(user_id = current_user.id).all()
    lst =[]
    for dataset in user_datasets: 
        lst.append(dataset.dataset_name)
    return render_template('load_data/manage_data.html',lst =lst)

@bp.route('/delete_data<dataset_name>', methods =['GET','POST'])
@login_required
def delete_data(dataset_name): 
    dataset = Dataset.query.filter_by(dataset_name = dataset_name).first()
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('load_data.manage_data'))