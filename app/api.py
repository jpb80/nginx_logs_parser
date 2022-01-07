#!/usr/bin/env python
# coding=utf-8
from flask import Flask
import nginx_log_parser

app = Flask(__name__)

@app.route('/')
def get_nginx_parser_results():
    return nginx_log_parser.main()

@app.route('/healthz')
def healthcheck():
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=False)
