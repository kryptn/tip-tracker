from flask import Flask, session, render_template, redirect, url_for, request
from hashlib import sha224
import time
import json

app = Flask(__name__)
app.secret_key = 'abcd'

userdata = 'userdata.txt'
flatfile = 'flatfile.txt'

def getusers(user, pword):
   """
   compares given data with stored data 
   if user isn't found, make a new one.

   """

   with open(userdata, 'r') as f:
      userlist = json.loads(f.read())
   
   if user in userlist.keys():
      if userlist[user] != pword:
         return False
   else:
      userlist[user] = pword
      with open(userdata, 'w') as f:
         f.write(json.dumps(userlist))
   
   return True

@app.template_filter('pretty')
def number_filter(s):
   return '%.02f' % s

@app.route('/')
@app.route('/'+)
def index(error=None, args={}):
   tips = None
   if 'tips' in session:
      tips = session['tips']
   
   return render_template('index.html', error=error, tips=tips)

@app.route('/tips', methods=['GET','POST'])
def tips():
   if session['authed'] and session['clocked']:
      if request.form['amount']:
         try:
            amount = float(request.form['amount'])
            ttime = time.localtime()
            session['tips'] += [{'amount':amount,'time':ttime}]
         except:
            pass

   return redirect(url_for('index'))

@app.route('/clock')
def clock():
   if session['authed']:
      if not session['clocked']:
         session['clocked'] = True
         session['in'] = time.localtime()
      else:
         session['clocked'] = False
         time_in = session.pop('in')

         data = dict()
         tips = session['tips']
         data['deliveries'] = len(session['tips'])
         data['gas'] = data['deliveries'] * 1.25
         data['tips'] = sum([x['amount'] for x in session['tips']])
         data['bag_total'] = data['tips'] + 20.00
         data['owe'] = 20.00 - data['gas']
         data['take_home'] = data['bag_total'] - data['owe']
         session['tips'] = list()
         return render_template('clock.html', **data)
   
   return redirect(url_for('index'))


@app.route('/login', methods=['POST','GET'])
def login():
   if request.method == 'POST':
      user = request.form['user']
      pword = sha224(user+request.form['pass']).hexdigest()

      result = getusers(user, pword)
      if result:
         session['authed'] = True
         session['clocked'] = False
         session['tips'] = list()
         session['user'] = user
   
   return redirect(url_for('index'))

@app.route('/logout')
def logout():
   """ no real point, i don't clear any other info """
   session['authed'] = False
   return redirect(url_for('index'))

@app.route('/clear')
def clear():
   """ lol debuggign """
   session['authed'] = False
   session['clocked'] = False
   session['tips'] = None
   session['user'] = None
   session['True'] = True
   return redirect(url_for('index'))

if __name__ == '__main__':
   app.run('0.0.0.0', debug=True)