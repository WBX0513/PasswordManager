import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import os
import subprocess

PWD_FILE = "passwords.txt"

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("密码管理器")
        self.root.geometry("650x480")
        self.root.configure(bg='#f0f0f0')
        self.create_widget()
        self.load_data()

    def create_widget(self):
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=45)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="账号密码管理系统", font=('Arial',14,'bold'),bg='#2c3e50',fg='white').pack(pady=8)

        # 表格区域
        table_frame = tk.LabelFrame(self.root, text="账号列表 | 点击网站打开链接，点击密码复制",
                                    font=('Arial',11,'bold'),bg='#f0f0f0',padx=8,pady=5)
        table_frame.pack(fill=tk.BOTH,expand=True,padx=10,pady=5)

        cols = ("site", "user", "pwd")
        self.tree = ttk.Treeview(table_frame,columns=cols,show="headings")
        self.tree.heading("site",text="网站地址")
        self.tree.heading("user",text="用户名")
        self.tree.heading("pwd",text="密码")
        self.tree.column("site",width=230)
        self.tree.column("user",width=160)
        self.tree.column("pwd",width=180)
        self.tree.pack(fill=tk.BOTH,expand=True)

        # 底部按钮区
        btn_frame = tk.Frame(self.root,bg='#f0f0f0')
        btn_frame.pack(pady=8)
        tk.Button(btn_frame,text="新增",bg='#27ae60',fg='white',width=9,command=self.add_item).grid(row=0,column=0,padx=6)
        tk.Button(btn_frame,text="修改",bg='#3498db',fg='white',width=9,command=self.edit_item).grid(row=0,column=1,padx=6)
        tk.Button(btn_frame,text="删除",bg='#e74c3c',fg='white',width=9,command=self.del_item).grid(row=0,column=2,padx=6)

        self.tree.bind("<Button-1>",self.on_click_cell)

    # 自定义弹窗：新增/修改共用，三个输入框、置顶、完成/取消按钮
    def input_dialog(self, title, old_site="", old_user="", old_pwd=""):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.attributes("-topmost", True) # 窗口置顶
        win.geometry("380x220")
        win.configure(bg="#f0f0f0")
        win.grab_set()

        res = {"site":old_site,"user":old_user,"pwd":old_pwd,"ok":False}

        tk.Label(win,text="网站地址：",bg="#f0f0f0").pack(pady=(10,2))
        e1 = tk.Entry(win,width=45)
        e1.insert(0,old_site)
        e1.pack()

        tk.Label(win,text="用户名：",bg="#f0f0f0").pack(pady=(6,2))
        e2 = tk.Entry(win,width=45)
        e2.insert(0,old_user)
        e2.pack()

        tk.Label(win,text="密码：",bg="#f0f0f0").pack(pady=(6,2))
        e3 = tk.Entry(win,width=45)
        e3.insert(0,old_pwd)
        e3.pack()

        def confirm():
            res["site"] = e1.get().strip()
            res["user"] = e2.get().strip()
            res["pwd"] = e3.get().strip()
            res["ok"] = True
            win.destroy()
        def cancel():
            win.destroy()

        btn_f = tk.Frame(win,bg="#f0f0f0")
        btn_f.pack(pady=12)
        tk.Button(btn_f,text="完成",bg="#27ae60",fg="white",command=confirm,width=8).grid(row=0,column=0,padx=8)
        tk.Button(btn_f,text="取消",bg="#e74c3c",fg="white",command=cancel,width=8).grid(row=0,column=1,padx=8)

        self.root.wait_window(win)
        return res

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        if not os.path.exists(PWD_FILE):
            return
        with open(PWD_FILE,"r",encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if not line:continue
                site,user,pwd = line.split("|")
                hide = "●"*len(pwd)
                self.tree.insert("",tk.END,values=(site,user,hide),tags=(pwd,))

    def save_all(self):
        lst = []
        for item in self.tree.get_children():
            val = self.tree.item(item,"values")
            real = self.tree.item(item,"tags")[0]
            lst.append(f"{val[0]}|{val[1]}|{real}")
        with open(PWD_FILE,"w",encoding="utf-8") as f:
            f.write("\n".join(lst))

    def on_click_cell(self,ev):
        sel = self.tree.focus()
        if not sel:return
        col_idx = int(self.tree.identify_column(ev.x)[1:])-1
        vals = self.tree.item(sel,"values")
        real_pwd = self.tree.item(sel,"tags")[0]
        if col_idx ==0:
            url = vals[0]
            if not url.startswith(("http://","https://")):
                url = "https://"+url
            webbrowser.open(url)
        elif col_idx ==2:
            subprocess.run(["clip"],input=real_pwd.encode("utf-8"),shell=True)
            messagebox.showinfo("提示","密码已复制剪贴板")

    def add_item(self):
        ret = self.input_dialog("新增账号信息")
        if not ret["ok"]:
            return
        site,user,pwd = ret["site"],ret["user"],ret["pwd"]
        if not all([site,user,pwd]):
            messagebox.showwarning("提示","三项内容不能为空")
            return
        hide = "●"*len(pwd)
        self.tree.insert("",tk.END,values=(site,user,hide),tags=(pwd,))
        self.save_all()

    def edit_item(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("提示","请选中一行")
            return
        old_s,old_u,_ = self.tree.item(sel,"values")
        old_p = self.tree.item(sel,"tags")[0]
        ret = self.input_dialog("修改账号信息",old_s,old_u,old_p)
        if not ret["ok"]:
            return
        ns,nu,np = ret["site"],ret["user"],ret["pwd"]
        if not all([ns,nu,np]):
            messagebox.showwarning("提示","三项内容不能为空")
            return
        self.tree.item(sel,values=(ns,nu,"●"*len(np)),tags=(np,))
        self.save_all()

    def del_item(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("提示","请选中一行")
            return
        if messagebox.askyesno("确认","确定删除本条？"):
            self.tree.delete(sel)
            self.save_all()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()
