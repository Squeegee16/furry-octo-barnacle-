from flaskinventory import db
from flask import current_app
from sqlalchemy.sql import func
from datetime import datetime

class Location(db.Model):
    loc_id = db.Column(db.Integer, primary_key= True)
    loc_name = db.Column(db.String(40),unique = True, nullable = False)
    loc_area = db.Column(db.String(20),unique = False, nullable = True, default = 0)
    loc_space = db.Column(db.Float, nullable = True)
    lat = db.Column(db.Float, unique=False, default = 0.0)
    lon = db.Column(db.Float, unique=False, default = 0.0)
    # notes about location - to add

    def __repr__(self):
        return f"Location('{self.loc_id}','{self.loc_name}','{self.loc_area}')"
        # return "Location('{self.loc_id}','{self.loc_name}','{self.loc_area}',)"

class Movement(db.Model):
    mid = db.Column(db.Integer, primary_key= True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    frm = db.Column(db.String(20), nullable = False)
    to = db.Column(db.String(20), nullable = False)
    pname = db.Column(db.String(20), nullable = False)
    pqty = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Movement('{self.mid}','{self.ts}','{self.frm}','{self.to}','{self.pname}','{self.pqty}')"

class Balance(db.Model):

    bid = db.Column(db.Integer, primary_key= True,nullable = False)
    product = db.Column(db.String(20), nullable = False)
    var = db.Column(db.String(80), nullable = False)
    location = db.Column(db.String(40),nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    usedSpace = db.Column(db.Float, unique=False, default = 0.0)
    availSpace = db.Column(db.Float, unique=False, default = 0.0)
    planted_date = db.Column(db.String(6), unique=False, nullable=True)
    xfer_date = db.Column(db.DateTime,nullable = True)
    #notes that follow plant to add

    def __repr__(self):
        return f"Balance('{self.bid}','{self.product}','{self.location}','{self.quantity}','{self.var}','{self.planted_date}','{self.usedSpace}')"

class Weather(db.Model):
    __tablename__ = 'Weather'

    wid = db.Column(db.Integer, primary_key= True,nullable = False)
    FFD = db.Column(db.String(6), unique=False, nullable=True)
    SFD = db.Column(db.String(6), unique=False, nullable=True)
    called = db.Column(db.DateTime, unique=True, nullable=True,default=None)
    sun_rise = db.Column(db.String(10), unique=False, nullable=True)
    sun_set = db.Column(db.String(10), unique=False, nullable=True)
    day_len = db.Column(db.String(10), unique=False, nullable=True)
    dwnst = db.Column(db.String(10), unique=False, nullable=True)
    dwnsp = db.Column(db.String(10), unique=False, nullable=True)

    def __repr__(self):
        return f"Weather('{self.wid}','{self.FFD}','{self.SFD}')"



class Product(db.Model):
    __tablename__ = 'Product'
    prod_id = db.Column(db.Integer, primary_key= True)
    prod_name = db.Column(db.String(20),unique = False ,nullable = False)
    prod_qty = db.Column(db.Integer, nullable = True)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    variety = db.Column(db.String(80), unique=False, nullable=True, default='Generic')
    SowType = db.Column(db.String(12), unique=False, nullable=True)
    DTMat = db.Column(db.Integer, unique=False, nullable=True,default=0)
    germination = db.Column(db.Integer, unique=False, nullable=True)
    RPinterval = db.Column(db.Integer, unique=False, default=0)
    Hardiness = db.Column(db.String(5), unique=False, nullable=True)
    RPdate = db.Column(db.String(6), unique=False, nullable=True)
    LPdate = db.Column(db.String(6), unique=False, nullable=True)
    Sdepth = db.Column(db.Float, unique=False, nullable=True)
    SspaceMin = db.Column(db.Float, unique=False, nullable=True)
    SspaceMax = db.Column(db.Float, unique=False, nullable=True)
    SrowspaceMin = db.Column(db.Float, unique=False, nullable=True)
    SrowspaceMax = db.Column(db.Float, unique=False, nullable=True)
    CFam_bean = db.Column(db.Boolean, nullable=False, default=False)
    CFam_beet = db.Column(db.Boolean, nullable=False, default=False)
    CFam_brassica = db.Column(db.Boolean, nullable=False, default=False)
    CFam_carrot = db.Column(db.Boolean, nullable=False, default=False)
    CFam_celery = db.Column(db.Boolean, nullable=False, default=False)
    CFam_onion = db.Column(db.Boolean, nullable=False, default=False)
    CFam_pea = db.Column(db.Boolean, nullable=False, default=False)
    CFam_pepper = db.Column(db.Boolean, nullable=False, default=False)
    CFam_potato = db.Column(db.Boolean, nullable=False, default=False)
    CFam_gourd = db.Column(db.Boolean, nullable=False, default=False)
    CFam_tomato = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.String(100), unique=False, default='No Notes')
    
    def __repr__(self):
        #return f"Product('{self.prod_id}','{self.prod_name}','{self.prod_qty}')"
        return f"Product('{self.prod_id}','{self.prod_name}','{self.prod_qty}','{self.image_file}',\
'{self.variety}','{self.DTMat}','{self.SowType}','{self.germination}','{self.RPinterval}',\
'{self.Hardiness}','{self.RPdate}','{self.LPdate}','{self.Sdepth}','{self.SspaceMin}',\
'{self.SspaceMax}','{self.SrowspaceMin}','{self.SrowspaceMax}','{self.CFam_bean}','{self.CFam_beet}',\
'{self.CFam_brassica}','{self.CFam_carrot}','{self.CFam_celery}','{self.CFam_onion}','{self.CFam_pea}',\
'{self.CFam_pepper}','{self.CFam_potato}','{self.CFam_gourd}','{self.CFam_tomato}','{self.notes}')"

#####################################################################

class archive(db.Model):
    __bind_key__ = 'old'
    __tablename__ = 'archive'
    item_id = db.Column(db.Integer, primary_key= True)
    location = db.Column(db.String(40),nullable = False)
    product = db.Column(db.String(20), nullable = False)
    var = db.Column(db.String(80), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    planted_date = db.Column(db.String(6), unique=False, nullable=True)
    planted_year = db.Column(db.Integer, nullable = False)
    xfer_date = db.Column(db.DateTime,nullable = True)
    def __repr__(self):
        return f"archive('{self.item_id}','{self.location}',\
        '{self.product}','{self.quantity}','{self.var}',\
        '{self.planted_date}',{self.planted_year}','{self.xfer_date}')"
