from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound

from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .models import (
    Session,
    DBSession,
    MyModel,
	Entry,
	User
    )

from .forms import EntryCreateForm

from pyramid.security import forget, remember
from .forms import LoginForm

from pyramid.security import authenticated_userid

@view_config(route_name='home', renderer='templates/list.jinja2')
def show_list_of_entries(request):
    form = None
    if not authenticated_userid(request):
        form = LoginForm()
    return {'entries': Entry.all(), 'login_form': form}

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

@view_config(route_name='create', renderer='templates/edit.jinja2', permission='create')
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

@view_config(route_name='edit', renderer='templates/edit.jinja2', permission='edit')
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

@view_config(route_name='login', renderer='string', request_method='POST')
def sign_in(request):
    login_form = None
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
    if login_form and login_form.validate():
        user = User.by_name(login_form.username.data)
        if user and user.has_password(login_form.password.data):
            headers = remember(request, user.name)
        else:
            headers = forget(request)
    else:
        headers = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=headers)

