from flask import Flask, render_template, request, redirect, flash, url_for, session
import MySQLdb
import subprocess

import my_tf_mod
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import os
import sys
import numpy as np
from werkzeug.utils import secure_filename

from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from PIL import Image, ImageFile

IMAGES_FOLDER = ''

app = Flask(__name__)
app.secret_key = "secret key"
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html')


# Admin Login
@app.route("/adminlogin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        uid=request.form["uid"]
        pwd=request.form["pwd"]

        if uid=="Admin" and pwd=="Admin":
            return render_template("adminhome.html")
        else:
            return render_template("adminlogin.html", msg="Your Login attempt was not successful. Please try again!!")
    return render_template("adminlogin.html")



@app.route("/seller", methods=["GET","POST"])
def seller():
    if request.method == "POST":
        db = MySQLdb.connect("localhost", "root", "", "crop")
        c1 = db.cursor()
        sname = request.form["sname"]
        addr = request.form["addr"]
        city = request.form["city"]
        mno = request.form["mno"]
        emailid = request.form["emailid"]
        pwd = request.form["pwd"]
        c1.execute("Select emailid from seller where emailid='%s'" %emailid)
        row=c1.fetchone()
        if (row is not None):
            return render_template("seller.html", msg="UserID Already Inserted!!!")
        else:
            c1.execute("INSERT INTO seller VALUES ('%s','%s','%s','%s','%s','%s')" % (sname, addr, city,mno,emailid,pwd))
            db.commit()
            return render_template("seller.html", msg="Seller Details Submitted!!!")
    return render_template("seller.html")
@app.route("/suggestion", methods=["GET","POST"])
def suggestion():
    if request.method == "POST":
        db = MySQLdb.connect("localhost", "root", "", "crop")
        c1 = db.cursor()
        bname = request.form["bname"]
        sugg = request.form["sug"]
        c1.execute("INSERT INTO sugg VALUES ('%s','%s')" % (bname,sugg))
        db.commit()
        return render_template("suggestion.html", msg="Suggestion Submitted!!!")
    return render_template("suggestion.html")

@app.route("/chat1")
def chat1():
    subprocess.run("python D:\\crop_bid\\chatgui.py")
    return render_template("chat1.html")

@app.route("/chat2")
def chat2():
    subprocess.run("python D:\\crop_bid\\chatgui.py")
    return render_template("chat2.html")

@app.route("/bid",methods=["GET", "POST"])
def bid():
   db=MySQLdb.connect("localhost","root","","crop")
   c1 = db.cursor()

   c1.execute("select * from product where current_bid=0 and cid not in (select cid from predict)")
   data = c1.fetchall()
   return render_template("bid.html", data=data)

@app.route("/bid1", methods=["GET", "POST"])
@app.route("/bid1/<string:sname>/<string:cid>/<string:cname>/<int:bprice>", methods=["GET", "POST"])
def bid1(sname, cid, cname,bprice):
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    bname=session["bname"]
    if request.method == "POST":
        if  request.form["b1"]=="Submit":
            db = MySQLdb.connect("localhost", "root", "", "crop")
            c1 = db.cursor()
            sname = request.form["sname"]
            cid = request.form["cid"]
            cname = request.form["cname"]
            bname = request.form["bname"]
            bprice = int(request.form["bprice"])
            bvalue = int(request.form["bvalue"])
            price=0
            status = ""
            c1.execute("select * from bid where bname='%s' and cid='%s'" % (bname, cid))
            row = c1.fetchone()
            if (row is not None):
                return render_template("bid1.html", msg="UserID Already Inserted!!!")
            else:
                c1.execute("select ifnull(max(reqid),1000)+1 from bid ")
                row = c1.fetchone()
                reqid = row[0]
                c1.execute("INSERT INTO bid VALUES ('%s','%s','%s','%s','%d','%d','%d','%s','%s','%d','%d','%s','%d')" % (
                sname, cid, cname, bname,bprice,bvalue,price,status,'',0,0,'',reqid))
                db.commit()
                return render_template("bid1.html", msg="Bid Details Submitted!!!")

    return render_template("bid1.html",sname=sname, cid=cid, cname=cname,bname=bname,bprice=bprice)

@app.route("/bid2",methods=["GET", "POST"])
def bid2():
   db=MySQLdb.connect("localhost","root","","crop")
   c1 = db.cursor()
   bname=session["bname"]
   c1.execute("select sname,cid,cname,bname,price,lservice,lamt,tamt,ddate from bid where bname in (select bname from predict where bname='%s' and status='not paid')"%(bname))
   data = c1.fetchall()
   return render_template("bid2.html", data=data)

@app.route("/bid3", methods=["GET", "POST"])
@app.route("/bid3/<string:sname>/<string:cid>/<string:cname>/<string:bname>/<int:bprice>/<string:lservice>/<int:lamt>/<int:tamt>/<string:ddate>", methods=["GET", "POST"])
def bid3(sname, cid, cname,bname,bprice,lservice,lamt,tamt,ddate):
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    bname=session["bname"]
    if request.method == "POST":
        if  request.form["b1"]=="Submit":
            db = MySQLdb.connect("localhost", "root", "", "crop")
            c1 = db.cursor()
            cdate = request.form["cdate"]
            sname = request.form["sname"]
            cid = request.form["cid"]
            cname = request.form["cname"]
            bname = request.form["bname"]
            bprice = int(request.form["bprice"])
            cno = request.form["cno"]
            amt = int(request.form["amt"])
            lservice= request.form["lservice"]
            lamt= int(request.form["lamt"])
            tamt = int(request.form["tamt"])
            ddate=request.form["ddate"]
            price=0
            status = ""
            c1.execute("INSERT INTO payment VALUES ('%s','%s','%s','%s','%s','%d','%s','%s','%s','%d','%d','%s')" % (cdate,sname, cid, cname, bname,bprice,cno,amt,lservice,lamt,tamt,ddate))
            db.commit()
            c1.execute("update bid set status='delivered' where cid='%s'"%(cid))
            db.commit()
            c1.execute("update predict set status='paid' where cid='%s'" % (cid))
            db.commit()
            c1.execute("update product set current_bid='%d' where cid='%s'" % (bprice,cid.strip()))
            db.commit()
            return render_template("bid3.html", msg="Payment Details Submitted!!!")

    return render_template("bid3.html",sname=sname, cid=cid, cname=cname,bname=bname,bprice=bprice,lservice=lservice,lamt=lamt,tamt=tamt,ddate=ddate)

@app.route("/bid21",methods=["GET", "POST"])
def bid21():
   db=MySQLdb.connect("localhost","root","","crop")
   c1 = db.cursor()
   #bname=session["bname"]
   #c1.execute("select sname,cid,cname,bname,price from bid where bname='%s'"%(bname))
   c1.execute("select sname,cid,cname,bname,price from bid where bname in (select bname from predict where status='amt predict')" )
   data = c1.fetchall()
   return render_template("bid21.html", data=data)

@app.route("/bid31", methods=["GET", "POST"])
@app.route("/bid31/<string:sname>/<string:cid>/<string:cname>/<string:bname>/<int:bprice>", methods=["GET", "POST"])
def bid31(sname, cid, cname,bname,bprice):
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    #bname=session["bname"]
    if request.method == "POST":
        if  request.form["b1"]=="Submit":
            db = MySQLdb.connect("localhost", "root", "", "crop")
            c1 = db.cursor()
            cdate = request.form["cdate"]
            sname = request.form["sname"]
            cid = request.form["cid"]
            cname = request.form["cname"]
            bname = request.form["bname"]
            bprice = int(request.form["bprice"])
            lservice = request.form["lservice"]
            lamt = int(request.form["lamt"])
            tamt = int(request.form["tamt"])
            ddate = request.form["ddate"]
            price=0
            status = ""
            c1.execute("update bid set lservice='%s',lamt='%d',tamt='%d',ddate='%s' where cid='%s'"%(lservice,lamt,tamt,ddate,cid))
            db.commit()
            c1.execute("update predict set status='not paid' where cid='%s'" % (cid))
            db.commit()
            return render_template("bid31.html", msg="Logistics Details Submitted!!!")

    return render_template("bid31.html",sname=sname, cid=cid, cname=cname,bname=bname,bprice=bprice)

@app.route("/viewproduct")
def viewproduct():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select * from product")
    data = c1.fetchall()
    return render_template("viewproduct.html", data=data)

@app.route("/viewproduct1")
def viewproduct1():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select * from product")
    data = c1.fetchall()
    return render_template("viewproduct1.html", data=data)

@app.route("/viewproduct2")
def viewproduct2():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select * from product")
    data = c1.fetchall()
    return render_template("viewproduct2.html", data=data)



@app.route("/prediction", methods=["GET","POST"])
def prediction():
    sname=session["sname"]
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select cid from product where cid not in (select cid from predict)")
    row = c1.fetchall()
    if request.method == "POST":
        if (request.form["b1"]=="VIEW"):
            cid=request.form["cid"]
            db = MySQLdb.connect("localhost", "root", "", "crop")
            c1 = db.cursor()
            c1.execute("select bvalue, bname from bid where cid='%s' and reqid=(select min(reqid) from bid where cid='%s' and bvalue=(select max(bvalue) from bid where cid='%s'))" %(cid,cid,cid))
            #c1.execute("SELECT MAX(bvalue),bname FROM bid WHERE cid ='%s' )"%(cid))
            highest_bid =c1.fetchone()
            session["bvalue"]=highest_bid[0]
            session["bname"] = highest_bid[1]
            if highest_bid[0] is None:
                print("No bids placed for this crop.")
            else:
                return render_template("prediction.html", bid=highest_bid[0],bname=highest_bid[1],cid1=cid,sname=sname)
        if (request.form["b1"] == "SUBMIT"):
            cid = request.form["cid1"]
            bvalue=session["bvalue"]
            bname=session["bname"]
            c1.execute("INSERT INTO predict VALUES ('%s','%s','%d','%s','%s')" % (sname, cid,bvalue,bname,'amt predict'))
            db.commit()
            c1.execute("update bid set price='%d' where cid='%s'"%(bvalue,cid))
            db.commit()
            return render_template("prediction.html",msg="submitted successfully")
    return render_template("prediction.html",sname=sname,cid=row)

@app.route("/viewsuggestions")
def viewsuggestions():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select * from sugg")
    data = c1.fetchall()
    return render_template("viewsuggestions.html", data=data)

@app.route("/viewsuggestions1")
def viewsuggestions1():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select * from sugg")
    data = c1.fetchall()
    return render_template("viewsuggestions1.html", data=data)

@app.route("/viewpayment")
def viewpayment():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select cdate,sname,cid,cname,bname,price,cno,amt,lservice,lamt,tamt,ddate from payment")
    data = c1.fetchall()
    return render_template("viewpayment.html", data=data)

@app.route("/pay")
def pay():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    bname = session["bname"]
    c1.execute("select cdate,sname,cid,cname,bname,price,cno,amt,lservice,lamt,tamt,ddate from payment where bname='%s'"%(bname))
    data = c1.fetchall()
    return render_template("viewpayment1.html", data=data)

@app.route("/viewpayment2")
def view_payment2():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    sname = session["sname"]
    c1.execute("select cdate,sname,cid,cname,bname,price,cno,amt,lservice,lamt,tamt,ddate from payment where sname='%s'"%(sname))
    data = c1.fetchall()
    return render_template("viewpayment2.html", data=data)

@app.route("/viewbidstatus")
def viewbidstatus():
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("select * from bid where status!='sold'")
    data = c1.fetchall()
    return render_template("viewbidstatus.html", data=data)


@app.route("/sellerlogin", methods=["GET","POST"])
def sellerlogin():
    if request.method == "POST":
        db = MySQLdb.connect("localhost", "root", "", "crop")
        c1 = db.cursor()
        eid=request.form["eid"]
        pwd=request.form["pwd"]
        print(eid,pwd)
        c1.execute("select * from seller where emailid='%s' and pwd='%s'"%(eid,pwd))
        if c1.rowcount>=1:
            row=c1.fetchone()
            session["eid"]=eid
            session["sname"]=row[0]
            return render_template("sellerhome.html")
        else:
            return render_template("sellerlogin.html", msg="Your Login attempt was not successful. Please try again!!")
    return render_template("sellerlogin.html")

# Company Homepage
@app.route("/sellerhome")
def sellerhome():
    return render_template('sellerhome.html')

@app.route("/buyer", methods=["GET","POST"])
def buyer():
    if request.method == "POST":
        db = MySQLdb.connect("localhost", "root", "", "crop")
        c1 = db.cursor()
        bname = request.form["bname"]
        addr = request.form["addr"]
        city = request.form["city"]
        mno = request.form["mno"]
        emailid = request.form["emailid"]
        pwd = request.form["pwd"]
        c1.execute("Select emailid from buyer where emailid='%s'" %emailid)
        row=c1.fetchone()
        if (row is not None):
            return render_template("buyer.html", msg="UserID Already Inserted!!!")
        else:
            c1.execute("INSERT INTO buyer VALUES ('%s','%s','%s','%s','%s','%s')" % (bname, addr, city,mno,emailid,pwd))
            db.commit()
            return render_template("buyer.html", msg="Buyer Details Submitted!!!")
    return render_template("buyer.html")

@app.route("/buyerlogin", methods=["GET","POST"])
def buyerlogin():
    if request.method == "POST":
        db = MySQLdb.connect("localhost", "root", "", "crop")
        c1 = db.cursor()
        eid=request.form["eid"]
        pwd=request.form["pwd"]
        print(eid,pwd)
        c1.execute("select * from buyer where emailid='%s' and pwd='%s'"%(eid,pwd))
        if c1.rowcount>=1:
            row=c1.fetchone()
            session["eid"]=eid
            session["bname"]=row[0]

            return render_template("buyerhome.html")
        else:
            return render_template("buyerlogin.html", msg="Your Login attempt was not successful. Please try again!!")
    return render_template("buyerlogin.html")

# Company Homepage
@app.route("/buyerhome")
def buyerhome():
    return render_template('buyerhome.html')

@app.route("/product", methods=["GET","POST"])
def product():
    sname=session["sname"]
    db = MySQLdb.connect("localhost", "root", "", "crop")
    c1 = db.cursor()
    c1.execute("Select count(*)+1 from product")
    row1 = c1.fetchone()
    r=row1[0]
    if request.method == "POST":
            db = MySQLdb.connect("localhost", "root", "", "crop")
            c1 = db.cursor()
            sname = request.form["sname"]
            cid = request.form["cid"]
            cname = request.form["cname"]
            bprice = int(request.form["bprice"])
            f=request.files["cimage"]
            location =request.form["location"]



            f.save(os.getcwd() + "\\static\\cimage\\" + f.filename)
            cimage = f.filename
            cbid = 0
            c1.execute("select cid from product where cid='%s'" % cid)
            row = c1.fetchone()
            if (row is not None):
                 return render_template("product.html", msg="Crop ID Already Inserted!!!")
            else:
                c1.execute("INSERT INTO product VALUES ('%s','%s','%s','%d','%d','%s','%s')" % (sname, cid, cname, bprice, cbid,cimage,location))
                db.commit()
                return render_template("product.html", msg="Product Details Submitted!!!")


    return render_template("product.html",sname=sname,r=r)

@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET','POST'])
def pred():
    if request.method=='POST':
         f1 = request.files['file']
         session["f"]=f1.filename
         org_img, img= my_tf_mod.preprocess(f1)
         print(f1.filename)
         print(img.shape)
         fruit_dict=my_tf_mod.classify_fruit(img)
         rotten=my_tf_mod.check_rotten(img)

         img_x=BytesIO()
         plt.imshow(org_img/255.0)
         plt.savefig(img_x,format='png')
         plt.close()
         img_x.seek(0)
         plot_url=base64.b64encode(img_x.getvalue()).decode('utf8')

    return render_template('Pred3.html', fruit_dict=fruit_dict, rotten=rotten, plot_url=plot_url)


@app.route("/signout")
def signout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)