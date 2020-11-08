from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response, send_file
from flask import current_app as app
import requests

main = Blueprint('main', __name__, url_prefix='/')

@main.route('/', methods=['GET'])
def index():
    return "It works!"
