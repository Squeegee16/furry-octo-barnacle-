from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SelectField,BooleanField, SubmitField, FloatField, SubmitField, TextAreaField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired,NumberRange,length, EqualTo, Email



class addproduct(FlaskForm):
    prodname = StringField('Plant Name', validators=[DataRequired()])
    prodvar = StringField('Variety', validators=[DataRequired()])
    prodqty = IntegerField('Quantity', validators=[NumberRange(min=1, max=100),DataRequired()])
    prodsubmit = SubmitField('Save Changes')

class editproduct(FlaskForm):
    editname = StringField('Plant Name', validators=[DataRequired()])
    editvar = StringField('Variety', validators=[DataRequired()])
    editqty = IntegerField('Quantity', validators=[NumberRange(min=1, max=100),DataRequired()])
    editsubmit = SubmitField('Save Changes')

class editplantdata(FlaskForm):
    epdhardiness = StringField('Hardiness Type           ')
    epdplantdate = StringField('Reccomended Planting Date')
    epdDTM = IntegerField('Days to Maturity         ', validators=[NumberRange(min=-1, max=1095)])
    epdgermination = IntegerField('Germination Time in days ', validators=[NumberRange(min=-1, max=180)])
    epdsowtype = StringField('Direct Sow or Transplantable?')
    epdseeddepth = FloatField('Sowing Depth in inches     ')
    epdseedspacemin = FloatField('Minimum Seed spacing inches')
    epdseedspacemax = FloatField('Maximum Seed spacing inches')
    epdrowspacemin = FloatField('Minimum Row spacing inches ')
    epdrowspacemax = FloatField('Maximum Row spacing inches ')
    epdfamilyBrassica =BooleanField('Brassica Family') 
    epdfamilyCarrot =BooleanField('Carrot Family') 
    epdfamilyCelery =BooleanField('Celery Family') 
    epdfamilyBean =BooleanField('Bean Family') 
    epdfamilyBeet =BooleanField('Beet Family') 
    epdfamilyOnion =BooleanField('Onion Family')
    epdfamilyPea =BooleanField('Pea Family') 
    epdfamilyPepper =BooleanField('Pepper Family') 
    epdfamilyPotato =BooleanField('Potato Family') 
    epdfamilySquash =BooleanField('Squash Family')
    epdfamilyTomato =BooleanField('Tomato Family')  
    epdpic = FileField('Update Plant Picture', validators=[FileAllowed(['jpg', 'png'])])
    epdsubmit = SubmitField('Save Changes')

class addlocation(FlaskForm):
    locname = StringField('Location Name', validators=[DataRequired()])
    locarea = StringField('Usable Area')
    locsubmit = SubmitField('Save Changes')

class editlocation(FlaskForm):
    editlocname = StringField('Location Name', validators=[DataRequired()])
    editlocarea = IntegerField('Usable Area', validators=[DataRequired()])
    editloclat = FloatField('Latitude in DD.DDD')
    editloclon = FloatField('Longitude in DD.DDD')
    editlocsubmit = SubmitField('Save Changes')

class moveproduct(FlaskForm):
    mprodname = SelectField('Plant Name')
    mprodvar = SelectField('Plant Variety')
    src = SelectField('Source')
    destination = SelectField('Destination')
    mprodqty = IntegerField('Quantity', validators=[NumberRange(min=1, max=100),DataRequired()])
    movesubmit = SubmitField('Move')

##########################################################################
class archivedata(FlaskForm):
    ll = StringField('')
    archivesubmit = SubmitField('are you sure?')