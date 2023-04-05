#
#   things to do:
#   mail notifications
#   Have a history section
#   print garden reports - in progress
#   users  
#       user space and gardens
#       user admin section
#   xfer buttons on green house & nursery
#   select plant populate pull downs
#   --fix plant date, transfer date only sets planted date from seed library or nursery
#   --Overview badges - show correct status
#
from flask import  render_template,url_for,redirect,flash,request,jsonify, Blueprint,Response
from flaskinventory import current_app,db
from flaskinventory.main.forms import addproduct,addlocation,moveproduct,editproduct,editlocation,editplantdata, archivedata
from flaskinventory.models import Location,Product,archive,Movement,Balance,Weather
from flaskinventory.main.utils import pdf_template,stripper,save_picture, cal_space, create_p2, planting_interval,growth_status,db_convert,getfrosty,montoint,getastrodata,str2bool,update_sorter
import time,datetime
from sqlalchemy.exc import IntegrityError
import re
import fpdf

main = Blueprint('main', __name__)

@main.route("/Overview")
def overview():
    balance = Balance.query.all()
    # location = Location.query.all()
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

    bal_loc = []
    form = addlocation()
    lform = editlocation()
    aform = archivedata()
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
        try:
            Balance.query.filter_by(location=locname).update(dict(location=lform.editlocname.data))
            Movement.query.filter_by(frm=locname).update(dict(frm=lform.editlocname.data))
            Movement.query.filter_by(to=locname).update(dict(to=lform.editlocname.data))
        except sqlite3.OperationalError:
            db.session.rollback()
            Balance.query.filter_by(location=locname).update(dict(location=lform.editlocname.data))
            Movement.query.filter_by(frm=locname).update(dict(frm=lform.editlocname.data))
            Movement.query.filter_by(to=locname).update(dict(to=lform.editlocname.data))
            db.session.commit()
        try:
            db.session.commit()
            flash(f'Your location has been updated!', 'success')
            return redirect(url_for('main.loc'))
        except IntegrityError :
            db.session.rollback()
            flash(f'This location already exists','danger')
            return redirect('/Location')

    elif form.validate_on_submit() :
        locname = request.form.get("locname","")
        locarea = request.form.get("locarea","")

        loc = Location(loc_name=locname,loc_area=locarea,lat=0.0,lon=0.0)
        db.session.add(loc)
        try:
            db.session.commit()
            flash(f'Your location {form.locname.data} has been added!', 'success')
            return redirect(url_for('main.loc'))
        except IntegrityError :
            db.session.rollback()
            flash(f'This location already exists','danger')
            return redirect('/Location')
########## archival spot #########
    elif aform.validate_on_submit() :
        #for each garden location combine inventory 
        timestamp = datetime.datetime.now()
        t2 = timestamp.strftime("%Y")

        inv = stripper(Balance.query.with_entities(Balance.bid).all())
        # print(inv)
        for z in range(len(inv)):
            bal_loc.append(stripper(db_convert(Balance.query.filter_by(bid = inv[z]).first())))
        # print(bal_loc)
        for h in range(len(bal_loc)):
            arch = archive(location=bal_loc[h][2],product=bal_loc[h][1],var=bal_loc[h][4], \
                quantity=bal_loc[h][3],planted_date=bal_loc[h][5],planted_year=t2, xfer_date=timestamp)
        # print(arch)
            db.session.add(arch)
        Balance.query.delete()
        Movement.query.delete()
        db.session.commit()
        flash(f'Garden Inventories sent to Archive','info')
    return render_template('loc.html',lform=lform,form=form,aform=aform,details=details)   
    

# local = stripper(Location.query.with_entities(Location.loc_name).all())

#         for z in range(len(local)):
#             #check if anything in location
#             if bool(Balance.query.filter_by(location = local[z]).all()):
#                 u.append(local[z])
#             else:
#                 print('nothing in location')
#         # print(u)
#         ''' do loop for each bal location '''

#         for i in range(len(u)):
#             # print('UU',u[i], i)
#             # print(Balance.query.filter_by(location = u[i]).all())
#             bal_loc.append(stripper(db_convert(Balance.query.filter_by(location = u[i]).all())))
#         # print(bal_loc)

#         for h in range(len(bal_loc)):
#             # print(bal_loc)
#             arch = archive(location=bal_loc[h][2],product=bal_loc[h][1],var=bal_loc[h][4], \
#                 quantity=bal_loc[h][3],planted_date=bal_loc[h][5],planted_year=t2, xfer_date=timestamp)
#             print(arch)
#             # db.session.add(arch)

        
        # db.session.commit()



    



@main.route("/Transfers", methods = ['GET', 'POST'])
def move():
    form = moveproduct()

    details = Movement.query.all()
    pdetails = Product.query.all()
    exists = bool(Movement.query.all())
    if exists== False and request.method == 'GET' :
            flash(f'Change Plant location','info')
    #----------------------------------------------------------
    prod_choices = Product.query.with_entities(Product.prod_name).all()
    variety_choice = Product.query.with_entities(Product.variety).all()
    loc_choices = Location.query.with_entities(Location.loc_name,Location.loc_name).all()
    #remove duplicates
    prod_list_names = []
    [prod_list_names.append(x) for x in prod_choices if x not in prod_list_names]
    var_list_names = []
    [var_list_names.append(z) for z in variety_choice if z not in var_list_names]

    src_list_names,dest_list_names=[('Seed Library','Seed Library')],[('Seed Library','Seed Library')]
    src_list_names+=loc_choices
    dest_list_names+=loc_choices
    #passing list_names to the form for select field
    form.mprodname.choices = stripper(prod_list_names)
    form.mprodvar.choices = stripper(var_list_names)
    form.src.choices = src_list_names
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
    t2 = timestamp.strftime("%d %b")

    try:
        if frm == to :
            a = 'same'
            return a

        elif frm =='Seed Library' and (to != 'Seed Library' or to != 'Nursery'):
            prodq = Product.query.filter_by(prod_name=name).first()
            if prodq.prod_qty >= qty:
                prodq.prod_qty-= qty
                bal = Balance.query.filter_by(location=to,product=name,var=var).first()
                a=str(bal)
                if(a=='None'):
                    Aused = cal_space(locSpace.loc_area,prod.SspaceMin,qty)
                    # print('new out',Aused)
                    new = Balance(product=name,var=var,location=to,quantity=qty,usedSpace=Aused[0],availSpace=Aused[1])
                    db.session.add(new)
                    db.session.commit()
                else:
                    bal.quantity += qty
                    Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bal.quantity)
                    # print('old out',Aused)
                    bal = Balance.query.filter_by(location=to,product=name).update(dict(quantity = bal.quantity,usedSpace=Aused[0],availSpace=Aused[1]))
                    db.session.commit()
            else:
                return False

        elif frm =='Seed Library' and to == 'Compost':
            prodq = Product.query.filter_by(prod_name=name).first()
            if prodq.prod_qty >= qty:
                prodq.prod_qty-= qty
                bal = Balance.query.filter_by(location=to,product=name,var=var).first()
                a=str(bal)
                if(a=='None'):
                    # Aused = cal_space(locSpace.loc_area,prod.SspaceMin,qty)
                    # print('new out',Aused)
                    new = Balance(product=name,var=var,location=to,quantity=qty,usedSpace=0.0,availSpace=0.0, planted_date = t2)
                    db.session.add(new)
                    db.session.commit()
                else:
                    bal.quantity += qty
                    # Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bal.quantity)
                    # print('old out',Aused)
                    bal = Balance.query.filter_by(location=to,product=name).update(dict(quantity = bal.quantity,usedSpace=0.0,availSpace=0.0,planted_date = bal.planted_date))
                    db.session.commit()


        elif frm =='Seed Library' and to == 'Nursery':
            prodq = Product.query.filter_by(prod_name=name).first()
            if prodq.prod_qty >= qty:
                prodq.prod_qty-= qty
                bal = Balance.query.filter_by(location=to,product=name,var=var).first()
                a=str(bal)
                if(a=='None'):
                    # Aused = cal_space(locSpace.loc_area,prod.SspaceMin,qty)
                    # print('new out',Aused)
                    new = Balance(product=name,var=var,location=to,quantity=qty,usedSpace=0.0,availSpace=0.0, planted_date = t2)
                    db.session.add(new)
                    db.session.commit()
                else:
                    bal.quantity += qty
                    # Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bal.quantity)
                    # print('old out',Aused)
                    bal = Balance.query.filter_by(location=to,product=name).update(dict(quantity = bal.quantity,usedSpace=0.0,availSpace=0.0,planted_date = bal.planted_date))
                    db.session.commit()
            else:
                return False


        # elif to == 'Seed Library' and frm != 'Seed Library':
        #     bal = Balance.query.filter_by(location=frm,product=name).first()
        #     a=str(bal)
        #     if(a=='None'):
        #         return 'no prod'
        #     else:
        #         if bal.quantity >= qty:
        #             prodq = Product.query.filter_by(prod_name=name,variety=var).first()
        #             prodq.prod_qty = prodq.prod_qty + qty
        #             bal.quantity -= qty
        #             Aused = cal_space(locSpace.loc_area,prod.SspaceMin,bal.quantity)
        #             # print('bal out',Aused)
        #             bal = Balance.query.filter_by(location=frm,product=name).update(dict(quantity = bal.quantity,usedSpace=Aused[0],availSpace=Aused[1]))
        #             db.session.commit()
        #         else:
        #             return False

        elif frm =='Nursery' and to != 'Seed Library':
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
                    # print('bal out',Aused)
                    bal = Balance.query.filter_by(location=frm,product=name).update(dict(quantity = bal.quantity,usedSpace=Aused[0],availSpace=Aused[1],planted_date = bal.planted_date))
                    db.session.commit()
                else:
                    return False

        else: #from='?' and to='?'
            bl = Balance.query.filter_by(location=frm,product=name,var=var).first() #check if from location is in Balance
            a=str(bl)

            if(a=='None'):#if not
                return 'no prod'

            elif bl.quantity >= qty:
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

                        bal = Balance.query.filter_by(location=frm,product=name).update(dict(quantity = bl.quantity,usedSpace=Aused[0],availSpace=Aused[1]))
                        db.session.commit()
            else:
                return False

    except AttributeError:
        flash(f'Plant not in Library', 'Warning')
        return redirect(url_for('main.move'))

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
        efc=str(form.epdfamilyBrassica.data)
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
            SrowspaceMin = pd[15], SrowspaceMax = pd[16], CFam_brassica = pd[17], CFam_carrot = pd[18], \
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
    # pid = request.args.get('p_id')
    bal = Balance.query.filter_by(location=name)
    tspace = float(request.args.get('tspace'))
    plt = []
    dat = Balance.query.filter_by(location=name).first()
    used = Balance.query.filter_by(location=name).all()
    u = []
    u2 = []
    u3 = []
    gs = []
    g2 = []
    inuse = 0.0

    for z in range(len(used)):
        u.append(stripper(db_convert(used[z])))

    for i in range(len(u)):
        print(u[i][4],'/n')
        print(Product.query.filter_by(variety=u[i][4]).first())
        inuse += float(u[i][6]) 
        gs.append(u[i][5])#planted date
        u3.append(stripper(db_convert(Product.query.filter_by(variety=u[i][4]).first())))
        plt.append(int(u3[i][5]))#DTM
        u2.append(int(u3[i][7]))#Germ time
        g2.append(growth_status(gs[i],plt[i],u2[i]))

    if request.method == 'GET':

        if dat == None:
            gs = (0,3)
            us = tspace
            flash(f' Nothing Planted ','warning')

        else:     
            us = float("{:.2f}".format(tspace - inuse))

        return render_template('locstat.html', b = bal,nam = name, ts = tspace, us = us, gs = g2 )


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
    if grow_days.days <0:
        ggrs = 0
    else:
        ggrs = grow_days.days

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
        grs = ggrs, diff = diff.days, astrodata = astrodata)
##########################################################################
@main.route("/Reports")
def reports():
    

    return render_template('test.html')
    
@main.route("/Reports/pdf")#plant library
def pdf(): 
    library = Product.query.all()
    pdf = pdf_template(0,library)
    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=report.pdf'})

@main.route("/Reports/pdf1",methods = ['GET', 'POST'])
def pdf1(): 
    pdf1 = pdf_template(1,1)
    return Response(pdf1.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=report1.pdf'})

@main.route("/Reports/pdf2",methods = ['GET', 'POST'])
def pdf2(): 
    pdf2 = pdf_template(2,1)
    return Response(pdf2.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=report2.pdf'})

@main.route("/Reports/pdf3",methods = ['GET', 'POST'])# hystorical
def pdf3(): 

        # inv = stripper(Balance.query.with_entities(Balance.bid).all())
        # # print(inv)
        # for z in range(len(inv)):
        #     bal_loc.append(stripper(db_convert(Balance.query.filter_by(bid = inv[z]).first())))

    pdf3 = pdf_template(3,1)
    return Response(pdf3.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=report3.pdf'})
###############################################################################################################

@main.route("/Archive", methods = ['GET', 'POST'])
def arch():
    ## year buttons
    bal = archive.query.all()
    exists = bool(archive.query.all())
    
    if exists== False :
        flash(f'Nothing to archive', 'info')

    return render_template('arch.html' ,balance=bal)




