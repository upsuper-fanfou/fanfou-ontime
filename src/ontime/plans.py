# - * - coding: UTF-8 - * -

from ontime import app

@app.route('/plan')
@app.route('/plan/p.<int:page>')
def list_plans(page=1):
    pass

@app.route('/plan/new', methods=['POST'])
def new_plan():
    pass

@app.route('/plan/<int:plan_id>/delete', methods=['POST'])
def delete_plan(plan_id):
    pass

@app.route('/plan/<int:plan_id>/edit', methods=['POST'])
def edit_plan(plan_id):
    pass
