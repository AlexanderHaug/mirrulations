import os
from threading import Thread


def main():

    def run_redis():
        os.system('redis-server')

    def run_server():
        from mirrulations_server.endpoints import run
        run()

    def run_work():
        from mirrulations_server.docs_work_gen import monolith
        from mirrulations_server.expire import expire
        monolith()
        expire()

    Thread(target=run_redis).start()
    Thread(target=run_server).start()
    Thread(target=run_work).start()


if __name__ == '__main__':
    main()
