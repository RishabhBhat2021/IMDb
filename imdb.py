from tkinter import *

import os

import requests
from bs4 import BeautifulSoup
import urllib.request 

from PIL import ImageTk,Image

# Tkinter Window
root = Tk()
root.title('IMDb Rating')
root.config(bg='black')
root.iconbitmap('imdb ico logo.ico')

# Frames to display the information
main_frame = Frame(root,bg='black') 
display_frame = Frame(root,bg='black')

main_frame.pack()

# IMDb Logo 
imdb_logo = ImageTk.PhotoImage(Image.open("imdb logo.png"))
imdb_logo_label = Label(main_frame,image=imdb_logo,bg="black")
imdb_logo_label.pack(padx=20,pady=20)

# Entry Widget
e = Entry(main_frame,font=80,width=20)
e.pack()

# Function to search for the title entered
def search():

    global poster
    global display_frame
    
    # List for containing the cast 
    cast_list = []

    display_frame.pack_forget()

    display_frame = Frame(root,bg='black')
    display_frame.pack()
    
    # Get the text entered in the entry box
    title = e.get()
    e.delete(0,END)

    # Starting a request for the text and then scraping the title name
    result = requests.get(f'https://www.imdb.com/find?q={title}&s=tt&ref_=fn_al_tt_mr')
    src = result.content
    soup = BeautifulSoup(src,'lxml')

    tag = soup.find('td',class_='result_text')

    title_name = tag.text
    title_id = tag.a.attrs['href']
    title_link = f'https://www.imdb.com/{title_id}'

    result_title = requests.get(title_link)
    src_title = result_title.content
    soup_title = BeautifulSoup(src_title,'lxml')
    tag_title = soup_title.find('div',class_='ratingValue')

    title_rating = tag_title.text

    # Title Name
    title_label = Label(display_frame,text=f'{title_name}\nIMDb:{title_rating}',font=("Helvetica",30,'bold'),bg="black",fg="white")
    title_label.grid(row=0,column=1)

    # Poster
    tag_img = soup_title.find('img')
    poster_link = tag_img.attrs['src']
    # Retreiving the Image using urllib
    urllib.request.urlretrieve(poster_link,'poster.png')  

    poster = ImageTk.PhotoImage(Image.open("poster.png"))
    poster_label = Label(display_frame,image=poster,bd=0,bg="black")
    poster_label.grid(row=0,column=0)

    # Cast
    cast_heading_label = Label(display_frame,text='Cast',bg='black',fg='white',font=('Helvetica',15,'bold'))
    cast_heading_label.grid(row=1,column=0,columnspan=2,padx=20,pady=(20,0))

    tags_cast = soup_title.find_all('td',class_='primary_photo')
    for tag_cast in tags_cast:
        cast_list.append(tag_cast.a.img.attrs['alt'])
    cast1 = '\n'.join(cast_list[:8])
    cast2 = '\n'.join(cast_list[8:])

    cast_label1 = Label(display_frame,text=cast1,bg='black',fg='white',font=6)
    cast_label2 = Label(display_frame,text=cast2,bg='black',fg='white',font=6)

    cast_label1.grid(row=2,column=0,padx=(20,0),pady=(0,20))
    cast_label2.grid(row=2,column=1,padx=(0,20),pady=(0,20))

    os.remove("poster.png")


search_button = Button(main_frame,text='Search',command=search,font=20)
search_button.pack(pady=20)

root.mainloop()
