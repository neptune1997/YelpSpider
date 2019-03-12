from mydb import database
from selecrawler import selecrawler
import time


def main():
    db = database()
    # db._createdb() ##use this function will create a new database
    db.connect()
    sele = selecrawler()
    sele.connectdb(db)
    sele.get_all_cities()
    for k, v in sele.citydict.items():
        if time.clock() > 300:
            break
        print("handling city {} ".format(k))
        sele.handle_onecity(k, v)
    print("got {} restaurants in {}s".format(db.count,time.clock()))


if __name__ == '__main__':
    main()
