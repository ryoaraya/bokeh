#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2020, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
import pytest ; pytest

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Bokeh imports
from bokeh.application import Application

# Module under test
import bokeh.server.contexts as bsc # isort:skip

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

class TestBokehServerContext(object):

    def test_init(self) -> None:
        ac = bsc.ApplicationContext("app", io_loop="ioloop")
        c = bsc.BokehServerContext(ac)
        assert c.application_context == ac

    def test_sessions(self) -> None:
        ac = bsc.ApplicationContext("app", io_loop="ioloop")
        ac._sessions = dict(foo=1, bar=2)
        c = bsc.BokehServerContext(ac)
        assert set(c.sessions) == set([1,2])

class TestBokehSessionContext(object):

    def test_init(self) -> None:
        ac = bsc.ApplicationContext("app", io_loop="ioloop")
        sc = bsc.BokehServerContext(ac)
        c = bsc.BokehSessionContext("id", sc, "doc")
        assert c.session is None
        assert c.request is None
        assert not c.destroyed
        assert c.logout_url is None

    def test_destroyed(self) -> None:
        class FakeSession(object):
            destroyed = False
        ac = bsc.ApplicationContext("app", io_loop="ioloop")
        sc = bsc.BokehServerContext(ac)
        c = bsc.BokehSessionContext("id", sc, "doc")
        sess = FakeSession()
        c._session = sess
        assert not c.destroyed
        sess.destroyed = True
        assert c.destroyed

    def test_logout_url(self) -> None:
        ac = bsc.ApplicationContext("app", io_loop="ioloop")
        sc = bsc.BokehServerContext(ac)
        c = bsc.BokehSessionContext("id", sc, "doc", logout_url="/logout")
        assert c.session is None
        assert c.request is None
        assert not c.destroyed
        assert c.logout_url == "/logout"

class TestApplicationContext(object):

    def test_init(self) -> None:
        c = bsc.ApplicationContext("app", io_loop="ioloop")
        assert c.io_loop == "ioloop"
        assert c.application == "app"
        assert c.url is None

        c = bsc.ApplicationContext("app", io_loop="ioloop", url="url")
        assert c.io_loop == "ioloop"
        assert c.application == "app"
        assert c.url == "url"

    def test_sessions(self) -> None:
        c = bsc.ApplicationContext("app", io_loop="ioloop")
        c._sessions = dict(foo=1, bar=2)
        assert set(c.sessions) == set([1,2])

    def test_get_session_success(self) -> None:
        c = bsc.ApplicationContext("app", io_loop="ioloop")
        c._sessions = dict(foo=1, bar=2)
        assert c.get_session("foo") == 1

    def test_get_session_failure(self) -> None:
        c = bsc.ApplicationContext("app", io_loop="ioloop")
        c._sessions = dict(foo=1, bar=2)
        with pytest.raises(bsc.ProtocolError) as e:
            c.get_session("bax")
        assert str(e.value).endswith("No such session bax")

    @pytest.mark.asyncio
    async def test_create_session_if_needed_new(self) -> None:
        app = Application()
        c = bsc.ApplicationContext(app, io_loop="ioloop")
        class FakeRequest(object):
            arguments = dict(foo=10)
        req = FakeRequest()
        s = await c.create_session_if_needed("foo", request=req)
        assert c.get_session("foo") == s

    @pytest.mark.asyncio
    async def test_create_session_if_needed_exists(self) -> None:
        app = Application()
        c = bsc.ApplicationContext(app, io_loop="ioloop")
        class FakeRequest(object):
            arguments = dict(foo=10)
        req = FakeRequest()
        s1 = await c.create_session_if_needed("foo", request=req)
        s2 = await c.create_session_if_needed("foo", request=req)
        assert s1 == s2

    @pytest.mark.asyncio
    async def test_create_session_if_needed_bad_sessionid(self) -> None:
        app = Application()
        c = bsc.ApplicationContext(app, io_loop="ioloop")
        class FakeRequest(object):
            arguments = dict(foo=10)
        req = FakeRequest()
        r = c.create_session_if_needed("", request=req)
        with pytest.raises(bsc.ProtocolError) as e:
            await r
        assert str(e.value).endswith("Session ID must not be empty")

    @pytest.mark.asyncio
    async def test_create_session_if_needed_logout_url(self) -> None:
        app = Application()
        c = bsc.ApplicationContext(app, io_loop="ioloop", logout_url="/logout")
        class FakeRequest(object):
            arguments = dict(foo=10)
        req = FakeRequest()
        s = await c.create_session_if_needed("foo", request=req)
        session = c.get_session("foo")
        assert session == s
        assert c._session_contexts[session.id].logout_url == "/logout"

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
