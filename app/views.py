from app import app, db
from flask import send_file, jsonify, abort, request, _request_ctx_stack
from bson.objectid import ObjectId
from functools import wraps
from werkzeug.local import LocalProxy
from flask.ext.cors import cross_origin

import jwt, base64, os, re, random

fin = open('.secret', 'r')
CLIENT_ID = fin.readline()[0:-1]
CLIENT_SECRET = fin.readline()[0:-1]

# Authentication annotation
current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)


# ==================== Authentication ====================================


def authenticate(error):
  resp = jsonify(error)
  resp.status_code = 401
  return resp

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
    elif len(parts) == 1:
      return {'code': 'invalid_header', 'description': 'Token not found'}
    elif len(parts) > 2:
      return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}

    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            base64.b64decode(CLIENT_SECRET.replace("_","/").replace("-","+"))
        )
    except jwt.ExpiredSignature:
        return authenticate({'code': 'token_expired', 'description': 'token is expired'})
    except jwt.DecodeError:
        return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})

    if payload['aud'] != CLIENT_ID:
      return authenticate({'code': 'invalid_audience', 'description': 'the audience does not match. expected: '+CLIENT_ID})

    _request_ctx_stack.top.current_user = user = payload
    return f(*args, **kwargs)

  return decorated


# ===============================================================================


# ================== chat ========================

# The format of chat 
# {
# 	_id = ObjectId(fdsfasfasdfasfsaf)
# 	user = ObjectId(jrjgrjrgrgnr)
# 	user_phrases = [{'_id': 'id1'}, {'_id': 'id3'}]
# 	ai_phrases = [{'_id': 'id2'}, {'_id': 'id4'}]
# 	root = ObjectId(fdfdsffd)
# }

@app.route('/api/v1.0/startchat/<topic_id>', methods=['POST'])
@requires_auth
def startChat(topic_id):
	# 0 -> AI goes first 1 -> user goes first
	turn = request.json['turn']
	language = db.topics.find_one({'_id': ObjectId(topic_id)})['language']
	root = db.utterances.find_one({'topic': ObjectId(topic_id), 'parent': None})

	children = map(encodeUtterance, list(db.utterances.find({'parent': root['_id']})))
	# If the tree root does not have any children, do not allow chat.
	if len(children) == 0:
		return jsonify({'ai_response': 'too short'})

	chatId = db.chat.insert({'user': current_user['sub'], 'user_phrases': [], 'ai_phrases': [],
							'root': root['_id'], 'language': language})
	if turn == 0:
		# print children
		chat = db.chat.find_one({'_id': chatId})
		db.chat.update({"_id": chatId}, {"$push": {"ai_phrases": {'_id': root['_id']}}})
		ai_response = root['body']
	else:
		children = [encodeUtterance(root)]
		ai_response = None

	return jsonify({'id': str(chatId), 'ai_response': ai_response, 'choices': children, 'language': language})


@app.route('/api/v1.0/chat/<chat_id>', methods=['POST'])
@requires_auth
def chat(chat_id):
	userResponse = request.json['userResponse']
	chat = db.chat.find_one({'_id': ObjectId(chat_id)})

	if len(chat['ai_phrases']) == 0: # user went first
		root = db.utterances.find_one({'_id': chat['root']})
		matched = match([root], userResponse)
	else:
		children = list(db.utterances.find({'parent': chat['ai_phrases'][-1]['_id']}))
		matched = match(children, userResponse)
	return processChat(matched, chat)
			
def processChat(matched, chat):
	log, ai_response, choices = "Working", None, None
	if matched:
		db.chat.update({"_id": chat['_id']}, {"$push": {"user_phrases": {'_id': matched['_id']}}})
		# TODO: remove list if it works without it
		ai_choices = list(db.utterances.find({'parent': matched['_id']}))
		if ai_choices:
			ai_response = ai_choices[random.randint(0, len(ai_choices) -1)]
			db.chat.update({"_id": chat['_id']}, {"$push": {"ai_phrases": {'_id': ai_response['_id']}}})
			choices = map(encodeUtterance, list(db.utterances.find({'parent': ai_response['_id']})))
			ai_response = ai_response['body']
			if not choices:
				log = "End by AI"
		else:
			log = "End by User"
	else:
		log = "Try again"
		# ai_response = "Say again?"
		ai_response = db.utilityPhrases.find_one({'intent': 'repeat', 'language': chat['language']})['body']

	return jsonify({'ai_response': ai_response, 'choices': choices, 'log': log})

def match(utterances, userResponse):
	userResponse = userResponse.lower()
	for u in utterances:
		# print re.sub(r'([\?\.!,])', '', u['body'].lower())
		# print userResponse
		if re.sub(r'([\?\.!,])', '', u['body'].lower()) == userResponse:
			return u
	return False



# ========================================================================


@app.route('/')
def index():
	# Initial Load
    return send_file("templates/index.html")

@app.route('/api/v1.0/topics', methods = ['GET'])
def get_topics():
	topics = map(encodeTopic, list(db.topics.find()))
	return jsonify({"topics": topics})

"""
schema of topic
{
	'name': 'greeting',
	'language': 'en-US'
}
"""

@app.route('/api/v1.0/topics', methods = ['POST'])
@requires_auth
def createTopic():
	topic = {
		'name': request.json['name'],
		'language': request.json['language']
	}
	topicId = db.topics.insert(topic)
	topicEncoded = encodeTopic(db.topics.find_one({'_id': topicId}))

	return jsonify({'topic': topicEncoded})


@app.route('/api/v1.0/topics/<topic_id>', methods = ['GET'])
@requires_auth
def get_tree(topic_id):
	# TODO: refactor. you dont need this line
	topic = db.topics.find_one({'_id': ObjectId(topic_id)})
	utterances = map(encodeUtterance, list(db.utterances.find({'topic': topic['_id']})))
	user = encode(db.users.find_one({'auth': current_user['sub']}))

	# print utterances

	tree = build_tree(utterances)
	# print tree
	return jsonify({'tree': tree, 'user': user})

@app.route('/api/v1.0/utterance', methods = ['POST'])
@requires_auth
def createUtterance():
	topic = ObjectId(request.json['topic'])
	parent = None if request.json['parent'] == None else ObjectId(request.json['parent'])
	utterance = {
		'body': request.json['body'],
		'user': db.users.find_one({'auth': current_user['sub']})['_id'],
		'parent': parent,
		'topic': topic,
		'collapsed': False
	}
	# print utterance
	newId = db.utterances.insert(decodeUtterance(utterance))

	utterances = map(encodeUtterance, list(db.utterances.find({'topic': topic})))
	tree = build_tree(utterances)
	# u = db.utterances.find_one({'_id': newId})
	# u['children'] = []
	# print u

	return jsonify({'tree': tree}), 201

"""
utilityPhrases
{
	'body': 'Say Again?',
	'language': 'en-US',
	'intent': 'repeat'
}
"""


@app.route('/api/v1.0/utterance/<utterance_id>', methods=['PUT'])
@requires_auth
def editUtterance(utterance_id):
	topic = db.utterances.find_one({'_id': ObjectId(utterance_id)})['topic']
	status = db.utterances.update({'_id': ObjectId(utterance_id)},{"$set": {"body": request.json['body']}})
	if status['ok'] != 1:
		print status

	utterances = map(encodeUtterance, list(db.utterances.find({'topic': topic})))
	tree = build_tree(utterances)
	return jsonify({'tree': tree})


@app.route('/api/v1.0/utterance/<utterance_id>', methods=['DELETE'])
@requires_auth
def deleteUtterance(utterance_id):
	topic = db.utterances.find_one({'_id': ObjectId(utterance_id)})['topic']
	status = db.utterances.remove({'_id': ObjectId(utterance_id)})
	if status['ok'] != 1:
		print status

	utterances = map(encodeUtterance, list(db.utterances.find({'topic': topic})))
	tree = build_tree(utterances)
	return jsonify({'tree': tree})


#======================= User ==========================================
"""
Users schema
{
	_id: '',
	auth: '',
	username: '',
	language: {
		'name': 'English',
		'code': 'en-US'
	}
}
"""


@app.route('/api/v1.0/signup', methods=['POST'])
@requires_auth
def signup():
	"""called every time a user login. If the user data does not exist, create one."""
	user = db.users.find_one({'auth': current_user['sub']})
	if user:
		return jsonify({'user': encode(user)})
	user = {
		'auth': current_user['sub'],
		'username': request.json['username'],
		# 'language': {
		# 	'name': 'English',
		# 	'code': 'en-US'
		# }
	}
	userId = db.users.insert(user)
	user = encode(db.users.find_one({'_id': userId}))
	return jsonify({'user': user})


@app.route('/api/v1.0/user/<user_id>', methods=['GET'])
@requires_auth
def getUser(user_id):
	user = encode(db.users.find_one({'_id': ObjectId(user_id)}))
	return jsonify(user)

@app.route('/api/v1.0/user/current', methods=['GET'])
@requires_auth
def getCurrentUser():
	user = encode(db.users.find_one({'auth': current_user['sub']}))
	return jsonify(user)

@app.route('/api/v1.0/settings', methods=['POST'])
@requires_auth
def settings():
	status = db.users.update({'auth': current_user['sub']},{"$set": {
		"username": request.json['username'],
		# "language": request.json['language']
	}})
	user = encode(db.users.find_one({'auth': current_user['sub']}))
	if status['ok'] != 1:
		print status
	return jsonify(user)

# ============== utility functions =====================================

def getLanguage():
	# Get the user's language 
	return db.users.find_one({'auth': current_user['sub']})['language']['code']

def encode(obj):
	# convert id ro string 
	obj['_id'] = str(obj['_id'])
	return obj

def encodeTopic(obj):
	# Add count to topic
	count = db.utterances.find({'topic': obj['_id']}).count()
	obj['_id'] = str(obj['_id'])
	obj['count'] = count
	return obj 

def encodeUtterance(obj):
	obj['_id'] = str(obj['_id'])
	obj['topic'] = str(obj['topic'])
	obj['parent'] = str(obj['parent']) if obj['parent'] != None else None
	obj['username'] = db.users.find_one({'_id': obj['user']})['username']
	obj['user'] = str(obj['user'])
	return obj

def decodeUtterance(obj):
	obj['topic'] = ObjectId(obj['topic'])
	obj['parent'] = ObjectId(obj['parent']) if obj['parent'] != None else None
	return obj

def build_tree(nodes):
    # create empty tree to fill
    tree = None
    for node in nodes:
        if node['parent'] == None:
            tree = node
            break
    if tree == None:
    	return None
    # fill in tree starting with roots (those with no parent)
    build_tree_recursive(tree, tree['_id'], nodes)
    return tree

def build_tree_recursive(tree, parent, nodes):
    # find children
    children  = [n for n in nodes if n['parent'] == parent]
    
    tree['children'] = []
    # build a subtree for each child
    for child in children:
    	# start new subtree
        tree['children'].append(child)
    	# call recursively to build a subtree for current node
    	build_tree_recursive(child, child['_id'], nodes)

