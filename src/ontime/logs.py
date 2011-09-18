# - * - coding: UTF-8 - * -

from ontime import app

@app.route('/log')
@app.route('/log/p.<int:page>')
@app.route('/log/type.<type>')
@app.route('/log/type.<type>/p.<int:page>')
def list_logs(**kws):
    pass
