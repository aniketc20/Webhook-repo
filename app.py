from flask import Flask, json, request
import re
from flask.templating import render_template
import pymongo
from extensions import dbs, uri, collections

client = pymongo.MongoClient(uri)

app = Flask(__name__)

@app.route("/")
def home():
    db = client[dbs['user']]
    #fetches all data from database
    collection = db[collections['github']].find()
    l = []
    for data in collection:
        l.append(data)
    return render_template('home.html', data=l)

@app.route("/github", methods=['POST'])
def api_mesg():
    if request.headers['Content-Type'] == 'application/json':
        db = client[dbs['user']]
        collection = db[collections['github']]
        context = {}
        l = request.json.keys()
        if('commits' in l):
            author = (request.json)['commits']
            # The if condition is for merge action. 
            # Push actions have a list length of 1 while merge actions have length>1
            if(len((request.json)['commits'])>1):
                context['author'] = '"'+ author[0]['author']['username'] +'"' # storing the name of the author who has merged
                context['action'] = ' merged branch '

                # the regex is used to fetch the branch name which has been merged
                regex = "\\/(.*?)\\\n"
                # we are finding the name of the 'from_branch' and storing it in an array matches
                matches = re.findall(regex, (request.json)['commits'][1]['message'])

                context['from_branch'] = '"'+ matches[0] +'" to '
            else:
                context['author'] = '"'+ author[0]['committer']['username'] +'"' # storing the name of the author who has committed
                context['action'] = ' pushed to '
            context['to_branch'] = '"'+ request.json['ref'][11:] +'" on ' # storing the branch where we have pushed
            context['time'] = request.json['repository']['updated_at']
            # this condition is to avoid saving of data while creating a new branch.
            if(context['author']!='"web-flow"'):
                # inserts data into our database
                collection.insert_one(context)
        else:
            # below code is for PULL-REQUESTS here context is a dictionary
            context['author'] = '"'+ (request.json)['pull_request']['user']['login'] +'"'
            context['action'] = (request.json)['action'] + ' a pull request from '
            context['from_branch'] = '"'+ (request.json)['pull_request']['head']['ref'] +'" to '
            context['to_branch'] = '"'+ (request.json)['pull_request']['head']['repo']['default_branch'] + '" on '
            context['time'] = (request.json)['pull_request']['head']['repo']['created_at']
            # we are only storing newly opened pull-requests. 
            # reopened or deleted pull-requests are ignored.
            if(context['action']=='opened a pull request from '):
                collection.insert_one(context)
        return {'data':json.dumps(request.json)}

