# forward_kubernetes_events_to_graylog
Watches kubernetes API for events in all namespaces, formats them in an opinionated way and sends them to a graylog server via UDP.

Some features of the forwarded messages:
 - level=info or level=warning depending on event type
 - cluster=cluster_name as specified on command line
 - source(host) field is either the pod name of the forwarder itself or event.source.host(kubernetes node of that event) if set
 - full_message contains the whole event, in some strange non-json form
 
It sends all currently known events on start
