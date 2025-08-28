from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, NumberRange, URL
from models import User, GlobalSettings


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active')
    reset_password = BooleanField('Reset Password')
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    submit = SubmitField('Update User')


class OllamaSettingsForm(FlaskForm):
    ollama_url = StringField('Ollama URL', validators=[DataRequired(), URL()], 
                           default='http://localhost:11434')
    default_chat_model = StringField('Default Chat Model', validators=[DataRequired()],
                                   default='llama3.1')
    default_vision_model = StringField('Default Vision Model', validators=[DataRequired()],
                                     default='llava')
    model_timeout = IntegerField('Model Timeout (seconds)', validators=[NumberRange(min=10, max=300)],
                                default=120)
    max_tokens = IntegerField('Max Tokens', validators=[NumberRange(min=100, max=4096)],
                             default=2048)
    temperature = FloatField('Temperature', validators=[NumberRange(min=0.0, max=2.0)],
                            default=0.7)
    submit = SubmitField('Save Settings')


class GlobalSettingForm(FlaskForm):
    key = StringField('Setting Key', validators=[DataRequired(), Length(max=100)])
    value = TextAreaField('Value', validators=[DataRequired()])
    description = TextAreaField('Description')
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('ollama', 'Ollama'),
        ('security', 'Security'),
        ('ui', 'User Interface'),
        ('api', 'API'),
        ('performance', 'Performance')
    ], default='general')
    submit = SubmitField('Save Setting')


class SystemMaintenanceForm(FlaskForm):
    action = SelectField('Maintenance Action', choices=[
        ('clear_logs', 'Clear System Logs'),
        ('optimize_db', 'Optimize Database'),
        ('reset_user_sessions', 'Reset All User Sessions'),
        ('backup_db', 'Backup Database'),
        ('clear_temp_files', 'Clear Temporary Files')
    ])
    confirm = BooleanField('I understand this action cannot be undone', validators=[DataRequired()])
    submit = SubmitField('Execute Action')


class BulkUserActionForm(FlaskForm):
    action = SelectField('Bulk Action', choices=[
        ('activate', 'Activate Selected Users'),
        ('deactivate', 'Deactivate Selected Users'),
        ('delete', 'Delete Selected Users'),
        ('make_admin', 'Make Admin'),
        ('remove_admin', 'Remove Admin')
    ])
    user_ids = StringField('User IDs (comma-separated)', validators=[DataRequired()])
    confirm = BooleanField('I confirm this bulk action', validators=[DataRequired()])
    submit = SubmitField('Execute Bulk Action')