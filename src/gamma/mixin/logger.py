import logging

class CallbackHandler(logging.Handler):
    _handlers:list[callable] = []
    def __init__(self, level=logging.DEBUG):
        super().__init__(level)
    
    def bind(self, handler:callable=None):
        if handler:
            self._handlers.append(handler)

    def emit(self, record):
        for handler in self._handlers:
            try: handler(record)
            except Exception as error: print(error) 

