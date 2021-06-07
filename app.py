from flask import Flask, json, request
import re
from flask.templating import render_template
import pymongo
from extensions import dbs, uri, collections

client = pymongo.MongoClient(uri)

app = Flask(__name__)

db = client[dbs['user']]
collection = db[collections['github']].find()

# initial conditions when user refreshes
# or lands on the web page for first time
old_top_doc = 0
doc_id = 0

# the loop captures the latest id
# of the document inserted in our db
for doc in collection.sort('_id', pymongo.DESCENDING):
    doc_id = doc['_id']
    break

# The user section
@app.route("/")
def home():
    db = client[dbs['user']]
    collection = db[collections['github']].find()
    for doc in collection.sort('_id', pymongo.DESCENDING):
        old_top_doc = doc['_id']
        break
    return render_template('home.html', old_top = old_top_doc)

# The admin section
@app.route("/admin")
def admin():
    db = client[dbs['user']]
    collection = db[collections['github']].find()
    for doc in collection.sort('_id', pymongo.DESCENDING):
        old_top_doc = doc['_id']
        break
    return render_template('admin.html', old_top = old_top_doc)

# The AJAX gateway
@app.route("/fetch", methods=['POST'])
def fetch():
    old_top_doc = int(request.form['old_top'])
    new_top = 0
    data = []
    db = client[dbs['user']]
    collection = db[collections['github']].find()
    i = 0
    for doc in collection.sort('_id', pymongo.DESCENDING):
        if(old_top_doc<doc['_id']):
            data.append(doc)
        if(i==0):
            new_top = doc['_id']
        i = i + 1
    data.append({'new_top':new_top})
    print(data)
    return json.dumps(data)

# The endpoint
@app.route("/github", methods=['POST'])
def api_mesg():
    global doc_id
    doc_id = doc_id + 1
    if request.headers['Content-Type'] == 'application/json':
        db = client[dbs['user']]
        collection = db[collections['github']]
        l = request.json.keys()
        if('commits' in l):
            data = (request.json)['commits']
            if(len(data)>1):
                merge(data, collection, doc_id)
            else:
                push(data, collection, doc_id)
        else:
            data = (request.json)['pull_request']
            pull(data, collection, doc_id)
            
        return {'data':json.dumps(request.json)}

# Merge Function
def merge(data, collection, doc_id):
    context = {}
    context['author'] = data[0]['author']['username']
    context['action'] = 'merged'
    context['timestamp'] = data[len(data)-1]['timestamp']
    # the regex is used to fetch
    # the branch name which has been merged
    regex = "\\/(.*?)\\\n"
    # we are finding the name of the 'from_branch'
    # and storing it in a list matches
    from_branch = re.findall(regex, data[len(data)-1]['message'])[0]
    context['from_branch'] = from_branch
    context['to_branch'] = request.json['ref'][11:]
    context['_id'] = doc_id
    if(context['author']!='"web-flow"'):
        collection.insert_one(context)
    return

# Push Function
def push(data, collection, doc_id):
    context = {}
    context['author'] = data[0]['committer']['username']
    context['from_branch'] = ''
    context['action'] = 'pushed'
    context['timestamp'] = data[0]['timestamp']
    context['to_branch'] = request.json['ref'][11:]
    context['_id'] = doc_id
    if(context['author']!='"web-flow"'):
        collection.insert_one(context)
    return

# Pull Function
def pull(data, collection, doc_id):
    context = {}
    context['author'] = data['user']['login']
    context['from_branch'] = data['head']['ref']
    context['to_branch'] = data['base']['ref']
    context['timestamp'] = data['created_at']
    context['_id'] = doc_id
    if((request.json)['action']=='opened'):
        context['action'] = 'pull-request'
        collection.insert_one(context)
    return