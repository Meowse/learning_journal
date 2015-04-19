from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .security import ACLFactory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'DATABASE_URL' in os.environ:
        settings['sqlalchemy.url'] = os.environ['DATABASE_URL']
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(
        settings=settings,
        authentication_policy=AuthTktAuthenticationPolicy('somesecret'),
        authorization_policy=ACLAuthorizationPolicy(),
        default_permission='view')
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/', factory=ACLFactory)
    config.add_route('detail', '/journal/{id:\d+}', factory=ACLFactory)
    config.add_route('create', '/journal/create', factory=ACLFactory)
    config.add_route('edit', '/journal/{id:\d+}/edit', factory=ACLFactory)
    config.add_route('login', '/login', factory=ACLFactory)
    config.scan()
    return config.make_wsgi_app()
