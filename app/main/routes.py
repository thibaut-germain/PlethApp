from flask import render_template, flash, redirect, url_for,current_app
from flask_login import current_user,logout_user,login_required
from datetime import datetime

from app.main import bp
from app.main.forms import ContactUs
from app.auth.forms import ResetPasswordForm
from app import db
from app.auth.email import send_email



@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@bp.route('/change_password', methods=['GET', 'POST'])
def change_password(): 
    form = ResetPasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        logout_user()
        flash('Your password has been changed. Please sign in.')
        return redirect(url_for('main.index'))
    return render_template('change_password.html', title="Change password", form = form)


@bp.route('/contact_us', methods=['GET', 'POST'])
@login_required
def contact_us():
    form = ContactUs()
    if form.validate_on_submit(): 
        subject = f"{form.subject.data}--{form.email.data}"
        send_email(subject,current_app.config['SENDING_ADDRESS'],current_app.config['CONTACTS'],form.message.data,None)
        flash("Message successfully send")
        return redirect(url_for('main.index'))
    return render_template('contact_us.html',title='Contact us',form=form)