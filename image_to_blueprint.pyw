from PIL import Image, ImageOps, ImageTk
import tkinter as tk
from tkinter import filedialog, ttk
import json, uuid, os, math, copy

### functions

def refresh_preview(): # called whenever the image is changed
    global preview_image_label, preview_imageTk, preview_image, preview_rotation, flip_state, mirror_state
    if flip.get() != flip_state:
        preview_image = ImageOps.flip(preview_image)
        flip_state = flip.get()
    if mirror.get() != mirror_state:
        preview_image = ImageOps.mirror(preview_image)
        mirror_state = mirror.get()
    if preview_rotation[0] != None:
        preview_imageTk = ImageTk.PhotoImage(preview_image.transpose(preview_rotation[0]))
    else:
        preview_imageTk = ImageTk.PhotoImage(preview_image)
    preview_image_label.configure(image = preview_imageTk)

def file_select_window(): # selecting the image
    global preview_image_label, preview_imageTk, preview_image, image_path, flip, flip_state, mirror, mirror_state, preview_rotation
    image_path = None
    image_path = tk.filedialog.askopenfilename(initialdir = "/", title = "Select Image", filetypes = (("Image Files","*.png *.jpeg *.jpg *.jfif *.bmp *.tiff *.webp *.ppm"),("All Files","*.*"))) # image path
    if image_path:
        root.title("Pixel Art Converter - " + os.path.basename(image_path))
    else:
        root.title("Pixel Art Converter")
    preview_image_label.destroy()
    preview_image_label = tk.Label(root)
    preview_imageTk = None
    preview_image = None
    flip_state = False
    mirror_state = False
    if image_path:
        file_select_button.configure(style = "TButton")
        preview_image = Image.open(image_path)
        if preview_image.size[0] == preview_image.size[1]:
            preview_image = preview_image.resize((475, 475), Image.LANCZOS)
        elif preview_image.size[0] > preview_image.size[1]: # width greater than height
            preview_image = preview_image.resize((475, round(475/preview_image.size[0] * preview_image.size[1])), Image.LANCZOS)
            bg = Image.new("RGBA", (475, 475), (0, 0, 0, 0))
            bg.paste(preview_image, (0, math.floor(( 475 - preview_image.size[1] ) / 2 )))
            preview_image = bg
            del bg
        elif preview_image.size[1] > preview_image.size[0]: # height greater than width
            preview_image = preview_image.resize((round(475/preview_image.size[1] * preview_image.size[0]), 475), Image.LANCZOS)
            bg = Image.new("RGBA", (475, 475), (0, 0, 0, 0))
            bg.paste(preview_image, (math.floor(( 475 - preview_image.size[0] ) / 2 ), 0))
            preview_image = bg
            del bg
        refresh_preview()
        if show_preview.get() == True:
            preview_image_label.grid(column = 0, row = 10, columnspan = 4, padx = 2, pady = 2)

def save_select_window(): # if using json saving, select the json file
    global save_path
    save_path = None
    save_path = tk.filedialog.askopenfilename(initialdir = "/", title = "Save As", filetypes = (("JSON Files","*.json"),("All Files","*.*"))) # save path
    if save_path:
        file_save_button.configure(style = "TButton")

def save_type_change(): # called when the type of saving is changed
    blueprint_name_box.grid_forget()
    blueprint_name_label.grid_forget()
    file_save_button.grid_forget()
    file_select_button.grid_forget()
    if save_type.get() == "blueprint":
        blueprint_name_box.grid(column = 2, row = 1, columnspan = 2, padx = 2, pady = 2)
        blueprint_name_label.grid(column = 1, row = 1, padx = 2, pady = 2)
        file_select_button.grid(column = 0, row = 1, padx = 2, pady = 2)
    elif save_type.get() == "json":
        file_save_button.grid(column = 2, row = 1, columnspan = 2, padx = 2, pady = 2)
        file_select_button.grid(column = 0, row = 1, columnspan = 2, padx = 2, pady = 2)

def backplate_change(): # called when the state of the backplate checkbox is changed
    if backplate.get():
        backplate_checkbox.grid_forget()
        backplate_checkbox.grid(column = 0, row = 2, padx = 2, pady = 4)
        backplate_checkbox.configure(text = "Backplate Material:")
        backplate_material_dropdown.grid(column = 1, row = 2, padx = 2, pady = 4)
        backplate__reverse_checkbox.grid(column = 2, row = 2, padx = 2, pady = 4)
        backplate_color_button.grid(column = 3, row = 2, padx = 2, pady = 2)
    else:
        backplate_checkbox.grid_forget()
        backplate_checkbox.grid(column = 0, row = 2, columnspan = 4, padx = 2, pady = 4)
        backplate_checkbox.configure(text = "Generate Backplate (layer of blocks behind image to improve visibility)")
        backplate_material_dropdown.grid_forget()
        backplate__reverse_checkbox.grid_forget()
        backplate_color_button.grid_forget()

def backplate_color_window(): # called when the user click the color picker button, opens the color picker window
    def return_color_set(color): # deals with the color and closes the color picker
        global backplate_color
        # style.configure("Backplate_Color.TButton", background = "#" + color)
        if check_color_valid(color):
            backplate_color = color.strip("#")
            backplate_color_picker.destroy()
    def check_color_valid(color): # makes sure the color is a valid hex code because of the option to enter a custom color
        valid_color = True
        color_list = list()
        if not color.startswith("#"):
            valid_color = False
        if len(color) != 7:
            valid_color = False
        for x in color.strip("#"):
            color_list.append(x)
        for x in color_list:
            if x not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"):
                valid_color = False
        if not valid_color:
            style.configure("Custom_Color_Label.TLabel", background = "#36393f", foreground = "#ef5034")
            custom_color_label.configure(text = "Input a valid hex color:")
        # elif not valid_color:
        #     style.configure("Custom_Color_Label.TLabel", background = "#36393f", foreground = "#ffffff")
        #     custom_color_label.configure(text = "Or use custom color:")
        return valid_color
    def on_entry_click(event):
        if custom_color_entry.get() == "ex. #222222":
            custom_color_entry.delete(0, "end")
            custom_color_entry.insert(0, "#")
            style.configure("Custom_Color_Entry.TEntry", foreground = "#000000")
            style.configure("Custom_Color_Label.TLabel", background = "#36393f", foreground = "#ffffff")
            custom_color_label.configure(text = "Or use custom color:")
    def on_focusout(event):
        if custom_color_entry.get() in ("#", ""):
            custom_color_entry.delete(0, "end")
            custom_color_entry.insert(0, "ex. #222222")
            style.configure("Custom_Color_Entry.TEntry", foreground = "#7f7f7f")


    backplate_color_picker = tk.Toplevel(root)
    backplate_color_picker.configure(bg = "#36393f") # discord background color lol because #eeeeee, one of the button colors, is actually the default background color
    backplate_color_picker.title("Pick Backplate Color:")
    backplate_color_picker.resizable(False, False)
    backplate_color_picker.geometry("685x225")

    style.configure("Custom_Color_Entry.TEntry", background = "#ffffff", foreground = "#7f7f7f")
    style.configure("Custom_Color_Label.TLabel", background = "#36393f", foreground = "#ffffff")
    # custom_color = tk.StringVar()
    
    custom_color_label = ttk.Label(backplate_color_picker, text = "Or use custom color:", style = "Custom_Color_Label.TLabel")
    custom_color_label.place(x = 555, y = 5, width = 125, height = 21)

    custom_color_entry = ttk.Entry(backplate_color_picker, style = "Custom_Color_Entry.TEntry")
    custom_color_entry.insert(0, "ex. #222222")
    custom_color_entry.bind('<FocusIn>', on_entry_click)
    custom_color_entry.bind('<FocusOut>', on_focusout)
    custom_color_entry.place(x = 555, y = 31, width = 125, height = 21)

    set_custom_color = ttk.Button(backplate_color_picker, text = "Use Color", command = lambda: return_color_set(custom_color_entry.get()))
    set_custom_color.place(x = 555, y = 57, width = 125, height = 25)

    ### using a for loop instead of brute force didn't work because the x and y were the current values and not the values when the button was re-defined
    # color_list = (("#eeeeee", "#f5f071", "#cbf66f", "#68ff88", "#7eeded", "#4c6fe3", "#ae79f0", "#ee7bf0", "#f06767", "#eeaf5c"), ("#7f7f7f", "#e2db13", "#a0ea00", "#19e753", "#2ce6e6", "#0a3ee2", "#7514ed", "#cf11d2", "#d02525", "#df7f00"), ("#4a4a4a", "#817c00", "#577d07", "#0e8031", "#118787", "#0f2e91", "#500aa6", "#720a74", "#7c0000", "#673b00"), ("#222222", "#323000", "#375000", "#064023", "#0a4444", "#0a1d5a", "#35086c", "#520653", "#560202", "#472800"))
    # for x in range(4):
    #     for y in range(10):
    #         curr_button = tk.Button(backplate_color_picker, bg = color_list[x][y], activebackground = color_list[x][y], relief = tk.GROOVE, bd = 0, command = lambda: print(bg))
    #         curr_button.place(x = y * 55 + 5, y = x * 55 + 5, width = 50, height = 50)
    
    ### brute force :(
    ### using tk buttons instead of ttk because they can be fully colored, also makes for a cleaner experience without any background or border
    button = tk.Button(backplate_color_picker, bg = "#eeeeee", activebackground = "#eeeeee", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#eeeeee"))
    button.place(x = 5, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#f5f071", activebackground = "#f5f071", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#f5f071"))
    button.place(x = 60, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#cbf66f", activebackground = "#cbf66f", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#cbf66f"))
    button.place(x = 115, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#68ff88", activebackground = "#68ff88", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#68ff88"))
    button.place(x = 170, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#7eeded", activebackground = "#7eeded", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#7eeded"))
    button.place(x = 225, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#4c6fe3", activebackground = "#4c6fe3", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#4c6fe3"))
    button.place(x = 280, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#ae79f0", activebackground = "#ae79f0", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#ae79f0"))
    button.place(x = 335, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#ee7bf0", activebackground = "#ee7bf0", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#ee7bf0"))
    button.place(x = 390, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#f06767", activebackground = "#f06767", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#f06767"))
    button.place(x = 445, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#eeaf5c", activebackground = "#eeaf5c", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#eeaf5c"))
    button.place(x = 500, y = 5, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#7f7f7f", activebackground = "#7f7f7f", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#7f7f7f"))
    button.place(x = 5, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#e2db13", activebackground = "#e2db13", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#e2db13"))
    button.place(x = 60, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#a0ea00", activebackground = "#a0ea00", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#a0ea00"))
    button.place(x = 115, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#19e753", activebackground = "#19e753", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#19e753"))
    button.place(x = 170, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#2ce6e6", activebackground = "#2ce6e6", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#2ce6e6"))
    button.place(x = 225, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#0a3ee2", activebackground = "#0a3ee2", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#0a3ee2"))
    button.place(x = 280, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#7514ed", activebackground = "#7514ed", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#7514ed"))
    button.place(x = 335, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#cf11d2", activebackground = "#cf11d2", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#cf11d2"))
    button.place(x = 390, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#d02525", activebackground = "#d02525", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#d02525"))
    button.place(x = 445, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#df7f00", activebackground = "#df7f00", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#df7f00"))
    button.place(x = 500, y = 60, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#4a4a4a", activebackground = "#4a4a4a", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#4a4a4a"))
    button.place(x = 5, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#817c00", activebackground = "#817c00", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#817c00"))
    button.place(x = 60, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#577d07", activebackground = "#577d07", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#577d07"))
    button.place(x = 115, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#0e8031", activebackground = "#0e8031", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#0e8031"))
    button.place(x = 170, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#118787", activebackground = "#118787", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#118787"))
    button.place(x = 225, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#0f2e91", activebackground = "#0f2e91", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#0f2e91"))
    button.place(x = 280, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#500aa6", activebackground = "#500aa6", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#500aa6"))
    button.place(x = 335, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#720a74", activebackground = "#720a74", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#720a74"))
    button.place(x = 390, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#7c0000", activebackground = "#7c0000", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#7c0000"))
    button.place(x = 445, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#673b00", activebackground = "#673b00", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#673b00"))
    button.place(x = 500, y = 115, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#222222", activebackground = "#222222", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#222222"))
    button.place(x = 5, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#323000", activebackground = "#323000", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#323000"))
    button.place(x = 60, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#375000", activebackground = "#375000", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#375000"))
    button.place(x = 115, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#064023", activebackground = "#064023", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#064023"))
    button.place(x = 170, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#0a4444", activebackground = "#0a4444", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#0a4444"))
    button.place(x = 225, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#0a1d5a", activebackground = "#0a1d5a", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#0a1d5a"))
    button.place(x = 280, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#35086c", activebackground = "#35086c", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#35086c"))
    button.place(x = 335, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#520653", activebackground = "#520653", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#520653"))
    button.place(x = 390, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#560202", activebackground = "#560202", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#560202"))
    button.place(x = 445, y = 170, width = 50, height = 50)
    button = tk.Button(backplate_color_picker, bg = "#472800", activebackground = "#472800", relief = tk.GROOVE, bd = 0, command = lambda: return_color_set("#472800"))
    button.place(x = 500, y = 170, width = 50, height = 50)

def flip_change(): # called when the flip checkbox is changed
    global image_path
    if image_path:
        refresh_preview()

def mirror_change(): # called when the mirror checkbox is changed
    global image_path
    if image_path:
        refresh_preview()

def rotation_change(event): # called when the rotation combobox is changed (using events instead of command)
    global preview_image, rotation_dict, rotation_string, preview_rotation
    if preview_image:
        preview_rotation = rotation_dict[rotation_string.get()]
        refresh_preview()

def resize_change(): # called when the resize type is changed
    resize_scale_box.grid_forget()
    resize_scale_box_label.grid_forget()
    resize_dimension_x_box_label.grid_forget()
    resize_dimension_x_box.grid_forget()
    resize_dimension_y_box_label.grid_forget()
    resize_dimension_y_box.grid_forget()
    resize_filter_dropdown.grid_forget()
    resize_filter_label.grid_forget()
    if resize_type.get() == "scale":
        resize_scale_box_label.grid(column = 0, row = 7, columnspan = 2, padx = 2, pady = 2)
        resize_scale_box.grid(column = 2, row = 7, columnspan = 2, padx = 2, pady = 2)
        resize_filter_dropdown.grid(column = 2, row = 8, padx = 2, pady = 2)
        resize_filter_label.grid(column = 1, row = 8, padx = 2, pady = 2)
    elif resize_type.get() == "dimension":
        resize_dimension_x_box_label.grid(column = 0, row = 7, padx = 2, pady = 2)
        resize_dimension_x_box.grid(column = 1, row = 7, padx = 2, pady = 2)
        resize_dimension_y_box_label.grid(column = 2, row = 7, padx = 2, pady = 2)
        resize_dimension_y_box.grid(column = 3, row = 7, padx = 2, pady = 2)
        resize_filter_dropdown.grid(column = 2, row = 8, padx = 2, pady = 2)
        resize_filter_label.grid(column = 1, row = 8, padx = 2, pady = 2)

def show_preview_change(): # called when the preview checkbox is changed
    global preview_image_label, image_path
    preview_image_label.grid_forget()
    if show_preview.get() == True and image_path:
        preview_image_label = tk.Label(root, image = preview_imageTk)
        preview_image_label.grid(column = 0, row = 10, columnspan = 4, padx = 2, pady = 2)

def export(): # first step of exporting, checks if all the variables are valid and if not highlights them in red
    valid_settings = True
    if image_path:
        file_select_button.configure(style = "TButton")
    else:
        file_select_button.configure(style = "Red.TButton")
        valid_settings = False
    if save_path:
        file_save_button.configure(style = "TButton")
    else:
        if save_type.get() == "json":
            file_save_button.configure(style = "Red.TButton")
            valid_settings = False
    try:
        int(opacity_threshold.get())
        opacity_threshold_label.configure(text = "Min Pixel Opacity (0-255):", style = "TLabel")
    except:
        opacity_threshold_label.configure(text = "Must be an integer:", style = "Red.TLabel")
        valid_settings = False
    try:
        float(resize_scale.get())
        resize_scale_box_label.configure(text = "Scale Factor:", style = "TLabel")
    except:
        if resize_type.get() == "scale":
            resize_scale_box_label.configure(text = "Must be a number:", style = "Red.TLabel")
            valid_settings = False
    try:
        int(resize_dimension_x_box.get())
        resize_dimension_x_box_label.configure(text = "Image Width:", style = "TLabel")
    except:
        if resize_type.get() == "dimension":
            resize_dimension_x_box_label.configure(text = "Must be an integer:", style = "Red.TLabel")
            valid_settings = False
    try:
        int(resize_dimension_y_box.get())
        resize_dimension_y_box_label.configure(text = "Image Height:", style = "TLabel")
    except:
        if resize_type.get() == "dimension":
            resize_dimension_y_box_label.configure(text = "Must be an integer:", style = "Red.TLabel")
            valid_settings = False
    if valid_settings:
        export_image()
        export_button.config(text = "Export", state = "normal")

def export_image(): # called by export(), actually exports the image to the blueprint
    export_button.config(text = "Prepping...", state = "disabled") # button state that is almost never seen lol
    root.update()
    bp_uuid = str(uuid.uuid4())
    raw_json = {"bodies": [{"childs": []}], "version": 3}
    description_json = {"description": bp_uuid, "localId": bp_uuid, "name": blueprint_name.get(), "type": "Blueprint", "version": 0}
    image = Image.open(image_path)
    image_copy = image
    if not flip.get(): # images are upside down by default
        image = ImageOps.flip(image)
    if mirror.get():
        image = ImageOps.mirror(image)
    if preview_rotation[1] != None:
        image = image.transpose(preview_rotation[1])
    if image.mode != "RGBA": # transparency support
        image = image.convert("RGBA")
    if resize_type.get() == "scale":
        image = image.resize((round(image.size[0] * float(resize_scale.get())), round(image.size[1] * float(resize_scale.get()))), Image.HAMMING)
    elif resize_type.get() == "dimension":
        image = image.resize((int(resize_dimension_x.get()), int(resize_dimension_y.get())), filter_dict[filter_string.get()])
    export_button.config(text = "Converting...")
    root.update()
    x = 0
    while x < image.size[0]: # iterate over the image checking the color
        y = 0
        while y < image.size[1] + 1:
            if y > 0:
                r = str(format(image.getpixel((x, y - 1))[0], "02x")) # convert 0-255 to 00-ff
                g = str(format(image.getpixel((x, y - 1))[1], "02x"))
                b = str(format(image.getpixel((x, y - 1))[2], "02x"))
                rgb = str(r + g + b)
                if image.getpixel((x, y - 1))[3] >= int(opacity_threshold.get()): # only save if the pixel is above the threshold
                    if plane.get() == "xy": # save the block to the json
                        raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": 1, "z": 1}, "color": rgb, "pos": {"x": x, "y": y, "z": 0}, "shapeId": material_dict[material_string.get()], "xaxis": 1, "zaxis": 3})
                    elif plane.get() == "xz":
                        raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": 1, "z": 1}, "color": rgb, "pos": {"x": x, "y": 0, "z": y}, "shapeId": material_dict[material_string.get()], "xaxis": 1, "zaxis": 3})
                    elif plane.get() == "yz":
                        raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": 1, "z": 1}, "color": rgb, "pos": {"x": 0, "y": x, "z": y}, "shapeId": material_dict[material_string.get()], "xaxis": 1, "zaxis": 3})
            elif x == round(image.size[0] / 2):
                if plane.get() == "xy": # save the block to the json
                    raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": 1, "z": 1}, "color": "000000", "pos": {"x": x, "y": y, "z": 0}, "shapeId": material_dict["Plastic"], "xaxis": 1, "zaxis": 3})
                elif plane.get() == "xz":
                    raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": 1, "z": 1}, "color": "000000", "pos": {"x": x, "y": 0, "z": y}, "shapeId": material_dict["Plastic"], "xaxis": 1, "zaxis": 3})
                elif plane.get() == "yz":
                    raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": 1, "z": 1}, "color": "000000", "pos": {"x": 0, "y": x, "z": y}, "shapeId": material_dict["Plastic"], "xaxis": 1, "zaxis": 3})
            y += 1
        x += 1
    if backplate.get():
        if not backplate_reverse.get():
            if plane.get() == "xy": # save the block to the json
                raw_json["bodies"][0]["childs"].append({"bounds": {"x": image.size[0], "y": image.size[1], "z": 1}, "color": backplate_color, "pos": {"x": 0, "y": 0, "z": -1}, "shapeId": material_dict[backplate_material_string.get()], "xaxis": 1, "zaxis": 3})
            elif plane.get() == "xz":
                raw_json["bodies"][0]["childs"].append({"bounds": {"x": image.size[0], "y": 1, "z": image.size[1]}, "color": backplate_color, "pos": {"x": 0, "y": 1, "z": 0}, "shapeId": material_dict[backplate_material_string.get()], "xaxis": 1, "zaxis": 3})
            elif plane.get() == "yz":
                raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": image.size[0], "z": image.size[1]}, "color": backplate_color, "pos": {"x": 1, "y": 0, "z": 0}, "shapeId": material_dict[backplate_material_string.get()], "xaxis": 1, "zaxis": 3})
        elif backplate_reverse.get():
            if plane.get() == "xy": # save the block to the json
                raw_json["bodies"][0]["childs"].append({"bounds": {"x": image.size[0], "y": image.size[1], "z": 1}, "color": backplate_color, "pos": {"x": 0, "y": 0, "z": 1}, "shapeId": material_dict[backplate_material_string.get()], "xaxis": 1, "zaxis": 3})
            elif plane.get() == "xz":
                raw_json["bodies"][0]["childs"].append({"bounds": {"x": image.size[0], "y": 1, "z": image.size[1]}, "color": backplate_color, "pos": {"x": 0, "y": -1, "z": 0}, "shapeId": material_dict[backplate_material_string.get()], "xaxis": 1, "zaxis": 3})
            elif plane.get() == "yz":
                raw_json["bodies"][0]["childs"].append({"bounds": {"x": 1, "y": image.size[0], "z": image.size[1]}, "color": backplate_color, "pos": {"x": -1, "y": 0, "z": 0}, "shapeId": material_dict[backplate_material_string.get()], "xaxis": 1, "zaxis": 3})
    export_button.config(text = "Saving...")
    root.update()
    if save_type.get() == "blueprint":
        user_folder_files = []
        for obj in os.listdir(os.getenv("APPDATA") + "\\Axolot Games\\Scrap Mechanic\\User"):
            if str(obj).startswith("User_"):
                user_folder_files.append(str(obj))
        if len(user_folder_files) != 1:
            print("more than one folder; user must have modified folder")
        blueprint_folder = os.getenv("APPDATA") + "\\Axolot Games\\Scrap Mechanic\\User\\" + user_folder_files[0] + "\\Blueprints\\" + bp_uuid
        os.mkdir(blueprint_folder)
        with open(blueprint_folder + "\\blueprint.json", "w") as f:
            f.truncate()
            json.dump(raw_json, f)
        with open(blueprint_folder + "\\description.json", "w") as f:
            f.truncate()
            json.dump(description_json, f, indent = 2)
        image_copy.resize((128, 128), Image.LANCZOS).save(blueprint_folder + "\\icon.png", "png")
    elif save_type.get() == "json":
        with open(save_path, "w") as f: # write the json to the file
            f.truncate()
            json.dump(raw_json, f)

### tkinter essentials

root = tk.Tk()
root.title("Pixel Art Converter")
root.resizable(False, False)
# root.configure(bg = "#36393f")

### variables

save_type = tk.StringVar()
save_type.set("blueprint")
blueprint_name = tk.StringVar()
blueprint_name.set("Image")
backplate = tk.BooleanVar()
backplate_material_string = tk.StringVar()
backplate_material_string.set("Plastic")
backplate_reverse = tk.BooleanVar()
backplate_color = "222222"
flip = tk.BooleanVar()
flip_state = False
mirror = tk.BooleanVar()
mirror_state = False
opacity_threshold = tk.StringVar()
opacity_threshold.set("255")
material_dict = {"Scrap Stone": "30a2288b-e88e-4a92-a916-1edbfc2b2dac", "Concrete 1": "a6c6ce30-dd47-4587-b475-085d55c6a3b4", "Concrete 2": "ff234e42-5da4-43cc-8893-940547c97882", "Concrete 3": "e281599c-2343-4c86-886e-b2c1444e8810", "Scrap Wood": "1fc74a28-addb-451a-878d-c3c605d63811", "Wood 1": "df953d9c-234f-4ac2-af5e-f0490b223e71", "Wood 2": "1897ee42-0291-43e4-9645-8c5a5d310398", "Wood 3": "061b5d4b-0a6a-4212-b0ae-9e9681f1cbfb", "Scrap Metal": "1f7ac0bb-ad45-4246-9817-59bdf7f7ab39", "Metal 1": "8aedf6c2-94e1-4506-89d4-a0227c552f1e", "Metal 2": "1016cafc-9f6b-40c9-8713-9019d399783f", "Metal 3": "c0dfdea5-a39d-433a-b94a-299345a5df46", "Barrier Block": "09ca2713-28ee-4119-9622-e85490034758", "Tile": "8ca49bff-eeef-4b43-abd0-b527a567f1b7", "Brick": "0603b36e-0bdb-4828-b90c-ff19abcdfe34", "Glass": "5f41af56-df4c-4837-9b3c-10781335757f", "Glass Tile": "749f69e0-56c9-488c-adf6-66c58531818f", "Armored Glass": "b5ee5539-75a2-4fef-873b-ef7c9398b3f5", "Path Light Block": "073f92af-f37e-4aff-96b3-d66284d5081c", "Spaceship Block": "027bd4ec-b16d-47d2-8756-e18dc2af3eb6", "Cardboard": "f0cba95b-2dc4-4492-8fd9-36546a4cb5aa", "Cracked Concrete": "f5ceb7e3-5576-41d2-82d2-29860cf6e20e", "Concrete Slab": "cd0eff89-b693-40ee-bd4c-3500b23df44e", "Rusted Metal": "220b201e-aa40-4995-96c8-e6007af160de", "Extruded Metal": "25a5ffe7-11b1-4d3e-8d7a-48129cbaf05e", "Bubble": "f406bf6e-9fd5-4aa0-97c1-0b3c2118198e", "Plastic": "628b2d61-5ceb-43e9-8334-a4135566df7a", "Insulation": "9be6047c-3d44-44db-b4b9-9bcf8a9aab20", "Plaster": "b145d9ae-4966-4af6-9497-8fca33f9aee3", "Carpet": "febce8a6-6c05-4e5d-803b-dfa930286944", "Painted Wall": "e981c337-1c8a-449c-8602-1dd990cbba3a", "Net": "4aa2a6f0-65a4-42e3-bf96-7dec62570e0b", "Solid Net": "3d0b7a6e-5b40-474c-bbaf-efaa54890e6a", "Punched Steel": "ea6864db-bb4f-4a89-b9ec-977849b6713a", "Striped Net": "a479066d-4b03-46b5-8437-e99fec3f43ee", "Square Mesh": "b4fa180c-2111-4339-b6fd-aed900b57093", "Restroom Block": "920b40c8-6dfc-42e7-84e1-d7e7e73128f6", "Diamond Plate": "f7d4bfed-1093-49b9-be32-394c872a1ef4", "Aluminum": "3e3242e4-1791-4f70-8d1d-0ae9ba3ee94c", "Worn Metal": "d740a27d-cc0f-4866-9e07-6a5c516ad719", "Spaceship Floor": "4ad97d49-c8a5-47f3-ace3-d56ba3affe50", "Sand": "c56700d9-bbe5-4b17-95ed-cef05bd8be1b"}
material_string = tk.StringVar()
material_string.set("Plastic")
rotation_dict = {"0°": (None, None), "90°": (Image.ROTATE_270, Image.ROTATE_90), "180°": (Image.ROTATE_180, Image.ROTATE_180), "270°": (Image.ROTATE_90, Image.ROTATE_270)}
rotation_string = tk.StringVar()
rotation_string.set("0°")
plane = tk.StringVar()
plane.set("xy")
resize_type = tk.StringVar()
resize_type.set("scale")
resize_scale = tk.StringVar()
resize_scale.set("0.2")
resize_dimension_x = tk.StringVar()
resize_dimension_y = tk.StringVar()
resize_dimension_x.set("200")
resize_dimension_y.set("200")
filter_dict = {"Nearest": Image.NEAREST, "Box": Image.BOX, "Bilinear": Image.BILINEAR, "Hamming": Image.HAMMING, "Bicubic": Image.BICUBIC, "Lanczos": Image.LANCZOS}
filter_string = tk.StringVar()
filter_string.set("Hamming")
style = ttk.Style()
# style.theme_use("xpnative")
# style.configure("Red.TButton", foreground = "red")
# style.configure("Red.TLabel", foreground = "red")
# style.configure("Backplate_Color.TButton", background = "white")
# style.configure("TLabel", background = "white", foreground = "black")
# style.configure("TCheckbutton", background = "white", foreground = "black")
# style.configure("TRadiobutton", background = "white", foreground = "black")
# style.configure("TButton", background = "white")
# style.configure("TCombobox", background = "white")
show_preview = tk.BooleanVar()
show_preview.set(True)
image_path = None
save_path = None
preview_image = None
preview_rotation = (None, None)

### gui elements

save_type_label = ttk.Label(root, text = "Save Type:")
save_type_label.grid(column = 0, row = 0, columnspan = 2, padx = 2, pady = 2)

save_type_blueprint_button = ttk.Radiobutton(root, text = "New Blueprint", variable = save_type, value = "blueprint", command = save_type_change)
save_type_blueprint_button.grid(column = 1, row = 0, columnspan = 2, padx = 2, pady = 2)

save_type_json_button = ttk.Radiobutton(root, text = "Replace JSON", variable = save_type, value = "json", command = save_type_change)
save_type_json_button.grid(column = 2, row = 0, columnspan = 2, padx = 2, pady = 2)

blueprint_name_label = ttk.Label(text = "Blueprint Name:")
blueprint_name_label.grid(column = 1, row = 1, padx = 2, pady = 2)

blueprint_name_box = ttk.Entry(root, textvariable = blueprint_name, width = 34)
blueprint_name_box.grid(column = 2, row = 1, columnspan = 2, padx = 2, pady = 2)

file_select_button = ttk.Button(text = "Select Image", command = file_select_window)
file_select_button.grid(column = 0, row = 1, padx = 2, pady = 2)

file_save_button = ttk.Button(text = "Select Save Path", command = save_select_window)

backplate_checkbox = ttk.Checkbutton(root, text = "Generate Backplate (layer of blocks behind image to improve visibility)", variable = backplate, onvalue = True, offvalue = False, command = backplate_change)
backplate_checkbox.grid(column = 0, row = 2, columnspan = 4, padx = 2, pady = 4)

backplate_material_dropdown = ttk.Combobox(root, textvariable = backplate_material_string, values = list(material_dict), width = 16, state = "readonly")

backplate__reverse_checkbox = ttk.Checkbutton(root, text = "Reverse Side", variable = backplate_reverse, onvalue = True, offvalue = False)

backplate_color_button = ttk.Button(root, text = "Select Color", style = "Backplate_Color.TButton", command = backplate_color_window)

material_label = ttk.Label(text = "Material:")
material_label.grid(column = 0, row = 3, padx = 39, pady = 2)

material_dropdown = ttk.Combobox(root, textvariable = material_string, values = list(material_dict), width = 16, state = "readonly")
material_dropdown.grid(column = 1, row = 3, padx = 2, pady = 2)

opacity_threshold_label = ttk.Label(root, text = "Min Pixel Opacity (0-255):")
opacity_threshold_label.grid(column = 2, row = 3, padx = 2, pady = 2)

opacity_threshold_box = ttk.Entry(root, textvariable = opacity_threshold, width = 10)
opacity_threshold_box.grid(column = 3, row = 3, padx = 7, pady = 2)

flip_checkbox = ttk.Checkbutton(root, text = "Flip (Vertical)", variable = flip, onvalue = True, offvalue = False, command = flip_change)
flip_checkbox.grid(column = 0, row = 4, padx = 3, pady = 2)

mirror_checkbox = ttk.Checkbutton(root, text = "Mirror (Horizontal)", variable = mirror, onvalue = True, offvalue = False, command = mirror_change)
mirror_checkbox.grid(column = 1, row = 4, padx = 3, pady = 2)

rotation_label = ttk.Label(text = "Rotation (Clockwise):")
rotation_label.grid(column = 2, row = 4, padx = 3, pady = 2)

rotation_dropdown = ttk.Combobox(root, textvariable = rotation_string, values = list(rotation_dict), width = 7, state = "readonly")
rotation_dropdown.grid(column = 3, row = 4, padx = 2, pady = 2)
rotation_dropdown.bind('<<ComboboxSelected>>', rotation_change)

plane_label = ttk.Label(text = "Plane:")
plane_label.grid(column = 0, row = 5, padx = 2, pady = 2)

plane_xy_button = ttk.Radiobutton(root, text = "XY", variable = plane, value = "xy")
plane_xy_button.grid(column = 1, row = 5, padx = 2, pady = 2)

plane_xz_button = ttk.Radiobutton(root, text = "XZ", variable = plane, value = "xz")
plane_xz_button.grid(column = 2, row = 5, padx = 2, pady = 2)

plane_yz_button = ttk.Radiobutton(root, text = "YZ", variable = plane, value = "yz")
plane_yz_button.grid(column = 3, row = 5, padx = 2, pady = 2)

resize_label = ttk.Label(text = "Resize Type:")
resize_label.grid(column = 0, row = 6, padx = 3, pady = 2)

resize_scale_button = ttk.Radiobutton(root, text = "Scale", variable = resize_type, command = resize_change, value = "scale")
resize_scale_button.grid(column = 1, row = 6, padx = 2, pady = 2)

resize_dimension_button = ttk.Radiobutton(root, text = "Dimensions", variable = resize_type, command = resize_change, value = "dimension")
resize_dimension_button.grid(column = 2, row = 6, padx = 2, pady = 2)

resize_none_button = ttk.Radiobutton(root, text = "None", variable = resize_type, command = resize_change, value = "none")
resize_none_button.grid(column = 3, row = 6, padx = 2, pady = 2)

resize_scale_box_label = ttk.Label(root, text = "Scale Factor:")
resize_scale_box_label.grid(column = 0, row = 7, columnspan = 2, padx = 2, pady = 2)

resize_scale_box = ttk.Entry(root, textvariable = resize_scale, width = 10)
resize_scale_box.grid(column = 2, row = 7, columnspan = 2, padx = 2, pady = 2)

resize_dimension_x_box_label = ttk.Label(root, text = "Image Width:")

resize_dimension_x_box = ttk.Entry(root, textvariable = resize_dimension_x, width = 10)

resize_dimension_y_box_label = ttk.Label(root, text = "Image Height:")

resize_dimension_y_box = ttk.Entry(root, textvariable = resize_dimension_y, width = 10)

resize_filter_label = ttk.Label(root, text = "Resize Method:")
resize_filter_label.grid(column = 1, row = 8, padx = 2, pady = 2)

resize_filter_dropdown = ttk.Combobox(root, textvariable = filter_string, values = list(filter_dict), state = "readonly")
resize_filter_dropdown.grid(column = 2, row = 8, padx = 2, pady = 2)

export_button = ttk.Button(root, text = "Export", command = export)
export_button.grid(column = 1, row = 9, padx = 2, pady = 2)

preview_image_checkbox = ttk.Checkbutton(root, text = "Show Preview", variable = show_preview, onvalue = True, offvalue = False, command = show_preview_change)
preview_image_checkbox.grid(column = 2, row = 9, padx = 2, pady = 2)

preview_image_label = tk.Label(root)

### old code to generate the brute forced buttons instead of doing it manually

# color_buttons = (("eeeeee", "f5f071", "cbf66f", "68ff88", "7eeded", "4c6fe3", "ae79f0", "ee7bf0", "f06767", "eeaf5c"), ("7f7f7f", "e2db13", "a0ea00", "19e753", "2ce6e6", "0a3ee2", "7514ed", "cf11d2", "d02525", "df7f00"), ("4a4a4a", "817c00", "577d07", "0e8031", "118787", "0f2e91", "500aa6", "720a74", "7c0000", "673b00"), ("222222", "323000", "375000", "064023", "0a4444", "0a1d5a", "35086c", "520653", "560202", "472800"))
# r = 1
# cmd = str()
# for row in color_buttons:
#     c = 1
#     for column in row:
#         cmd += "style.configure(\"button_style_" + str(c) + "_" + str(r) + ".TButton\", foreground = \"" + column + "\")\n"
#         c += 1
#     r += 1
# print(cmd)

root.mainloop()

### remnants from when this was a command line program 

# # root.withdraw() # really stupid way to get a file selection menu
# flip, mirror, plane, resize_type = str(input("flip vertically? (Y/N) ")), str(input("flip horizontally? (Y/N) ")), str(input("which plane should it be aligned to? (XZ/YZ/XY) ")), str(input("resize type? (scale/dimension/none/S/D/N) ")) # get user defined variables
# if resize_type.lower() in ("scale", "s"):
#     resize_scale = float(input("resize factor? "))
# elif resize_type.lower() in ("dimension", "d"):
#     resize_dimension_x = int(input("image width? "))
#     resize_dimension_y = int(input("image height? "))
# save_path = tk.filedialog.asksaveasfilename(initialdir = "/", title = "Save As", filetypes = (("JSON Files","*.json"),("All Files","*.*"))) # saving path
# print("Converting...")

# print("Saving...")
# input("Saved!")