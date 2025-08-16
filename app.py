from flask import Flask, Response
import plotly.express as px

from storage import load_parking_data, load_parking_data_raw


app = Flask(__name__)


@app.route('/')
def index():
    data = load_parking_data(None)
    return data.to_dict()

@app.route('/histogram')
def histogram():
    hourly_data, totals = load_parking_data_raw()
    fig = px.bar(
        hourly_data.reset_index(),
        x='crossed_at',
        y=['in', 'out', 'turnback'],
        # color='direction',
        barmode='group',
        labels={'crossed_at': 'Hour of Day', 'count': 'Number of Crossings'},
        title='Hourly Crossings by Direction'
    )
    return fig.to_html(full_html=True)


@app.route('/test')
def test():
    return """<html><body><h1>Hello</h1></body></html>"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)