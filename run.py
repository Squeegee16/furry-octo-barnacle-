#! /usr/bin/env python3

from flaskinventory import garden_app

app = garden_app()#ref from init.py

if __name__ == '__main__':# run this file directly
    try:
        app.run(debug = True,host = "192.168.0.156", port = 5000) # auto rerun of webapp when changes occur
    except OSError:
         app.run(host = "127.0.0.1", port = 5000)
    except KeyboardInterrupt:
        print('User Stop')
        