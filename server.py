import os
import json
from tornado import ioloop, web, websocket, concurrent
from concurrent.futures import ThreadPoolExecutor


content = None
meta_logs_map = {}


class Index(web.RequestHandler):
    def get(self):
        self.render('build/index.html')


class SocketManager(object):
    connections = []

    @classmethod
    def add_connection(cls, socket):
        cls.connections.append(socket)

    @classmethod
    def remove_connection(cls, socket):
        cls.connections.remove(socket)


class Socket(websocket.WebSocketHandler):
    exception_list = ['final_chips', 'self']

    def open(self):
        print('Open a web socket.')

    def on_close(self):
        print('Close a web socket.')

    def on_message(self, message):
        print(message)
        parse_full_json(message)
        if content:
            for e in self.exception_list:
                if e in content:
                    self.write_message({e: content[e]})
                    del content[e]
            for key in content:
                self.write_message(content.get(key))


class UploadLog(web.RequestHandler):
    executor = ThreadPoolExecutor(os.cpu_count())

    async def post(self):
        print(self.request.files)
        try:
            file_list = list(self.request.files.values())[0]
            for f in file_list:
                await self.write_log_file(f)
                GetNewLogUploaded.update_log_message(f['filename'])
        except Exception as e:
            print('Get exception: %s' % e)

    @concurrent.run_on_executor
    def write_log_file(self, f):
        print('Get %s.' % f['filename'])
        with open('battle-log/%s' % f['filename'], 'wb') as fh:
            fh.write(f['body'])


settings = {
    'autoreload': True,
}


if __name__ == '__main__':
    app = web.Application([
        (r'/', Index),
        (r'/socket', Socket),
        (r'/build/(.*)', web.StaticFileHandler, {'path': './build'}),
        (r'/img/(.*)', web.StaticFileHandler, {'path': './assets/img'}),
    ], **settings)
    app.listen(3000)
    ioloop.IOLoop.current().start()
