import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

import os

import threading

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
        imdb_logo_label.pack(padx=10,pady=(20,10))        

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, SearchPage, HistoryPage, LoadingPage, ErrorPage):
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
        
        buttons_frame = tk.Frame(self, bg="black")
        buttons_frame.pack(pady=10)

        self.my_entry = tk.Entry(buttons_frame, font=MEDIUM_FONT)
        self.my_entry.pack(padx=10, pady=10, side=tk.LEFT)

        my_button = ttk.Button(buttons_frame, text="Search", command = self.search)
        my_button.pack(padx=10, pady=10, side=tk.LEFT)

        history_button = ttk.Button(buttons_frame, text="Show History", command=lambda: controller.show_frame(HistoryPage))
        history_button.pack(padx=10, pady=10, side=tk.RIGHT)

    def search(self):

        self.controller.show_frame(LoadingPage)

        search_page = self.controller.get_page(SearchPage)

        threading.Thread(target=search_page.search_title).start()


class SearchPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg="black")

        self.controller = controller

        home_button = ttk.Button(self, text="Go Back", command=lambda: controller.show_frame(StartPage))
        home_button.pack(pady=10)

        self.main_frame = tk.Frame(self, bg="black")

        self.title_frame = tk.Frame(self.main_frame, bg="black")

        self.title_label = tk.Label(self.title_frame, font=BOLD_LARGE_FONT, bg="black", fg="white")
        self.poster_label = tk.Label(self.title_frame, bd=0, bg="black")

        self.cast_frame = tk.Frame(self.main_frame, bg="black")

        self.cast_textbox = tk.Text(self.cast_frame, bg="black", fg="white", font=MEDIUM_FONT, width=30, height=15)
        self.cast_textbox.tag_configure("center", justify='center')   # To center allign the text
        self.cast_textbox.tag_add("center", "1.0", "end")             # in the Text Box: cast_textbox

        # make a scrollbar
        self.scrollbar = tk.Scrollbar(self.main_frame)

        self.cast_heading_label = tk.Label(self.cast_frame, text='Cast', bg='black', fg='white', font=BOLD_MEDIUM_FONT)
        
    def search_title(self):

        home_page = self.controller.get_page(StartPage)
        self.title = home_page.my_entry.get()

        try:
            result = requests.get(f'https://www.imdb.com/find?q={self.title}&s=tt&ref_=fn_al_tt_mr')
            src = result.content
            soup = BeautifulSoup(src,'lxml')

            tag = soup.find('td',class_='result_text')

            self.title_name = tag.text

            title_id = tag.a.attrs['href']
            self.title_link = f'https://www.imdb.com/{title_id}'

            result_title = requests.get(self.title_link)
            src_title = result_title.content
            soup_title = BeautifulSoup(src_title, 'lxml')
            tag_title = soup_title.find('div', class_='ratingValue')

            self.title_rating = tag_title.text
            self.title_rating = self.title_rating.strip("\n")

            # Title Name
            self.title_label.config(text=f'{self.title_name}\nIMDb: {self.title_rating}')
            self.title_label.pack(pady=10)

            # Poster
            self.tag_img = soup_title.find('img')
            self.poster_link = self.tag_img.attrs['src']
            # Retreiving the Image using urllib
            urllib.request.urlretrieve(self.poster_link, 'poster.png')  

            self.poster = ImageTk.PhotoImage(Image.open("poster.png"))
            self.poster_label.config(image=self.poster)
            self.poster_label.pack(pady=10)

            # Cast
            self.cast_list = ""

            self.cast_heading_label.pack(padx=20, pady=(20,15))

            self.tags_cast = soup_title.find_all('td',class_='primary_photo')
            
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Configuring the ScrollBar
            self.scrollbar.config(command=self.cast_textbox.yview)

            self.cast_textbox.config(yscrollcommand=self.scrollbar.set)

            self.cast_textbox.delete("1.0", tk.END)

            for self.tag_cast in self.tags_cast:
                self.cast_list = self.tag_cast.a.img.attrs['alt'] + "\n"
                self.cast_textbox.insert("1.0", self.cast_list, "center")

            self.cast_frame.pack(padx=10, side=tk.RIGHT)
            self.cast_textbox.pack()
            self.title_frame.pack(pady=10, padx=10, side=tk.LEFT)
            self.main_frame.pack(pady=10)

            history_page = self.controller.get_page(HistoryPage)
            history = self.title_name + " " + self.title_rating + "\n"
            history_page.history_log.insert(tk.END, history)

            self.controller.show_frame(SearchPage)
        
        except:
            self.controller.show_frame(ErrorPage)


class HistoryPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg="black")

        self.controller = controller

        history_label = tk.Label(self, text="Search History", bg="black", fg="white", font=MEDIUM_FONT)
        history_label.pack(pady=10, side=tk.TOP)

        self.history_log = tk.Text(self, bg="black", fg="white", font=40)
        self.history_log.pack(fill="both", expand=True)

        home_button = ttk.Button(self, text="Return to Home", command=lambda: controller.show_frame(StartPage))
        home_button.pack(pady=10, side=tk.BOTTOM)

    def delete_last(self):

        search_page = self.controller
        search_page.pack_forget()


class LoadingPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg="black")

        self.controller = controller

        loading_label = tk.Label(self, text="Searching...\nPlease Wait", bg="black", fg="white", font=BOLD_MEDIUM_FONT)
        loading_label.pack()


class ErrorPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg="black")

        self.controller = controller

        not_found_label = tk.Label(self, text="Oops...\nSome Error occured", bg="black", fg="white", font=BOLD_MEDIUM_FONT)
        not_found_label.pack()

        home_button = ttk.Button(self, text="Return to Home", command=lambda: controller.show_frame(StartPage))
        home_button.pack(pady=10, side=tk.BOTTOM)


def main():
    
    app = ImdbApp()
    app.mainloop()
    os.remove("poster.png")

if __name__ == "__main__":
    main()