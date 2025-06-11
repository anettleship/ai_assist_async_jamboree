import asyncio
import tornado

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        # Add 2 second delay to demonstrate async vs sync difference
        await asyncio.sleep(2)
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

async def main():
    app = make_app()
    app.listen(8888, address='0.0.0.0')
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())