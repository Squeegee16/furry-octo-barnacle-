from flask import  render_template,url_for,redirect,flash,request,jsonify, Blueprint
from flaskinventory import current_app,db
from flaskinventory.main.forms import addproduct,addlocation,moveproduct,editproduct,editlocation,editplantdata
from flaskinventory.models import Location,Product,Movement,Balance,Weather
from flaskinventory.main.utils import save_picture, cal_space, create_p2, planting_interval,growth_status,db_convert,getfrosty,montoint,getastrodata,str2bool,update_sorter
import time,datetime
from sqlalchemy.exc import IntegrityError
import re

main = Blueprint('main', __name__)

@main.route("/Overview")
def overview():
    balance = Balance.query.all()
    location = Location.query.all()
    exists = bool(Balance.query.all())
    if exists== False :
        flash(f'Nothing Planted', 'info')
    
    return render_template('overview.html' ,balance=balance)


@main.route("/Product", methods = ['GET','POST'])
def product():
    form = addproduct()
    eform = editproduct()
    details = Product.query.all()
    exists = bool(Product.query.all())

    if exists== False and request.method == 'GET' :
            flash(f'Library Empty','info')
    elif eform.validate_on_submit() and request.method == 'POST':
# existing plant
        p_id = request.form.get("Plantid","")
        pname = request.form.get("Plantname","")
        prod = Product.query.filter_by(prod_id = p_id).first()

        locSpace = Location.query.filter_by(loc_name = pname).first()
        if locSpace == None:
            Product.query.filter_by(prod_id=p_id).update(dict(prod_name = eform.editname.data,variety =eform.editvar.data,prod_qty =eform.editqty.data))
            db.session.commit()
            flash(f'Your plant data has been updated!', 'success')
            return redirect('/Product')
        else:
            prod.prod_name = eform.editname.data
            prod.prod_qty= eform.editqty.data
            prod.prodvar= eform.editvar.data
    #<!-- area caluclations -->
            Aused = cal_space(locSpace.loc_area,prod.SspaceMin,prod.prod_qty)
            Balance.query.filter_by(product=pname).update(dict(product=eform.editname.data,usedSpace=Aused[0],availSpace=Aused[1]))
            Movement.query.filter_by(pname=pname).update(dict(pname=eform.editname.data))
        try:
            db.session.commit()
            flash(f'Your plant data has been updated!', 'success')
            return redirect('/Product')
        except IntegrityError :
            db.session.rollback()
            flash(f'This plant already exists','danger')
            return redirect('/Product')
        return render_template('product.html',details=details,eform=eform)
#new plant
    elif form.validate_on_submit() :
        product = Product(prod_name=form.prodname.data,variety=form.prodvar.data,prod_qty=form.prodqty.data)
        db.session.add(product)
        try:
            db.session.commit()
            flash(f'Your plant "{form.prodname.data}" has been added!', 'success')
            return redirect(url_for('main.product'))
        except IntegrityError :
            db.session.rollback()
            flash(f'This plant already exists','danger')
            return redirect('/Product')
    return render_template('product.html',eform=eform,form=form,details=details)



@main.route("/Location", methods = ['GET', 'POST'])
def loc():
    form = addlocation()
    lform = editlocation()
    details = Location.query.all()
    exists = bool(Location.query.all())
    if exists== False and request.method == 'GET':
            flash(f'Add locations to view','info')
    if lform.validate_on_submit() and request.method == 'POST':
        p_id = request.form.get("locid","")
        locname = request.form.get("locname","")
        locarea = request.form.get("locarea","")
        details = Location.query.all()
        loc = Location.query.filter_by(loc_id = p_id).first()
        loc.loc_name = lform.editlocname.data
        loc.loc_area = lform.editlocarea.data
        loc.lat=lform.editloclat.data
        loc.lon=lform.editloclon.data
        
        Balance.query.filter_by(location=locname).update(dict(location=lform.editlocname.data))

        Movement.query.filter_by(frm=locname).update(dict(frm=lform.editlocname.data))

        Movement.query.filter_by(to=locname).update(dict(to=lform.editlocname.data))
        try:
            db.session.commit()
            flash(f'Your location has been updated!', 'success')
            return redirect(url_for('main.loc'))
        except IntegrityError :
            db.session.rollback()
            flash(f'This location already exists','danger')
            return redirect('/Location')
    elif form.validate_on_submit() :
        loc = Location(loc_name=form.locname.data,loc_area=form.locarea.data,lat=lform.editloclat.data,lon=lform.editloclon.data)
        db.session.add(loc)
        try:
            db.session.commit()
            flash(f'Your location {form.locname.data} has been added!', 'success')
            return redirect(url_for('main.loc'))
        except IntegrityError :
            db.session.rollback()
            flash(f'This location already exists','danger')
            return redirect('/Location')
    return render_template('loc.html',lform=lform,form = form,details=details)



@main.route("/Transfers", methods = ['GET', 'POST'])
def move():
    form = moveproduct()

    details = Movement.query.all()
    pdetails = Product.query.all()
    exists = bool(Movement.query.all())
    if exists== False and request.method == 'GET' :
            flash(f'Change Plant location','info')
    #----------------------------------------------------------
    prod_choices = Product.query.with_entities(Product.prod_name,Product.prod_name).all()
    variety_choice = Product.query.with_entities(Product.variety,Product.variety).all()
    loc_choices = Location.query.with_entities(Location.loc_name,Location.loc_name).all()
    prod_list_names = []
    var_list_names = []
    src_list_names,dest_list_names=[('Seed Library','Seed Library')],[('Seed Library','Seed Library')]

    prod_list_names+=prod_choices
    src_list_names+=loc_choices
    dest_list_names+=loc_choices
    var_list_names+=variety_choice

    #passing list_names to the form for select field
    form.mprodname.choices = prod_list_names
    form.src.choices = src_list_names
    form.mprodvar.choices = var_list_names
    form.destination.choices = dest_list_names
    #--------------------------------------------------------------
    #send to db
    if form.validate_on_submit() and request.method == 'POST' :

        timestamp = datetime.datetime.now()
        t2 = timestamp.strftime("%d %b")
        boolbeans = check(form.src.data,form.destination.data,form.mprodname.data,form.mprodvar.data,form.mprodqty.data)
        if boolbeans == False:
            flash(f'Not enough seeds/plants in location', 'danger')
        elif boolbeans == 'same':
            flash(f'Source and destination cannot be the same.', 'danger')
        elif boolbeans == 'no prod':
            flash(f'Not enough Plants in this location.Please add some', 'danger')
        else:
            mov = Movement(ts=timestamp,frm=form.src.data,to = form.destination.data,pname=form.mprodname.data,pqty=form.mprodqty.data)
            bal = Balance.query.filter_by(location=form.destination.data,product=form.mprodname.data).update(dict(xfer_date=timestamp, planted_date = t2))
            db.session.add(mov)
            db.session.commit()


#<!-- area caluclations -->

            flash(f'Your plant has been moved!', 'success')

        return redirect(url_for('main.move'))
    return render_template('move.html',form = form,details= details)

def check(frm,to,name,var,qty):
    prod = Product.query.filter_by(variety = var).first()
    locSpace = Location.query.filter_by(loc_name = to).first()

    if frm == to :
        a = 'same'
        return a
    elif frm =='Seed Library' and to != 'Seed Library':
        prodq = Product.query.filter_by(prod_name=name).first()

        if prodq.prod_qty >= qty:
            prodq.prod_qty-= qty
            bal = Balance.query.filter_by(location=to,product=name,var=var).first()
            a=str(bal)
            if(a=='None'):
                Aused = cal_space(locSpace.loc_area,prod.SspaceMin,qty)
                new = Balance(product=name,var=var,location=to,quantity=qty,usedSpace=Aused[0])
                db.session.add(new)
            else:
                bal.quantity += qty
                Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bal.quantity)
                bal = Balance.query.filter_by(location=to,product=name).update(dict(quantity = bal.quantity,usedSpace=Aused[0]))
            db.session.commit()
        else :
            return False
    elif to == 'Seed Library' and frm != 'Seed Library':
        bal = Balance.query.filter_by(location=frm,product=name).first()
        a=str(bal)
        if(a=='None'):
            return 'no prod'
        else:
            if bal.quantity >= qty:
                prodq = Product.query.filter_by(prod_name=name,variety=var).first()
                prodq.prod_qty = prodq.prod_qty + qty
                bal.quantity -= qty
                Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bal.quantity)
                bal = Balance.query.filter_by(location=frm,product=name).update(dict(quantity = bal.quantity,usedSpace=Aused[0]))
                #db.session.commit()
            else :
                 return False

    else: #from='?' and to='?'
        bl = Balance.query.filter_by(location=frm,product=name,var=var).first() #check if from location is in Balance
        a=str(bl)
        if(a=='None'):#if not
            return 'no prod'

        elif (bl.quantity - 1000) > qty:
           #if from qty is sufficiently large, check to  in Balance
            bal = Balance.query.filter_by(location=to,product=name,var=var).first()
            a = str(bal)
            if a=='None':
                #if not add entry
                new = Balance(product=name,var=var,location=to,quantity=qty)
                db.session.add(new)
                bl = Balance.query.filter_by(location=frm,product=name,var=var).first()
                bl.quantity -= qty
                db.session.commit()
            else:#else add to 'from' qty and minus from 'to' qty
                    bal.quantity += qty #if yes,add to to qty
                    bl = Balance.query.filter_by(location=frm,product=name,var=var).first()
                    bl.quantity -= qty
                    Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bl.quantity)
                    bal = Balance.query.filter_by(location=frm,product=name).update(dict(quantity = bl.quantity,usedSpace=Aused[0]))
                    db.session.commit()
        else  :
                 return False

@main.route("/delete")
def delete():
    type = request.args.get('type')
    if type == 'product':
        pid = request.args.get('p_id')
        product = Product.query.filter_by(prod_id=pid).delete()
        db.session.commit()
        flash(f'Your plant data has been deleted!', 'success')
        return redirect(url_for('main.product'))
        return render_template('product.html')
    else:
        pid = request.args.get('p_id')
        loc = Location.query.filter_by(loc_id = pid).delete()
        db.session.commit()
        flash(f'Your location has been deleted!', 'success')
        return redirect(url_for('main.loc'))
        return render_template('loc.html')

@main.route("/datacard", methods = ['GET', 'POST'])

def dataCard():
    l1 = 17
    name = request.args.get('type')
    pid = request.args.get('p_id')
    form = editplantdata()
    pro = db_convert(Product.query.filter_by(prod_id = pid).all())
    pro[3] = pro[3].strip("'")
    frost = db_convert(Weather.query.all())
    #name, variety, DTM, rpinterval, sowtype,
    pi = planting_interval(pro[1],pro[4],pro[5],pro[8],pro[6],frost[2],frost[1])

    if request.method == 'GET':

        return render_template('plantdata.html',plant = name,plantdata = pro, l1 = l1, form = form, pi = pi, frost = frost)

    elif request.method == 'POST' :
        print("c##################################################################################3")

        eh=form.epdhardiness.data
        ep=form.epdplantdate.data
        eg=form.epdgermination.data
        edtm=str(form.epdDTM.data)
        swtp=form.epdsowtype.data
        esd=form.epdseeddepth.data
        esm=form.epdseedspacemin.data
        esx=form.epdseedspacemax.data
        erm=form.epdrowspacemin.data
        erx=form.epdrowspacemax.data
        efc=str(form.epdfamilyCabbage.data)
        efca=str(form.epdfamilyCarrot.data)
        efce=str(form.epdfamilyCelery.data)
        efb=str(form.epdfamilyBean.data)
        efbe=str(form.epdfamilyBeet.data)
        efo=str(form.epdfamilyOnion.data)
        efp=str(form.epdfamilyPea.data)
        efpe=str(form.epdfamilyPepper.data)
        efpo=str(form.epdfamilyPotato.data)
        efs=str(form.epdfamilySquash.data)
        eft=str(form.epdfamilyTomato.data)
                                                     
        po = [pid,'','','',name,edtm,swtp,eg,'',eh,'',ep,esd,esm,esx,erm,erx,efb,efbe,efc,efca,efce,efo,efp,efpe,efpo,efs,eft,'']
        pd = update_sorter(pro,po)

        if form.epdpic.data:# != None or '': 
            picture_file = save_picture(form.epdpic.data)
            
            try:
                p = Product.query.filter_by(prod_id=pid).update(dict(image_file=picture_file))
                flash(f'Plant photo updated!', 'success')
                db.session.commit()
                return redirect(url_for('main.product'))
            except ValueError as e:
                db.session.rollback()
                flash(f' Data Error: {e}','info')
                return redirect(url_for('main.product'))

        try:
            pp = Product.query.filter_by(prod_id=pid).update(dict(DTMat=pd[2],SowType=pd[6],germination = pd[7],\
            RPdate = pd[8], Hardiness = pd[9], Sdepth = pd[12],SspaceMin = pd[13], SspaceMax = pd[14], \
            SrowspaceMin = pd[15], SrowspaceMax = pd[16], CFam_cabbage = pd[17], CFam_carrot = pd[18], \
            CFam_celery = pd[19], CFam_bean = pd[20], CFam_beet = pd[21], CFam_onion = pd[22], CFam_pea = pd[23], \
            CFam_pepper = pd[24], CFam_potato = pd[25], CFam_gourd = pd[26], CFam_tomato = pd[27]))

            db.session.commit()
            flash(f'Plant Data updated!', 'success')
            return redirect(url_for('main.product'))
        except IntegrityError as e:
            db.session.rollback()
            flash(f' Database Error {e}','danger')
            return redirect(url_for('main.product'))

        return render_template('plantdata.html',plant = name,plantdata = pro, l1 = l1, form = form,pi = pi, frost = frost)

    return render_template('plantdata.html',plant = name,plantdata = pro, l1 = l1, form = form, pi = pi, frost = frost)
    

@main.route("/locstat", methods = ['GET', 'POST'])

def locstatCard():
    name = request.args.get('loc')
    pid = request.args.get('p_id')
    bal = Balance.query.filter_by(location=name)
    tspace = float(request.args.get('tspace'))
    plt = Product.query.filter_by(prod_id=pid).first()
    inuse = Balance.query.filter_by(location=name).first()

    if request.method == 'GET':
        if inuse == None:
            gs = (0,3)
            us = tspace
            flash(f' Nothing Planted ','warning')
        else:    
            gs = growth_status(inuse.planted_date,plt.DTMat,plt.germination)    
            us = float("{:.2f}".format(tspace - inuse.usedSpace))
        

        return render_template('locstat.html', b = bal,nam = name, ts = tspace, us = us, gs = gs )


@main.route("/Dashboard", methods = ['GET', 'POST'])
@main.route("/")
def dashboard():
    city = 'Halifax'
    t = datetime.datetime.date(datetime.datetime.today())
    ts = datetime.datetime.strftime(t, '%A %B %d %Y')
    tz = -3
    solday = create_p2(datetime.datetime.today())
    bal = Balance.query.all()
    eone = bool(Location.query.all())
    etwo = bool(Balance.query.all())
    w = Weather.query.filter_by(wid=1).first()
    loc = Location.query.filter_by(loc_id=1).first()

    ffd = datetime.datetime(t.year,montoint(w.FFD[3:6]),int(w.FFD[0:2]))
    sfd = datetime.datetime(t.year,montoint(w.SFD[3:6]),int(w.SFD[0:2]))

    diff = ffd - sfd
    grow_days = ffd - datetime.datetime(t.year,t.month,t.day) 

    if w.called == None:
        Weather.query.filter_by(wid=1).update(dict(called=t))
        astrodata = getastrodata(loc.lat,loc.lon,tz)
        if astrodata[5] == 1:
            astrodata = (w.sun_rise,w.sun_set,w.day_len,w.dwnst,w.dwnsp,tz)
        else:
            pass
        fday = getfrosty(city)
        if fday[2] == 1:
            fday = w.FFD, w.SFD

    elif w.called >= datetime.datetime.today():
        fday = w.FFD, w.SFD
        astrodata = (w.sun_rise,w.sun_set,w.day_len,w.dwnst,w.dwnsp,tz)
    else:
        fday = getfrosty(city)
        if fday[2] == 1:
            fday = w.FFD, w.SFD
        astrodata = getastrodata(loc.lat,loc.lon,tz)
        if astrodata[5] == 1:
            astrodata = (w.sun_rise,w.sun_set,w.day_len,w.dwnst,w.dwnsp,tz)
        else:
            pass

    Weather.query.filter_by(wid=1).update(dict(FFD=fday[0],SFD=fday[1],called=t,sun_rise=astrodata[0],\
        sun_set=astrodata[1],day_len=astrodata[2],dwnst=astrodata[3],dwnsp=astrodata[4]))

    db.session.commit()
    if request.method == 'GET':
            
        if eone and etwo == True:
            var=db_convert(bal)
            Var = var[4].strip("'")
            p_date = var[5].strip("'")
            #print('AAAAAAA',p_date)
            plt = Product.query.filter_by(variety = Var).first()
            gs = growth_status(p_date,plt.DTMat,plt.germination)
        else:
          gs =(0,3)  
       
    return render_template('dashboard.html', ts = ts, plot = solday, bal = bal, gs = gs, fday = fday, \
        grs = grow_days.days, diff = diff.days, astrodata = astrodata)

    
    
    