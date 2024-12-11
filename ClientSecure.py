import socket
import threading
import tkinter
from tkinter import simpledialog, messagebox, LEFT, RIGHT, BOTTOM, END, Scrollbar, INSERT, Listbox
import time
import pyDes

wowkey = '1689'

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.running = True
        self.nickname = self.get_nickname()

        self.win = tkinter.Tk()
        self.win.title("LAN Secure Chat App")
        self.win.configure(bg="lightgray")
        self.setup_gui()

        recv_thread = threading.Thread(target=self.receive)
        recv_thread.start()

        self.win.mainloop()

    def setup_gui(self):
        self.logo_label = tkinter.Label(self.win, text="LAN Secure Chat App", bg="lightgray", fg="black", font=("Arial", 24, "bold"))
        self.logo_label.pack(pady=20)

        self.text_area = tkinter.Text(self.win, bg="white", fg="black", font=("Arial", 12), wrap=tkinter.WORD)
        self.text_area.pack(expand=True, fill="both", padx=20, pady=(0, 10))
        self.text_area.config(state="disabled")

        scrollbar = Scrollbar(self.win, command=self.text_area.yview)
        scrollbar.pack(side=RIGHT, fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)

        input_frame = tkinter.Frame(self.win, bg="lightgray")
        input_frame.pack(pady=(0, 20))

        self.input_area = tkinter.Text(input_frame, height=3, width=50, font=("Arial", 12), bg="white", fg="black")
        self.input_area.pack(side=LEFT, padx=10, pady=10)

        send_button = tkinter.Button(input_frame, text="Send", bg="navy", fg="white", font=("Arial", 12, "bold"), command=self.write)
        send_button.pack(side=RIGHT, padx=10)

        self.online_users_label = tkinter.Label(self.win, text="Online Users:", bg="lightgray", fg="black", font=("Arial", 12))
        self.online_users_label.pack(pady=(0, 5))

        self.online_users_list = Listbox(self.win, bg="lightgray", fg="black", font=("Arial", 12), height=5)
        self.online_users_list.pack(pady=(0, 10), padx=20, fill="x")

    def get_nickname(self):
        while True:
            nickname = simpledialog.askstring("Nickname", "Please choose a nickname:")
            if not nickname:
                if not messagebox.askretrycancel("Nickname", "Nickname cannot be empty. Retry?"):
                    self.stop()
                continue
            else:
                return nickname

    def write(self):
        message = f"[{time.strftime('%H:%M:%S')}] {self.nickname}: {self.input_area.get('1.0', 'end')}"
        encrypted_message = pyDes.triple_des(wowkey.ljust(24)).encrypt(message, padmode=2) 
        self.sock.send(encrypted_message)
        self.input_area.delete('1.0', "end")

    def stop(self):
        self.running = False
        self.sock.close()
        self.win.destroy()

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode("utf-8")
                if message == "NICK":
                    self.sock.send(self.nickname.encode("utf-8"))
                else:
                    if message.startswith("Online Users:"):
                        online_users = message.split(":")[1].strip().split(", ")
                        self.update_online_users(online_users)
                    else:
                        self.text_area.config(state='normal')
                        self.text_area.insert(END, message)
                        self.text_area.see(END)
                        self.text_area.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                self.stop()

    def update_online_users(self, online_users):
        self.online_users_list.delete(0, END)
        for user in online_users:
            self.online_users_list.insert(END, user)

HOST = simpledialog.askstring("IP : ", "Please write host IP")
PORT = 59429
Client(HOST, PORT)
