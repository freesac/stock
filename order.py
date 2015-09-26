# -*- encoding: utf8 -*-
__author__ = '���ڽ���'

import tkinter.messagebox
import tkinter as tk
from tkinter import ttk
import threading
import time
import win32gui
import win32api
import datetime

import win32con
import tushare as ts

TIME = 100

is_start = False
is_monitor = True
items_list = []
trading_messages = []
stock_name = ''
stock_price = ''


def hold_mouse():
    # �̶����λ��
    # ��ȡ��Ļ�����ش�С
    screen_width_pixel = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    # �̶����λ��
    mouse_position = [
        screen_width_pixel - 200, 200, screen_width_pixel - 200, 200]
    win32api.ClipCursor(mouse_position)


def release_mouse():
    # �ͷ����
    mouse_position = [0, 0, 0, 0]
    win32api.ClipCursor(mouse_position)


def focus_on_window(hwnd):
    # win32gui.ShowWindow(hwnd_parent, win32con.SW_SHOWMAXIMIZED)
    win32gui.SetForegroundWindow(hwnd)


def get_sub_handlers_lst(hwnd, class_name):
    # ���Ҹ�������class_name�����о������Ϊ�б�
    hwnd_child_lst = []
    hwnd_child = win32gui.FindWindowEx(hwnd, None, class_name, None)
    hwnd_child_lst.append(hwnd_child)
    while True:
        hwnd_child = win32gui.FindWindowEx(hwnd, hwnd_child, class_name, None)
        if hwnd_child != 0:
            hwnd_child_lst.append(hwnd_child)
        else:
            return hwnd_child_lst


def get_last_handlers_lst(hwnd_parent):
    '''
    :param hwnd_parent: ��������
    :return: �ؼ�����б�
    '''
    # ��ȡ˫��ί�н���dialog�����пؼ����
    hwnd_second = win32gui.FindWindowEx(hwnd_parent, None, 'AfxMDIFrame42s', None)
    # AfxMDIFrame42s�����������Ӵ��ڵľ��
    hwnd_three_lst = get_sub_handlers_lst(hwnd_second, '#32770')
    # ˫��ί�н����µ�dialog�����Ӵ��ھ��������EDIT,BUTTON,STATIC�ؼ���
    for handler in hwnd_three_lst:
        hwnd_last_lst = get_sub_handlers_lst(handler, None)
        if len(hwnd_last_lst) == 70:
            # print('hwnd_last_lst are', hwnd_last_lst)
            return hwnd_last_lst


def left_mouse_click(hwnd):
    # ���������
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, None, None)
    win32api.Sleep(TIME)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, None)
    win32api.Sleep(TIME)


def virtual_key(hwnd_parent, key_code):
    win32gui.PostMessage(hwnd_parent, win32con.WM_KEYDOWN, key_code, 0)  # ��Ϣ����
    win32api.Sleep(TIME)
    win32gui.PostMessage(hwnd_parent, win32con.WM_KEYUP, key_code, 0)
    win32api.Sleep(TIME)


def input_string(hwnd_edit, string):
    # EDIT�ؼ��������ַ���
    win32api.SendMessage(hwnd_edit, win32con.WM_SETTEXT, None, string)
    win32api.Sleep(TIME)


def is_click_popup_window(hwnd_parent, button_title):
    # ����е���ʽ���ڣ��������ȷ����ť
    if hwnd_parent:
        hwnd_popup = win32gui.GetWindow(hwnd_parent, win32con.GW_ENABLEDPOPUP)
        # print('hwnd_parent and hwnd_popup are', hwnd_parent, hwnd_popup)
        if hwnd_popup:
            focus_on_window(hwnd_popup)
            hwnd_button = win32gui.FindWindowEx(hwnd_popup, None, 'Button', button_title)
            left_mouse_click(hwnd_button)
            return True
    return False


def buy(hwnd_parent, stock_code, stock_number):
    virtual_key(hwnd_parent, win32con.VK_F6)  # ���뱣֤��˫��ί�н����²���Ч
    hwnd_lst = get_last_handlers_lst(hwnd_parent)  # ������ǰ�����»�þ��
    if is_click_popup_window(hwnd_parent, None):  # �ж��Ƿ��Ƿ�ʱ����������
        time.sleep(5)
    left_mouse_click(hwnd_lst[2])
    input_string(hwnd_lst[2], stock_code)
    left_mouse_click(hwnd_lst[7])
    input_string(hwnd_lst[7], stock_number)
    left_mouse_click(hwnd_lst[8])
    time.sleep(0.5)  # ��0.5s����ȷ�ϴ������޵���
    return not is_click_popup_window(hwnd_parent, None)  # �������True��Ҳ˵������û�г���


def sell(hwnd_parent, stock_code, stock_number):
    virtual_key(hwnd_parent, win32con.VK_F6)
    hwnd_lst = get_last_handlers_lst(hwnd_parent)
    if is_click_popup_window(hwnd_parent, None):
        time.sleep(5)
    left_mouse_click(hwnd_lst[11])
    input_string(hwnd_lst[11], stock_code)
    left_mouse_click(hwnd_lst[16])
    input_string(hwnd_lst[16], stock_number)
    left_mouse_click(hwnd_lst[17])
    time.sleep(0.5)
    return not is_click_popup_window(hwnd_parent, None)


def trading_init(trading_program_title):
    # ��ȡ����������
    hwnd_parent = win32gui.FindWindow(None, trading_program_title)
    if hwnd_parent == 0:
        tkinter.messagebox.showerror('����', '���ȴ򿪻�̩֤ȯ��������������б����')
    return hwnd_parent


def get_stock_data(stock_code):
    stock_data = []
    df = ts.get_realtime_quotes(stock_code)
    # print(df)
    stock_data.append(df['name'][0])
    stock_data.append(float(df['price'][0]))
    return stock_data


def is_digit(str1):
    # �ַ����Ƿ�������
    if str1 == '':
        return False
    for ch in str1:
        if not ch.isdigit():
            if ch != '.':
                return False
    return True


def monitor():
    # �ɼۼ�غ���
    global stock_name, stock_price, trading_messages
    hwnd_parent = trading_init('���Ϲ�Ʊ����ϵͳ5.0')
    sell_times = 1
    buy_times = 1
    # ���hwnd_parentΪ�㣬ֱ����ֹѭ��
    while is_monitor and hwnd_parent:
        if is_start:
            if items_list[0] != '':
                stock_name, stock_price = get_stock_data(items_list[0])

                # ����
                if items_list[3] != '':

                    # stop_loss_sell
                    if sell_times and (stock_price < items_list[1]):
                        dt = datetime.datetime.now()
                        if sell(hwnd_parent, items_list[0], items_list[3]):
                            trading_messages.append(
                                (dt.strftime('%x'), dt.strftime('%X'), items_list[0], stock_name, 'ֹ��', stock_price,
                                 items_list[3], '�ɹ�'))
                        else:
                            trading_messages.append(
                                (dt.strftime('%x'), dt.strftime('%X'), items_list[0], stock_name, 'ֹ��', stock_price,
                                 items_list[3], 'ʧ��'))
                        sell_times -= 1
                        time.sleep(1)

                    # stop_profit_sell
                    if sell_times and (stock_price > items_list[2]):
                        dt = datetime.datetime.now()
                        if sell(hwnd_parent, items_list[0], items_list[3]):
                            trading_messages.append(
                                (dt.strftime('%x'), dt.strftime('%X'), items_list[0], stock_name, 'ֹӯ', stock_price,
                                 items_list[3], '�ɹ�'))
                        else:
                            trading_messages.append(
                                (dt.strftime('%x'), dt.strftime('%X'), items_list[0], stock_name, 'ֹӯ', stock_price,
                                 items_list[3], 'ʧ��'))
                        sell_times -= 1
                        time.sleep(1)

                # ����
                if items_list[5] != '':
                    # ͻ������
                    if buy_times and (stock_price > items_list[4]):
                        dt = datetime.datetime.now()
                        if buy(hwnd_parent, items_list[0], items_list[5]):
                            trading_messages.append(
                                (dt.strftime('%x'), dt.strftime('%X'), items_list[0], stock_name, 'ͻ������', stock_price,
                                 items_list[5], '�ɹ�'))
                        else:
                            trading_messages.append(
                                (dt.strftime('%x'), dt.strftime('%X'), items_list[0], stock_name, 'ͻ������', stock_price,
                                 items_list[5], 'ʧ��'))
                        buy_times -= 1
                        time.sleep(1)
        time.sleep(3)


class StockGui:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("��Ʊ���װ���")

        # self.window.geometry("800x600+300+300")
        self.window.resizable(0, 0)

        # ��Ʊ��Ϣ
        frame1 = tk.Frame(self.window)
        frame1.pack(side=tk.LEFT, padx=10, pady=10)

        label_frame0 = tk.LabelFrame(frame1, text="��Ʊ")
        label_frame0.pack(side=tk.TOP, padx=5)

        tk.Label(label_frame0, text="��Ʊ����", width=10).grid(
            row=1, column=1, sticky=tk.W)
        tk.Label(label_frame0, text="��Ʊ����", width=10).grid(
            row=2, column=1, sticky=tk.W)
        tk.Label(label_frame0, text="��ǰ�۸�", width=10).grid(
            row=3, column=1, sticky=tk.W)
        self.stock_code = tk.StringVar()
        self.stock_code_entry = tk.Entry(label_frame0, textvariable=self.stock_code, width=10,
                                         justify=tk.RIGHT)
        self.stock_code_entry.grid(row=1, column=2)
        self.stock_name_label = tk.Label(
            label_frame0, width=10, bg="yellow", justify=tk.RIGHT)
        self.stock_name_label.grid(row=2, column=2)
        self.stock_price_label = tk.Label(
            label_frame0, width=10, bg="yellow", justify=tk.RIGHT)
        self.stock_price_label.grid(row=3, column=2)

        # ����
        label_frame1 = tk.LabelFrame(frame1, text="����")
        label_frame1.pack(side=tk.TOP, padx=5)
        tk.Label(label_frame1, text="ֹ��۸�", width=10, fg="blue").grid(
            row=1, column=1, sticky=tk.W)
        tk.Label(label_frame1, text="ֹӯ�۸�", width=10, fg="blue").grid(
            row=2, column=1, sticky=tk.W)
        tk.Label(label_frame1, text="��������", width=10, fg="blue").grid(
            row=3, column=1, sticky=tk.W)
        self.stop_loss_price = tk.StringVar()
        self.stop_loss_price_entry = tk.Entry(label_frame1, textvariable=self.stop_loss_price, width=10,
                                              justify=tk.RIGHT)
        self.stop_loss_price_entry.grid(row=1, column=2)

        self.stop_profit_price = tk.StringVar()
        self.stop_profit_price_entry = tk.Entry(label_frame1, textvariable=self.stop_profit_price, width=10,
                                                justify=tk.RIGHT)
        self.stop_profit_price_entry.grid(row=2, column=2)

        self.sell_stock_number = tk.StringVar()
        self.sell_stock_number_entry = tk.Entry(label_frame1, textvariable=self.sell_stock_number, width=10,
                                                justify=tk.RIGHT)
        self.sell_stock_number_entry.grid(row=3, column=2)

        # ����
        label_frame2 = tk.LabelFrame(frame1, text="����")
        label_frame2.pack(side=tk.TOP, padx=5)
        tk.Label(label_frame2, text="ͻ�Ƽ۸�", width=10, fg="red").grid(
            row=1, column=1, sticky=tk.W)
        tk.Label(label_frame2, text="��������", width=10, fg="red").grid(
            row=2, column=1, sticky=tk.W)

        self.buy_stock_price = tk.StringVar()
        self.buy_stock_price_entry = tk.Entry(label_frame2, textvariable=self.buy_stock_price, width=10,
                                              justify=tk.RIGHT)
        self.buy_stock_price_entry.grid(row=1, column=2)

        self.buy_stock_number = tk.StringVar()
        self.buy_stock_number_entry = tk.Entry(label_frame2, textvariable=self.buy_stock_number, width=10,
                                               justify=tk.RIGHT)
        self.buy_stock_number_entry.grid(row=2, column=2)
        # ί��
        frame2 = tk.LabelFrame(self.window, text='ί����־')
        frame2.pack(side=tk.LEFT, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(frame2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        col_name = ['����', 'ʱ��', '֤ȯ����', '֤ȯ����', '����', '�۸�', '����', '��ע']
        self.tree = ttk.Treeview(frame2, show='headings', columns=col_name, yscrollcommand=scrollbar.set)
        self.tree.pack()
        scrollbar.config(command=self.tree.yview)

        for name in col_name:
            self.tree.heading(name, text=name)
            self.tree.column(name, width=70, anchor=tk.E)
        # ��ť
        frame3 = tk.LabelFrame(self.window)
        frame3.pack(side=tk.LEFT, padx=10, pady=10)
        self.start_bt = ttk.Button(
            frame3, text="����", command=self.start_stop)
        self.start_bt.pack()
        ttk.Button(frame3, text='ˢ��', command=self.refresh_table).pack()
        self.count = 0

        self.window.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.window.after(100, self.update_labels)

        self.window.mainloop()

    def refresh_table(self):
        # ˢ�»�����ί����־
        length = len(trading_messages)
        while self.count < length:
            self.tree.insert('', 0, values=trading_messages[self.count])
            self.count += 1

    def update_labels(self):
        # ʵʱˢ�¹�Ʊ�۸�
        self.stock_name_label['text'] = stock_name
        self.stock_price_label['text'] = str(stock_price)
        self.window.after(3000, self.update_labels)

    def start_stop(self):
        global is_start

        if is_start is False:
            is_start = True
        else:
            is_start = False

        if is_start:
            self.get_items()
            self.start_bt['text'] = 'ֹͣ'
            self.disable_widget()
        else:
            self.enable_widget()
            self.start_bt['text'] = '����'

    def close(self):
        # �ر����ʱ��ֹͣmonitor�߳�
        global is_monitor
        is_monitor = False
        self.window.quit()

    def enable_widget(self):
        self.stock_code_entry['state'] = tk.NORMAL
        self.stop_loss_price_entry['state'] = tk.NORMAL
        self.stop_profit_price_entry['state'] = tk.NORMAL
        self.sell_stock_number_entry['state'] = tk.NORMAL
        self.buy_stock_price_entry['state'] = tk.NORMAL
        self.buy_stock_number_entry['state'] = tk.NORMAL

    def disable_widget(self):
        self.stock_code_entry['state'] = tk.DISABLED
        self.stop_loss_price_entry['state'] = tk.DISABLED
        self.stop_profit_price_entry['state'] = tk.DISABLED
        self.sell_stock_number_entry['state'] = tk.DISABLED
        self.buy_stock_price_entry['state'] = tk.DISABLED
        self.buy_stock_number_entry['state'] = tk.DISABLED

    def get_items(self):
        global items_list

        items_list = []

        # ��Ʊ����
        stock_code = self.stock_code.get().strip()
        if stock_code.isdigit() and len(stock_code) == 6:
            items_list.append(stock_code)
        else:
            items_list.append('')

        # ֹ��۸�
        stock_loss_price = self.stop_loss_price.get().strip()
        if is_digit(stock_loss_price):
            items_list.append(float(stock_loss_price))
        else:
            items_list.append(0)

        # ��дֹӯ�ۣ�Ĭ��Ϊ10000ֹӯ
        stop_profit_price = self.stop_profit_price.get().strip()
        if is_digit(stop_profit_price):
            items_list.append(float(stop_profit_price))
        else:
            items_list.append(10000)

        # ������Ʊ����
        sell_stock_number = self.sell_stock_number.get().strip()
        if sell_stock_number.isdigit():
            items_list.append(sell_stock_number)
        else:
            items_list.append('')

        # ��дͻ������ۣ�Ĭ��ͻ��10000ʱ����
        buy_stock_price = self.buy_stock_price.get().strip()
        if is_digit(buy_stock_price):
            items_list.append(float(buy_stock_price))
        else:
            items_list.append(10000)

        # �����Ʊ����
        buy_stock_price = self.buy_stock_number.get().strip()
        if buy_stock_price.isdigit():
            items_list.append(buy_stock_price)
        else:
            items_list.append('')


if __name__ == '__main__':
    t1 = threading.Thread(target=StockGui)
    t2 = threading.Thread(target=monitor)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    Status API Training Shop Blog About Pricing 

