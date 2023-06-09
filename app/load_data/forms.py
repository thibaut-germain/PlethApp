from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_wtf.file import FileField,FileRequired,FileAllowed
from flask_login import current_user


from app.models import Dataset



class UploadData(FlaskForm): 
    dataset = FileField('Dataset', validators=[FileRequired(), FileAllowed(['zip'],"zip only!")])
    labels = FileField('Labels',validators=[FileAllowed(['txt', 'csv' ],"txt or csv only!")])
    dataset_name = StringField('Dataset Name', validators=[DataRequired()])
    submit = SubmitField('Upload')

    def validate_name(name): 
        dataset =  Dataset.query.filter_by(user_id = current_user.id,dataset_name =name).first()
        if dataset is not None: 
            raise ValidationError('Please use a different dataset name.')