from flask import Flask, request, render_template, redirect, session, flash, url_for, jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HelloWorld'
client = MongoClient('mongodb://test:test123@ds125423.mlab.com:25423/dynamic_blogging')
db = client['dynamic_blogging']

user = db.user
month = {'1':'Jan','2':'Feb','3':'Mar','4':'Apr','5':'May','6':'Jun','7':'Jul','8':'Aug',
'9':'Sep','10':'Oct','11':'Nov','12':'Dec'}

@app.route('/', methods=['POST','GET'])
def index():
	entertainment = 0
	facts = 0
	movies = 0
	others = 0
	technology = 0
	sports = 0
	find = user.find()
	blogList = []
	for document in find:
		blogList.append(document)
		if document['tag'] == 'Entertainment':
			entertainment += 1
		elif document['tag'] == 'Technology':
			technology += 1
		elif document['tag'] == 'Facts':
			facts += 1
		elif document['tag'] == 'Movies':
			movies += 1
		elif document['tag'] == 'Others':
			others += 1
		elif document['tag'] == 'Sports':
			sports += 1
	tags = {'ent': entertainment, 'tech': technology, 'fact': facts, 'mov': movies, 'oth': others, 'spo': sports}
	search = []
	while blogList:
		search.append(blogList.pop())
	return render_template('index.html' ,user=user, search=search, tags=tags)

@app.route('/admin', methods=['POST','GET'])
def login():
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'test':
			session['username'] = 'admin'
			return redirect(url_for('add'))
		else:
			flash('Invalid Username or Password' , 'danger')
			return render_template('login.html')

	return render_template('login.html')

@app.route("/post/<l>", methods=['POST','GET'])
def post(l):
	document = user.find_one({"title":str(l)})
	return render_template('fullpost.html', document=document)

@app.route('/add_new_post', methods=['POST','GET'])
def add():
	if session['username']:
		var = datetime.date.today()
		date = month[str(var.month)]+" "+str(var.day)+","+str(var.year)
		if request.method == 'POST':
			user =db.user
			user.insert_one({'title':request.form['title'], 
				'content': request.form['content'],
				'date':date,
				'image': request.form['image'],
				'url': request.form['link'],
				'tag': request.form['tag']})
			flash('Added Successfully!' , 'success')
			return render_template('posts.html')

		return render_template('posts.html')

	flash('You must login first !!', 'warning')
	return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session['username'] = None
	return redirect(url_for('login'))

@app.route('/tags/<tag>')
def tags(tag):
	search = user.find()
	doc =[]
	for i in search:
		if i['tag'] == tag:
			doc.append(i)
	return render_template('tags.html', doc=doc)

@app.route('/<d>')
def date(d):
	doc =[]
	search = user.find()
	for i in search:
		if i['date'] == d:
			doc.append(i)
	return render_template('date.html', doc=doc)

@app.route('/search/', methods=['POST','GET'])
def search():
	if request.method == 'POST':
		data = request.form['search']
		a = re.compile(str(request.form['search']), re.IGNORECASE)
		search = user.find()
		doc = []
		for i in search:
			b = a.findall(i['title'])
			for j in b:
				doc.append(i)

		return render_template('tags.html', doc=doc)

	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)
