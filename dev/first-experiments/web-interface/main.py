import random
import json

from flask import Flask
from flask import render_template
from flask import request
from flask import Response

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    prediction = {}
    return render_template('./index.html', title='Home', prediction=prediction)

@app.route('/current_prediction', methods= ['GET'])
def stuff():
    classes = ['left', 'still', 'right']

    prediction = {'direction': random.choice(classes), 'prob': random.uniform(0, 1)}
    return prediction
