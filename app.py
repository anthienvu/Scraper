#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Feb 27 20:44:06 2020

@author: trungminh
'''



import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table as dt
import pandas as pd
import scraper
from six.moves.urllib.parse import quote

import flask
import os
from random import randint



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

def serve_layout():
    return html.Div([
                     html.H1(children = 'Scraper Demo'),
    
                     html.Div([
                         html.Div(dcc.Input(id = 'input_text', type = 'text',
                                            style ={ 'width': 600, 'margin': 10}),
                                  style = {'display': 'inline-block', 'fontColor': 'blue'}),
                         html.Button('Search', id='button_search'),
                         ], style = {'margin-bottom': 10}),

                     html.Div(                 
                         html.A('Download Data', id = 'link_download',
                                download = 'rawdata.csv', href='', target='_blank')
                         ),
                                  
                     html.Div([
                         dt.DataTable(id = 'dtable_time',
                             columns = [{'name': i, 'id': i} for i in ['Title', 'Email', 'Phone']],
                             style_table = {'overflowX': 'scroll'},
                             style_cell = {'textAlign': 'left',
                                         'height': 'auto',
                                         'whiteSpace': 'normal'
                                         })
                         ], style = {'display': 'inline-block', 'width':1000}),
                                                  
                     ], style = {'textAlign': 'center'})

app.layout = serve_layout
                     
@app.callback(Output('button_search', 'disabled'),
              [Input('input_text', 'value')])
def update_button(value):
    
    if value is None or len(value) == 0:
        return True
    else:
        return False
                     
        
@app.callback(Output('dtable_time', 'data'),
              [Input('button_search', 'n_clicks')],
              [State('input_text', 'value')])
def run_scraper(n_clicks, value):
    info_df = pd.DataFrame()
    
    if (value is not None and len(value) > 0):
        info_df = scraper.runScraper(value)
                      
    return info_df.to_dict('records')
                

@app.callback(Output('link_download', 'href'),
    [dash.dependencies.Input('dtable_time', 'data')])
def update_download_link(data):
    if data is not None and len(data) > 0:
        data = pd.DataFrame.from_dict(data)
        data = data[['Title', 'Email', 'Phone']]
        csv_string = data.to_csv(index = False, encoding = 'utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)
        return csv_string
    else:
        return None                     
        
if __name__ == '__main__':
    app.run_server(debug = True)
#    app.run_server(host = '127.0.0.1', port = '5000',debug=True)