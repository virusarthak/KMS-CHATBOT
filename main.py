import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer=LancasterStemmer()

import numpy
import tflearn 
import tensorflow
import random
import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

from flask import Flask, render_template, request, jsonify

...

@app.route('/chat', methods=['POST'])
def chat():
    input_text = request.json['input']
    results = model.predict([bag_of_words(input_text, words)])[0]
    results_index = numpy.argmax(results)
    tag = labels[results_index]
    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']
    output_text = random.choice(responses)
    return jsonify({'output': output_text})

if __name__ == '__main__':
    app.run(debug=True)


with open("intents.json") as file:
    data=json.load(file)

words=[]
labels=[]
docs_x=[]
docs_y=[]
 

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        wrds=nltk.word_tokenize(pattern)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent["tag"])

    if intent["tag"] not in labels:
        labels.append(intent["tag"])    

words=[stemmer.stem(w.lower()) for w in words if w !="?"]
words=sorted(list(set(words))) 

labels=sorted(labels)

training=[]
output=[]

out_empty=[0 for _ in range(len(labels))]

for x,doc in enumerate(docs_x):
    bag=[]

    wrds=[stemmer.stem(w.lower()) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)

    output_row=out_empty[:]
    output_row[labels.index(docs_y[x])]=1 

    training.append(bag)
    output.append(output_row)   

training = numpy.array(training)
output = numpy.array(output)           


net= tflearn.input_data(shape=[None,len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]),activation="softmax")
net = tflearn.regression(net)

model=tflearn.DNN(net)

model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)


def chat():
    print("Hi, what's your name?")
    name = input("You: ")
    print(f"Hello {name}! How can I assist you today? (type quit to stop)")

    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']

        print(random.choice(responses))

chat()