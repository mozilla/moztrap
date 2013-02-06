"""
Deployment for moztrap

Requires commander (https://github.com/oremj/commander) which is installed on
the systems that need it.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task, hostgroups

import commander_settings as settings

@task
def update_code(ctx, tag):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("git fetch")
        ctx.local("git pull origin %s" % tag)
        ctx.local("git submodule sync")
        ctx.local("git submodule update --init --recursive")
        ctx.local("find . -type f -name '.gitignore' -or -name '*.pyc' -delete")
        ctx.local("git rev-parse HEAD > media/revision.txt")

@task
def update_assets(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("LANG=en_US.UTF-8 python2.6 vendor-manage.py collectstatic --noinput")
        ctx.local("LANG=en_US.UTF-8 python2.6 vendor-manage.py compress")

@task
def database(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("python2.6 vendor-manage.py syncdb --migrate")

@task
def checkin_changes(ctx):
    ctx.local(settings.DEPLOY_SCRIPT)


@hostgroups(settings.WEB_HOSTGROUP, remote_kwargs={'ssh_key': settings.SSH_KEY})
def deploy_app(ctx):
    ctx.remote(settings.REMOTE_UPDATE_SCRIPT)
    ctx.remote("/bin/touch %s" % settings.REMOTE_WSGI)


@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    update_code(ref)


@task
def update(ctx):
    update_assets()
    database()


@task
def deploy(ctx):
    pre_update()
    update()
    checkin_changes()
    deploy_app()