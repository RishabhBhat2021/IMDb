from sys import displayhook
import threading

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

import os

import requests
from bs4 import BeautifulSoup
import urllib.request

BOLD_LARGE_FONT = ("Helveticta", 30, "bold")
BOLD_MEDIUM_FONT = ("Helveticta", 15, "bold")
LARGE_FONT = ("Helveticta", 30)
MEDIUM_FONT = ("Helveticta", 15)
SMALL_FONT = (("Helveticta", 5))


class ImdbApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "IMDb Search Catalogue")
        tk.Tk.iconbitmap(self, default='imdb ico logo.ico')
        tk.Tk.config(self, bg="black")

        # Use self.image for images 
        self.imdb_logo = ImageTk.PhotoImage(Image.open("imdb logo.png"))
        imdb_logo_label = tk.Label(self, image=self.imdb_logo, bg="black")
        imdb_logo_label.pack(padx=10,pady=10)        

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, HistoryPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    ### Getting the page object from this class (main class)
    def get_page(self, page_class):
        return self.frames[page_class]


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg="black")

        self.controller = controller

        self.my_entry = tk.Entry(self, font=MEDIUM_FONT)
        self.my_entry.pack(pady=10)
        
        my_button = ttk.Button(self, text="Search", command=lambda: threading.Thread(target=self.search_title).start())
        my_button.pack(pady=10)

        history_button = ttk.Button(self, text="Show History", command=lambda: controller.show_frame(HistoryPage))
        history_button.pack(pady=10)

        self.display_frame = tk.Frame(self, bg="black")

        self.title_label = tk.Label(self.display_frame, font=BOLD_LARGE_FONT, bg="black", fg="white")

    def search_title(self):

        self.display_frame.pack_forget()
        
        self.title = self.my_entry.get()

        result = requests.get(f'https://www.imdb.com/find?q={self.title}&s=tt&ref_=fn_al_tt_mr')
        src = result.content
        soup = BeautifulSoup(src,'lxml')

        tag = soup.find('td',class_='result_text')

        self.title_name = tag.text

        title_id = tag.a.attrs['href']
        title_link = f'https://www.imdb.com/{title_id}'

        result_title = requests.get(title_link)
        src_title = result_title.content
        soup_title = BeautifulSoup(src_title, 'lxml')
        tag_title = soup_title.find('div', class_='ratingValue')

        self.title_rating = tag_title.text
        self.title_rating = self.title_rating.strip("\n")

        # Title Name
        self.title_label.config(text=f'{self.title_name}\nIMDb: {self.title_rating}')
        self.title_label.grid(row=0, column=1)

        # Poster
        tag_img = soup_title.find('img')
        poster_link = tag_img.attrs['src']
        # Retreiving the Image using urllib
        urllib.request.urlretrieve(poster_link, 'poster.png')  

        self.poster = ImageTk.PhotoImage(Image.open("poster.png"))
        poster_label = tk.Label(self.display_frame, image=self.poster, bd=0, bg="black")
        poster_label.grid(row=0,column=0)

        # Cast
        self.cast_list = []

        self.cast_frame = tk.Frame(self.display_frame, bg="black")
        self.cast_frame.grid(row=2, column=0, columnspan=2)

        cast_heading_label = tk.Label(self.cast_frame, text='Cast', bg='black', fg='white', font=BOLD_MEDIUM_FONT)
        cast_heading_label.pack(padx=20, pady=(20,0))

        tags_cast = soup_title.find_all('td',class_='primary_photo')

        self.cast_textbox = tk.Text(self.cast_frame, bg="black", fg="white")
        self.cast_textbox.pack()

        # make a scrollbar
        scrollbar = tk.Scrollbar(self.cast_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configuring the ScrollBar
        scrollbar.config(command=self.cast_textbox.yview)

        self.cast_textbox.config(yscrollcommand=scrollbar.set)

        for tag_cast in tags_cast:
            cast_list = tag_cast.a.img.attrs['alt'] + "\n"
            self.cast_textbox.insert(tk.END, cast_list)

        history_page = self.controller.get_page(HistoryPage)
        history = self.title_name + " " + self.title_rating + "\n"
        history_page.history_log.insert(tk.END, history)

        self.display_frame.pack()

        os.remove("poster.png")

class HistoryPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg="black")

        self.history_log = tk.Text(self, bg="black", fg="white")
        self.history_log.pack(fill="both", expand=True)

        home_button = ttk.Button(self, text="Return to Home", command=lambda: controller.show_frame(StartPage))
        home_button.pack(pady=10, side="bottom")

        history_label = tk.Label(self, text="Search History", bg="black", fg="white", font=MEDIUM_FONT)
        history_label.pack(pady=10)


def main():
    
    app = ImdbApp()
    app.mainloop()

if __name__ == "__main__":
    main()