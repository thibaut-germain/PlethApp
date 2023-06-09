from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, SelectField,IntegerField,FloatField
from wtforms.validators import ValidationError, DataRequired, NumberRange
from flask_login import current_user

from app.models import Experiment

class ExperimentParameters(FlaskForm): 
    dataset_id = SelectField('Select a dataset', validators=[DataRequired()], coerce=int,validate_choice=False)
    experiment_name = StringField('Experiment Name', validators=[DataRequired()])

    sampfreq = IntegerField('Sampling frequency (Hz)',validators=[DataRequired()],default = 2000)
    down_sampfreq = IntegerField('Down sampling frequency (Hz), optional',validators=[DataRequired()], default = 250)
    prominence = FloatField('Peak prominence (ml)', validators=[DataRequired()],default = 0.03)
    wlen = FloatField('Window size for prominence search (s)', validators=[DataRequired()],default = 2)
    minimum_cycle_duration = FloatField('Minimum cycle duration (s)', validators=[DataRequired()],default = 0.1)
    maximum_cycle_duration = FloatField('Maximum cycle duration (s)', validators=[DataRequired()],default = 3)
    training_size_per_interval = IntegerField('Training size per interval',validators=[DataRequired()],default = 30)
    interval_size = IntegerField('Interval size (s)',validators=[DataRequired()],default=60)

    n_iteration = IntegerField('Number of clustering iteration',validators=[DataRequired()],default =10)
    n_in_cluster = IntegerField('Number of inhalation cluster',validators=[DataRequired()], default = 5)
    n_out_cluster = IntegerField('Number of exhalation cluster',validators=[DataRequired()],default=5)
    in_cluster_duration = FloatField('Inhalation duration (s)', validators=[DataRequired()],default=0.2)
    out_cluster_duration = FloatField('Exhalation duration (s)', validators=[DataRequired()],default=0.2)
    radius = FloatField('Maximum time warping (s)', validators=[DataRequired()],default=0.02)
    quantile_threshold = FloatField('Quantile threshold for prediction',validators=[DataRequired(),NumberRange(0,1)],default =0.95)

    submit = SubmitField('Launch experiment')

    def parameters_to_dct(self): 
        dct = dict(
            sampfreq = self.sampfreq.data,
            down_sampfreq = self.down_sampfreq.data,
            prominence = self.prominence.data,
            wlen = self.wlen.data,
            cycle_minimum_duration = self.minimum_cycle_duration.data,
            cycle_maximum_duration = self.maximum_cycle_duration.data, 
            training_size_per_interval = self.training_size_per_interval.data,
            interval = self.interval_size.data,
            n_iteration = self.n_iteration.data,
            in_ncluster = self.n_in_cluster.data,
            out_ncluster = self.n_out_cluster.data,
            in_centroid_duration = self.in_cluster_duration.data, 
            out_centroid_duration = self.out_cluster_duration.data,
            radius = self.radius.data,
            quantile_threshold = self.quantile_threshold.data,
        )
        return dct

    def validate_experiment_name(self,experiement_name): 
        experiment = Experiment.query.filter_by(user_id = current_user.id,experiment_name=experiement_name.data).first()
        if experiment is not None: 
            raise ValidationError('Please use a different experiement name.')