__author__ = 'jluker'

import os
import sys
import requests
from requests.auth import HTTPDigestAuth
from urlparse import urljoin
from endpoints import *

_auth_headers = {'X-REQUESTED-AUTH': 'Digest',
                 'X-Opencast-Matterhorn-Authorization': 'true'}

_cache_type = 'memory'
if not os.environ.get('TESTING', False):
    import requests_cache
    requests_cache.install_cache(backend=_cache_type)

_session = requests.Session()

def handle_http_exceptions(callbacks={}):
    def wrapper(f):
        def newfunc(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except requests.HTTPError, e:
                resp = e.response
                req = e.request
                if resp.status_code == 404:
                    print >>sys.stderr, \
                        "Endpoint not found at %s. " % req.url \
                        + "Perhaps it is not available on this node?"
                elif resp.status_code == 401:
                    print >>sys.stderr, "Access denied: %s" % e
                else:
                    for code, handler in callbacks.items():
                        if resp.status_code == code:
                            handler(e)
        return newfunc
    return wrapper

class MHClient(object):

    def __init__(self, base_url, user, passwd):
        self.base_url = base_url
        self.user = user
        self.passwd = passwd

    @handle_http_exceptions()
    def endpoints(self):
        """
        Retrieve the list of REST endpoint descriptions
        :return: list of dicts containing details on each endpoint available
        """
        return InfoEndpoint.endpoints(self)

    @handle_http_exceptions()
    def me(self):
        """
        Retrieve information about the current client user
        :return: dict containing info about the user, user's role(s), organization, etc
        """
        return InfoEndpoint.me(self)

    @handle_http_exceptions()
    def user_actions(self, **kwargs):
        actions = UserTrackingEndpoint.user_actions(self, **kwargs)
        return [UserAction(x, self) for x in actions]

    @handle_http_exceptions()
    def workflows(self, **kwargs):
        wfs = WorkflowEndpoint.instances(self, **kwargs)
        return [Workflow(x, self) for x in wfs]

    @handle_http_exceptions()
    def workflow(self, instance_id):
        wf = WorkflowEndpoint.instance(self, instance_id)
        return Workflow(wf, self)

    @handle_http_exceptions()
    def episodes(self, **kwargs):
        eps = EpisodeEndpoint.episodes(self, **kwargs)
        return [Episode(x, self) for x in eps]

    @handle_http_exceptions()
    def episode(self, episode_id):
        ep = EpisodeEndpoint.episode(self, episode_id)
        return Episode(ep, self)

    @handle_http_exceptions()
    def agents(self):
        agents_ = CaptureEndpoint.agents(self)
        return [CaptureAgent(x, self) for x in agents_]

    @handle_http_exceptions()
    def agent(self, agent_name):
        agent_ = CaptureEndpoint.agent(self, agent_name)
        return CaptureAgent(agent_, self)

    def get(self, path, params={}, headers={}):
        headers.update(_auth_headers)
        url = urljoin(self.base_url, path)
        auth = HTTPDigestAuth(self.user, self.passwd)
        resp = _session.get(url, params=params, headers=headers, auth=auth)
        resp.raise_for_status()
        return resp.json()


