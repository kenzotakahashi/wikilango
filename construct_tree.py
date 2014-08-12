nodes = [
{"id": 1, "body": 'Hello.', "parent": None},
{"id": 2, "body": 'How are you?', "parent": 1},
{"id": 6, "body": "I'm fine.", "parent": 2},
{"id": 7, "body": "That's great.", "parent": 6},
{"id": 3, "body": 'Hi there.', "parent": 1},
{"id": 4, "body": "How's it going?", "parent": 3},
{"id": 5, "body": "I'm pretty good.", "parent": 4}
]




# result = \
# {'children': [
#     {'body': 'Hello.', 'id': 1, 'parent': None, 'children': [
#         {'body': 'How are you?', 'id': 2, 'parent': 1, 'children': [
#             {'body': "I'm fine.", 'id': 6, 'parent': 2, 'children': [
#                 {'body': "That's great.", 'id': 7, 'parent': 6, 'children': []}
#             ]}
#         ]},
#         {'body': 'Hi there.', 'id': 3, 'parent': 1, 'children': [
#             {'body': "How's it going?", 'id': 4, 'parent': 3, 'children': [
#                 {'body': "I'm pretty good.", 'id': 5, 'parent': 4, 'children': []}
#             ]}
#         ]}
#     ]}
# ]}

{'body': 'Hello.', 'id': 1, 'parent': None, 'children': [
    {'body': 'How are you?', 'id': 2, 'parent': 1, 'children': [
        {'body': "I'm fine.", 'id': 6, 'parent': 2, 'children': [
            {'body': "That's great.", 'id': 7, 'parent': 6, 'children': []}
        ]}
    ]}, 
    {'body': 'Hi there.', 'id': 3, 'parent': 1, 'children': [
        {'body': "How's it going?", 'id': 4, 'parent': 3, 'children': [
            {'body': "I'm pretty good.", 'id': 5, 'parent': 4, 'children': []}
        ]}
    ]}
]}



# i = ObjectId('53d526d5705bd6867a5b41d1')

# a = db.utterances.insert({'topic': i, "body": 'Hello.', "parent": None})
# b = db.utterances.insert({'topic': i, "body": 'How are you?', "parent": a})
# c = db.utterances.insert({'topic': i, "body": "I'm fine.", "parent": b})
# d = db.utterances.insert({'topic': i, "body": "That's great.", "parent": c})
# e = db.utterances.insert({'topic': i, "body": 'Hi there.', "parent": a})
# f = db.utterances.insert({'topic': i, "body": "How's it going?", "parent": e})
# g = db.utterances.insert({'topic': i, "body": "I'm pretty good.", "parent": f})


t = db.topics.insert({'name': 'Weather'})
i = ObjectId('53dccbb8705bd6c625f2db9c')

a = db.utterances.insert({'topic': i, "body": "It's such a nice day.", "parent": None})
b = db.utterances.insert({'topic': i, "body": "Yes, it is.", "parent": a})
c = db.utterances.insert({'topic': i, "body": "It looks like it may rain soon.", "parent": b})
d = db.utterances.insert({'topic': i, "body": "Hopefully it will.", "parent": c})
e = db.utterances.insert({'topic': i, "body": "Really? It's too hot.", "parent": a})
f = db.utterances.insert({'topic': i, "body": "I'd rather be hot than cold.", "parent": e})
g = db.utterances.insert({'topic': i, "body": "I hope that it doesn't rain", "parent": c})
h = db.utterances.insert({'topic': i, "body": "", "parent": })
i = db.utterances.insert({'topic': i, "body": "", "parent": })
j = db.utterances.insert({'topic': i, "body": "", "parent": })


