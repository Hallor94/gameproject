listeners = {}

def subscribe(event_name, callback):
    if event_name not in listeners:
        listeners[event_name] = []
    listeners[event_name].append(callback)

def broadcast(event_name, context):
    for cb in listeners.get(event_name, []):
        cb(context)
