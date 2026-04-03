class EventListener:
    def __init__(self):
        self.events = {}
        self.connections = []

    def register_event(self, event_name, handler):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(handler)

    def emit_event(self, event_name, *args, **kwargs):
        if event_name in self.events:
            for handler in self.events[event_name]:
                handler(*args, **kwargs)

    def manage_connection(self, connection):
        self.connections.append(connection)

    def handle_gift(self, gift_info):
        self.emit_event('gift', gift_info)

    def handle_danmaku(self, danmaku_info):
        self.emit_event('danmaku', danmaku_info)

    def handle_join(self, user_info):
        self.emit_event('join', user_info)

    def handle_leave(self, user_info):
        self.emit_event('leave', user_info)

    def handle_pk(self, pk_info):
        self.emit_event('pk', pk_info)

