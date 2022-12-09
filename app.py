from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    # return '<h1>Hello, World!</h1>'
    return render_template('./index.html')
