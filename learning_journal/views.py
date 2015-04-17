from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound

from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .models import (
    Session,
    DBSession,
    MyModel,
	Entry
    )

from .forms import EntryCreateForm

@view_config(route_name='home', renderer='templates/list.jinja2')
def show_list_of_entries(request):
    return { 'entries': Entry.all() }

@view_config(route_name='detail', renderer='templates/detail.jinja2')
def show_entry(request):
    entry_id = request.matchdict['id']
    entry = Entry.by_id(entry_id)
    if not entry:
        return HTTPNotFound()
    return { 'entry': entry }
#	{
#        'id': entry.id + 1,
#        'title': entry.title,
#        'body': entry.body
#    }
#    return "detail view for entry with id " + entry_id + " has value " + str(entry)

@view_config(route_name='create', renderer='templates/edit.jinja2')
def create_entry(request):
    entry = Entry()
    form = EntryCreateForm(request.POST)
    if request.method == 'POST' and form.validate():
        form.populate_obj(entry)
        session = Session()
        session.add(entry)
        session.commit()
        #return HTTPFound(location=request.route_url('home'))
        return HTTPFound(location=request.route_url('detail', id=entry.id))
    return {'form': form, 'action': 'create'}

@view_config(route_name='edit', renderer='templates/edit.jinja2')
def update_entry(request):
    entry_id = request.matchdict['id']
    entry = Entry.by_id(entry_id)
    if not entry:
        return HTTPNotFound()
    form = EntryCreateForm(request.POST, obj=entry)
#    if request.method == 'GET':
#        form.title.data = entry.title
#        form.body.data = entry.body
    if request.method == 'POST' and form.validate():
        form.populate_obj(entry)
        #return HTTPFound(location=request.route_url('home'))
        return HTTPFound(location=request.route_url('detail', id=entry.id))
    return { 'form': form, 'action': 'edit' }

#@view_config(route_name='home', renderer='templates/mytemplate.pt')
#def my_view(request):
#    try:
#        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
#    except DBAPIError:
#        return Response(conn_err_msg, content_type='text/plain', status_int=500)
#    return {'one': one, 'project': 'learning_journal'}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

