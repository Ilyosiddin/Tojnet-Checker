#!/usr/bin/python3

import sqlite3
import tkinter
from tkinter import messagebox as mb
from tkinter import ttk

import requests
from bs4 import BeautifulSoup

def get_accounts_list():
    """
        Return list with accounts
    """

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(""" SELECT name, login, password FROM Users; """)
    data = cursor.fetchall()
    conn.close()

    return [i[0] for i in data]


def get_current_user():
    """
        Return a dict with current user name, login and password
    """

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(""" SELECT name, login, password FROM Users WHERE current = 1 """)
    data = cursor.fetchall()
    conn.close()
    if data:
        return {
            "name": data[0][0],
            "login": data[0][1],
            "password": data[0][2]
        }


def get_balance(html):
    """ Return a string with balance of account on stat.tojnet.tj """

    return html.select('.utm-cell')[7].text


def get_id(html):
    """ Return a string with ID of account on stat.tojnet.tj  """

    return html.select('.utm-cell')[5].text


def get_link(html):
    """ Return a URL of page with info """

    return 'http://stat.tojnet.tj/' + html.select('.utm-cell'
                                                  )[1].a.get_attribute_list('href')[0]


def get_paid_mbytes(html):
    """ Return a string which haves one number (Paid mbytes) """

    text = html.select('.utm-cell')[19].text.split()
    text = list(text)
    for i in text:
        try:
            int(i.split('.')[0])
            return i
        except ValueError:
            pass

def get_ip(html):
    """ Return an IP Adress """

    return html.select('.utm-cell')[8].text


def get_purchased_mbytes(html):
    """ Return a string about purchased mbytes """

    text = html.select('.utm-cell')[21].text.split()[1]
    try:
        int(text.split('.')[0])
        return text
    except ValueError:
        return "0"

def get_price_of_purchased_mbytes(html):
    """ Return a string about price of purchased mbytes """

    text = html.select('.utm-cell')[22].text
    try:
        int(text.split('.')[0])
        return text
    except ValueError:
        return "0"


def update():
    """
        Update info about balance, mbytes, etc...
    """

    session = requests.Session()
    user = get_current_user()

    if user:
        try:
            response = session.post('http://stat.tojnet.tj',
                                    data=user)
        except:
            mb.showerror(lang["error"],
                         lang["msg_bad_connect"]
                         )
            return
        html = BeautifulSoup(response.text, 'html.parser')

        label_balance['text'] = lang['balance'] + get_balance(html)
        label_id['text'] = 'ID: ' + get_id(html)

        response = \
            session.get('http://stat.tojnet.tj/?module=41_services')
        response = session.get(get_link(BeautifulSoup(response.content,
                                                      'html.parser')))
        html = BeautifulSoup(response.content, 'html.parser')

        label_paid_mbytes['text'] = lang["paid_mbytes"] \
                                    + get_paid_mbytes(html)
        label_ip['text'] = lang['ip_addr'] + get_ip(html)
        label_purchased_mbytes['text'] = lang["purchased_mbytes"] \
                                         + get_purchased_mbytes(html)
        label_price['text'] = lang["purchased_mbytes_price"] + get_price_of_purchased_mbytes(html)
    else:

        mb.showerror(lang['error'], lang["msg_set_account_before_update"])


def accounts_settings():
    """
        Create a window with entries for passwords, names etc
    """

    def update_boxes():
        accounts_box['values'] = get_accounts_list()
        user = get_current_user()
        def_account_box['values'] = get_accounts_list()
        if user:
            name = user['name']
            def_account_box.set(name)

    def delete_account():
        """
            Delete account, get data from combobox
        """
        name = accounts_box.get()
        print(name)

        conn = sqlite3.connect("data.db")

        cursor = conn.cursor()
        print(""" DELETE FROM Users where name = \"{}\" """.format(name))
        cursor.execute(""" DELETE FROM Users where name = \"{}\" """.format(name))
        conn.commit()
        conn.close()

    def create_account():
        """
            Create account and save it to data.dat, get data from Entries
        """

        name = input_name.get()
        password = input_password.get()
        login = input_login.get()

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(""" UPDATE Users SET current = 0 WHERE current = 1 """)
        cursor.execute(
            """ 
                INSERT INTO Users (name, login, password, current) VALUES (\"{}\", \"{}\", \"{}\", 1);
            """.format(name,
                       login,
                       password))
        conn.commit()
        conn.close()
        update_boxes()

    def set_def_account():
        name = def_account_box.get()
        if name:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute(""" UPDATE Users SET current = 0 WHERE current = 1 """)
            cursor.execute(""" UPDATE Users SET current = 1 WHERE name = \"{}\" """.format(name))
            conn.commit()
            conn.close()
            update_boxes()

    window = tkinter.Toplevel(root)
    window.focus_set()
    window.grab_set()
    window.title(lang['accounts'])
    window.resizable(False, False)
    window.geometry('400x300')

    # delete account field

    lbl_delete_account = tkinter.Label(window, text=lang["del_account"],
                                       font='Arial 15')
    lbl_delete_account.pack()
    accounts_box = ttk.Combobox(window, values=get_accounts_list())
    accounts_box.pack()
    delete_button = ttk.Button(window, text=lang["del_this_account"],
                               command=delete_account)
    delete_button.pack()

    # create account field

    lbl_create_account = tkinter.Label(window, text=lang["create_account"],
                                       font='Arial 15')
    lbl_create_account.pack()

    name_lbl = tkinter.Label(window, text=lang["name"], font="Arial 10")
    name_lbl.place(x=40, y=104)

    login_lbl = tkinter.Label(window, text=lang["login"], font="Arial 10")
    login_lbl.place(x=40, y=124)

    password_lbl = tkinter.Label(window, text=lang["password"], font="Arial 10")
    password_lbl.place(x=40, y=144)

    input_name = ttk.Entry(window)
    input_name.pack()

    input_login = ttk.Entry(window)
    input_login.pack()

    input_password = ttk.Entry(window)
    input_password.pack()

    button_create = ttk.Button(window, text=lang['create_account'],
                               command=create_account)
    button_create.pack()

    # set default account field

    lbl_def_account = tkinter.Label(window,
                                    text=lang["sel_def_account"],
                                    font='Arial 15')
    lbl_def_account.pack()
    def_account_box = ttk.Combobox(window)
    user = get_current_user()
    if user:
        def_account_box.set(user['name'])
        
    def_account_box.pack()
    set_def_account_button = ttk.Button(window, text='SET',
                                        command=set_def_account)
    set_def_account_button.pack()

    update_boxes()


def get_language():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute(""" SELECT * FROM Languages WHERE current = 1; """)
    data = cursor.fetchall()
    conn.close()
    return {
        "lang_name": data[0][0],
        "error": data[0][1],
        "msg_bad_connect": data[0][2],
        "balance": data[0][3],
        "paid_mbytes": data[0][4],
        "purchased_mbytes": data[0][5], 
        "purchased_mbytes_price": data[0][6],
        "msg_set_account_before_update": data[0][7],
        "msg_set_account": data[0][8],
        "accounts": data[0][9], 
        "del_account": data[0][10], 
        "del_this_account": data[0][11], 
        "create_account": data[0][12],
        "name": data[0][13], 
        "login": data[0][14], 
        "password": data[0][15], 
        "sel_def_account": data[0][16], 
        "update": data[0][17], 
        "settings": data[0][18], 
        "about_program": data[0][19], 
        "language": data[0][20], 
        "ip_addr": data[0][21],
        "lang_info": data[0][23],
        "msg_about_prog": data[0][24]
    }



def language():
    def set_lang():
        name = box.get()
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        cursor.execute(""" UPDATE Languages SET current = 0 WHERE current = 1 """)
        cursor.execute(""" UPDATE Languages SET current = 1 WHERE lang_name = \"{}\" """.format(name))
        conn.commit()
        conn.close()
        mb.showinfo("Info", lang["lang_info"])

    window = tkinter.Toplevel(root)
    window.focus_set()
    window.grab_set()
    window.geometry("300x60")
    window.resizable(False, False) 
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lang_name FROM Languages")
    data = cursor.fetchall()
    data = [i[0] for i in data]

    cursor.execute("SELECT lang_name FROM Languages WHERE current = 1")
    lang_name = cursor.fetchall()[0][0]

    box = ttk.Combobox(window, values=data)
    box.pack()
    box.set(lang_name)
    conn.close()
    button = ttk.Button(window, text="SET", command=set_lang)
    button.pack(side=tkinter.BOTTOM)

def about_program():
    mb.showinfo("Info",lang["msg_about_prog"].replace("\\n", "\n"))
    

if __name__ == '__main__':
    lang = get_language()
    root = tkinter.Tk()
    root.iconbitmap("icon.ico")
    root.geometry('600x400')
    root.title('TojNet Checker v0.01')
    root.resizable(False, False)
    main_menu = tkinter.Menu(root)
    root.config(menu=main_menu)
    settings_menu = tkinter.Menu(main_menu)
    main_menu.add_command(label=lang["update"], command=update)
    main_menu.add_cascade(label=lang["settings"], menu=settings_menu)
    main_menu.add_command(label=lang["about_program"], command=about_program)
    settings_menu.add_command(label=lang["accounts"],
                              command=accounts_settings)
    settings_menu.add_command(label=lang["language"], command=language)

    label_balance = tkinter.Label(text=lang["balance"], font='Arial 18')
    label_balance.place(x=20, y=20)

    label_paid_mbytes = tkinter.Label(text=lang["paid_mbytes"],
                                      font='Arial 18')
    label_paid_mbytes.place(x=20, y=60)

    label_ip = tkinter.Label(text=lang["ip_addr"], font='Arial 18')
    label_ip.place(x=20, y=100)

    label_purchased_mbytes = tkinter.Label(text=lang["purchased_mbytes"],
                                           font='Arial 18')
    label_purchased_mbytes.place(x=20, y=140)

    label_price = tkinter.Label(text=lang["purchased_mbytes_price"],
                                font='Arial 18')
    label_price.place(x=20, y=180)

    label_id = tkinter.Label(text='ID: ', font='Arial 18')
    label_id.place(x=20, y=220)

    update_button = ttk.Button(text=lang["update"], command=update)
    update_button.place(x=280, y=350)

    root.mainloop()
