#!/usr/bin/env python3

import graypy.handler
graypy.handler.make_message_dict = lambda x, *args: x  # get out of my way

GRAYLOG_IP = None
CLUSTER = None


def forward_to_graylog(event):
    import socket
    if not hasattr(forward_to_graylog, 'handler'):
        forward_to_graylog.handler = graypy.handler.GELFHandler(GRAYLOG_IP)
    level = 6 if event.type == 'Normal' else 4
    gl_event = dict(
        version="1.1",
        host=socket.gethostname(),
        short_message=event.message,
        full_message=str(event),
        timestamp=event.last_timestamp.isoformat(),
        level=level,

        _cluster=CLUSTER,
        _reason=event.reason,
        _namespace=event.involved_object.namespace,
        _kind=event.involved_object.kind,
        _name=event.involved_object.name,
        _first_timestamp=event.first_timestamp.isoformat(),
    )
    if event.source.component:
        gl_event['source_component'] = event.source.component
    if event.source.host:
        gl_event['host'] = event.source.host
    pickle = forward_to_graylog.handler.makePickle(gl_event)
    forward_to_graylog.handler.send(pickle)


def main(args):
    global GRAYLOG_IP, CLUSTER
    from kubernetes import client, config, watch
    if len(args) < 3:
        raise RuntimeError("args: graylog_ip cluster_name")
    GRAYLOG_IP = args[1]
    CLUSTER = args[2]
    try:
        config.load_kube_config()
    except IOError:
        config.load_incluster_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    while True:
        for event in w.stream(v1.list_event_for_all_namespaces):
            type_ = event['type']
            if type_ != 'ADDED':
                continue
            event = event['object']
            if event.api_version != 'v1':
                continue
            forward_to_graylog(event)

if __name__ == '__main__':
    import sys
    main(sys.argv)
