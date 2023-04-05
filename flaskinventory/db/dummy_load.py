#! /usr/bin/env python3

from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sqlalchemy.sql import func
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin 
from os import path
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from csv import reader
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_ECHO'] = 'False'
db = SQLAlchemy(app)

class Location(db.Model):
    loc_id = db.Column(db.Integer, primary_key= True)
    loc_name = db.Column(db.String(20),unique = True, nullable = False)
    loc_area = db.Column(db.String(20),unique = False, nullable = True, default = 0)
    loc_space = db.Column(db.Float, nullable = True)
    lat = db.Column(db.Float, unique=False, default = 0.0)
    lon = db.Column(db.Float, unique=False, default = 0.0)

    def __repr__(self):
        return f"Location('{self.loc_id}','{self.loc_name}','{self.loc_area}')"
        return "Location('{self.loc_id}','{self.loc_name}','{self.loc_area}',)"

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
    var = db.Column(db.String(20), nullable = False)
    location = db.Column(db.String(20),nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    usedSpace = db.Column(db.Float, unique=False, default = 0.0)
    availSpace = db.Column(db.Float, unique=False, default = 0.0)
    planted_date = db.Column(db.String(6), unique=False, nullable=True)
    xfer_date = db.Column(db.DateTime,nullable = True)

    def __repr__(self):
        return f"Balance('{self.bid}','{self.product}','{self.location}','{self.quantity}','{self.var}','{self.planted_date}')"

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
    CFam_cabbage = db.Column(db.Boolean, nullable=False, default=False)
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
'{self.CFam_cabbage}','{self.CFam_carrot}','{self.CFam_celery}','{self.CFam_onion}','{self.CFam_pea}',\
'{self.CFam_pepper}','{self.CFam_potato}','{self.CFam_gourd}','{self.CFam_tomato}','{self.notes}')"


def create_database(app):
    if not path.exists('site.db'):
        db.create_all(app=app)
        print('Created Database!')
    else:
        print("Resetting Database")
        db.drop_all(app=app)
        db.create_all(app=app)
        print('Database Refeshed!')

def str2bool(v):
#     return v.lower() in ("yes", "true", "t", "1")
    if type(v) == str:
        return v.lower() in ("yes", "true", "t", "1")
    else:
        v=str(v)
        return v.lower() in ("yes", "true", "t", "1")

def main(test, load):
    if test == False and load == True:
        ##########################################################################################
        create_database(app)
        ##########################################################################################
        print("Generating location")
        #pw = generate_password_hash('password', method='sha256')

        loc_to_load = Location(loc_name = "greenhouse", loc_area = 5184,lat = 44.796307,lon = -63.678483)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Box 2", loc_area = 2304.0,lat = 44.79629,lon = -63.678441)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Box 1", loc_area = 2304.0,lat = 44.796262,lon = -63.678441)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Carrot Bed", loc_area = 1728.0,lat = 44.796096,lon = -63.678395)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Strawberry Bed", loc_area = 1728.0,lat = 44.796085,lon = -63.678402)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Teir 1", loc_area = 6960.0,lat = 44.796269,lon = -63.678428)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Teir 2", loc_area = 7656.0,lat = 44.796269,lon = -63.678411)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Teir 3", loc_area = 12528.0,lat = 44.796269,lon = -63.678374)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Nursery", loc_area = 0.0,lat = 44.796269,lon = -63.678374)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Compost", loc_area = 0.0,lat = 44.796269,lon = -63.678374)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Arch Side 1", loc_area = 1044.0,lat = 44.796269,lon = -63.678374)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Arch Side 2", loc_area = 1044.0,lat = 44.796269,lon = -63.678374)
        db.session.add(loc_to_load)
        loc_to_load = Location(loc_name = "Yard", loc_area = 1000000.0,lat = 44.796269,lon = -63.678374)
        db.session.add(loc_to_load)
        db.session.commit()
        # print("Loaded location 1")
        # loc_to_load = Location(loc_name = "garden", loc_area = 10)
        # db.session.add(loc_to_load)
        # db.session.commit()
        print("Loaded location 2")
        # ##########################################################################################
        print("generating weather table")
        weather = Weather(FFD = '15-Oct',SFD= '15-May')
        db.session.add(weather)
        db.session.commit()

        ##########################################################################################
        print("Select plant library to load") 
        Tk().withdraw()
        file = askopenfilename()
        line = 0
        rows=[]
        with open(file,'r', encoding="utf-8-sig") as csvfile:
            rdr=reader(csvfile, delimiter=",")
            fields = next(rdr)
            for row in rdr:
                rows.append(row)
            row_count = rdr.line_num
        # print(rows)
        csvfile.closed
        for row in rows:
            #print("A", row_count, line)
            if not line < row_count:
                break
            else:
                plib = Product(prod_name = row[0],prod_qty = 100,image_file = "default.png",variety = row[1],DTMat = row[2],SowType = row[3],germination = row[4],
                    RPinterval = row[5],Hardiness = row[6],RPdate = row[7],LPdate = row[8],Sdepth = row[9],
                    SspaceMin = row[10],SspaceMax = row[11],SrowspaceMin = row[12],SrowspaceMax = row[13],
                #######################################################################################
                    CFam_bean = str2bool(row[14]),CFam_beet = str2bool(row[15]),CFam_cabbage = str2bool(row[16]),CFam_carrot = str2bool(row[17]),
                    CFam_celery = str2bool(row[18]),CFam_onion = str2bool(row[19]),CFam_pea = str2bool(row[20]),CFam_pepper = str2bool(row[21]),
                    CFam_potato = str2bool(row[22]),CFam_gourd = str2bool(row[23]),CFam_tomato = str2bool(row[24]),notes = row[52])

                db.session.add(plib)
                db.session.commit()
            line += 1
       
        print("Loaded ", line, " Plants")
        ##########################################################################################
        # print("loading location movements")
        # garden_to_load = Movement(ts=datetime.utcnow,frm="greenhouse",to="garden",pname="Onion",pqty=5)
        # db.session.add(garden_to_load)
        # db.session.commit()
        # ##########################################################################################
        # print("Inserting location balances")
        # bal_to_load = Balance(product="Onion",location="greenhouse",quantity=5)
        # bal_to_load = Balance(product="Onion",location="garden",quantity=5)
        # bal_to_load = Balance(product="Peas",location="greenhouse",quantity=5)
        # db.session.add(bal_to_load)
        # db.session.commit()
        ##########################################################################################
        print('complete')
        db.session.close()
        exit()

    # elif test == False and load == False:
    #     user_csv=db.session.query(Plantdata).filter_by(family="Onion").all()

    #     fieldnames = ["Family","image_file","Variety","Days to Maturity","Sow Type","germination","Planting Interval","Hardiness","Reccomended planting date","Last Planting Date","Seed Planting Depth","Seed Spacing","Seed Spacing max","Seed Row Spacing","Seed Row Spacing max","Bean Family","Beet Family","Cabbage Family","Carrot Family","Celery Family","Onion Family","Pea Family","Pepper Family","Potato Family","Squash Family","Tomato Family","Notes"]
    #     for row in user_csv:
    #         for index in range(0,len(fieldnames[:7])):
    #             print(type(index),type(row),type(fieldnames),type(fieldnames[:7]),type(user_csv))
    #             x = fieldnames[index]
    #             print(user_csv[x])

    #     db.session.close()
    #     exit()

    # else:
    #     conn = sqlite3.connect('site.db')
    #     c = conn.cursor()

        # c.execute("SELECT * FROM Product WHERE prod_name = Onion", {'prod_name': 'Onion'})
        # x = c.fetchall()
        # for row in range(0, len(x)):
        #     print("A:" ,type(x[row])," :",x[row],"\n") 

        # c.execute("SELECT * FROM Location WHERE loc_name = greenhouse'", {'loc_name': 'greenhouse'})
        # x = c.fetchall()
        # for row in range(0, len(x)):
        #     print("A:" ,type(x[row])," :",x[row],"\n") 

        # c.execute("SELECT * FROM Movement WHERE frm=greenhouse", {'frm': 'greenhouse'})
        # x = c.fetchall()
        # for row in range(0, len(x)):
        #     print("A:" ,type(x[row])," :",x[row],"\n") 

        # c.execute("SELECT * FROM Balance WHERE product=Onion", {'product': 'Onion'})
        # x = c.fetchall()
        # for row in range(0, len(x)):
        #     print("A:" ,type(x[row])," :",x[row],"\n") 

        # user_csv=c.execute("SELECT * FROM Product WHERE family=:family", {'family': 'Onion'}).fetchall()

        # fieldnames = ["Family","image_file","Variety","Days to Maturity","Sow Type","germination","Planting Interval","Hardiness","Reccomended planting date","Last Planting Date","Seed Planting Depth","Seed Spacing","Seed Spacing max","Seed Row Spacing","Seed Row Spacing max","Bean Family","Beet Family","Cabbage Family","Carrot Family","Celery Family","Onion Family","Pea Family","Pepper Family","Potato Family","Squash Family","Tomato Family","Notes"]
        # for row in user_csv:
        #     print(row)
        #     for index in range(0,len(fieldnames)):
        #         print(row[index])

        # conn.close()


    if __name__ == '__main__':
        app.run(debug=True)
############################
main(False, True)