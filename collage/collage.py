import cv2
import numpy as np
import json
from time import time
import os
import math
from datetime import timedelta
import argparse
from colorama import Fore, Style, init
from tqdm import tqdm

def show_info(start, highligth="", end=""):
    
    print(Style.BRIGHT +
          Fore.YELLOW + f"[*] {start} " +         
          Fore.GREEN + f"{highligth} " +
          Fore.YELLOW + f"{end}"
          )


def average_to_json(database_path, precision):
    
    '''
    Function Description : 
    
    * This function is used for saving average colors of the images in the database to a file 
    so the program doesn't have to apply this every time when using the same database.
    
    What it does : 
    
        -Takes a database path and iterates through the list of images in that database
        -Calulates the average color of the image by using numpy.average() and appends it to the list 'files_avg_col'
        -Writes 'files_avg_col' to a json file 
    
    NOTE :  The image is resized to a smaller version to reduce iteration, user specifies the resize amount
            'files_avg_col' list is converted to an integer array with .astype(int) because numpy.average() returns a float array
            Reversed the 'average_color' array before appending to 'files_avg_col' because cv2 uses BGR format for colors 
            Used .tolist() because type 'ndarray' is not JSON serializable
       
    '''
    
    
    file_names = os.listdir(database_path)
    show_info("Creating a json file to store average colors of the database")  
    
    files_avg_col = []
    
    for i, file in zip(tqdm(range(len(file_names))), file_names):
        image = get_image(database_path, file, precision) 
        avarage_color = np.average(image, (0, 1)).astype(int) 
        files_avg_col.append(avarage_color.tolist()[::-1])     
               
    json_file_name = os.path.basename(os.path.normpath(database_path))
    with open(f"{json_file_name}.json", "w") as json_file:
        json.dump(files_avg_col, json_file)   
        
    show_info("Created/modified", f"json file (.\{json_file_name}.json)", "to store average colors of the database")   

def new_shape(image, crop_size):
    
    '''
    
    Function Description:
    
    * This function finds the closest multiple of 'crop_size' that is smaller than the image shape
    so the chunks(every square in the result image) that have a shape of (crop_size x crop_size)
    can fill the whole image perfectly.
    
    What it does :

        -Iterates through the shapes of images (width and heigth)
        -Floors the shape/crop_size and multiplies it by crop_size
            ( 
                Example :   if the shape is 340 and crop_size is 7,
                            340/7 ( shape/crop_size ) would be 48,57
                            Floor of 48,57.. is 48 
                            and 48 * 7 is 336‬                        
            )
        -Appends the new value to a 'new_shape'
        -Returns 'new_shape' after the loop is finished

    
    Example :   if the given image's shape is 300x224 and 'crop_size' equals to 7,
                the function would return [294, 224] since the closest multiple of 7 that is smaller than 300 is 294
                and the closest multiple of 7 that is smaller than 224 is 224
    
    
    '''
    
    new_shape = []
    for shape in image.shape[:-1]:
        new_shape.append(math.floor(shape/crop_size)*crop_size)
    return new_shape
    

def crop(image, crop_size):
    
    '''
    
    Function Description:
    
    * This function crops the input image into (crop_size x crop_size) squares and takes the average color of it
    so the function 'arrange(colors, json_file, database_list)' can use the returned list to find the closest color.
    
    What it does :

        -Resizes the image (see 'new_shape()')
        -Crops the image using numpy indexing ( A single chunk has the size of (crop_size x crop_size) )
        -Appends 'current_average' to 'average_list'
        -Returns 'average_list' after the loop is finished

    NOTE :  'files_avg_col' list is converted to an integer array with .astype(int) because numpy.average() returns a float array
            Reversed the 'current_average' array before appending to 'average_list' because cv2 uses BGR format for colors 
              
    '''
    
    show_info("Cropping the image into pieces")
    
    image = cv2.imread(image)
    image = cv2.resize(image, tuple(new_shape(image, crop_size)[::-1]))

    
    average_list = []   
    for y_index in tqdm(range(0, image.shape[0], crop_size)):
        
        for x_index in range(0, image.shape[1], crop_size):
            
            cropped_image = image[y_index:y_index+crop_size, x_index:x_index+crop_size]
            current_average = np.average(cropped_image, (0, 1))[::-1]     
            average_list.append(current_average.astype(int))   
            
            
    return average_list
        
        
def arrange(colors, json_file, database_list):
    
    '''
    
    Function Description :
    
    * This function uses an algorithm to find the closest color ( from 'crop(image, crop_size))' ) to a given color ( from 'avg_colors.json' )
    
    What it does  :

        -Converts 'colors' to a numpy array
        -Converts 'colors' ( if its dimension is bigger than 2 ) to a 2-dimensional array by multiplying every dimension except the last one
         since the last dimension represents RGB values and should always stay as 3
         so an array with the shape (2, 2, 3) would become (4, 3) like in the example
            (                
                Example:    

                    if 'colors' was 
                                      
                    [[[  0   0   0]
                    [255 255 255]]

                    [[255 255 255]
                    [  0   0   0]]]
                
                    which is 3-dimensional, using a for loop wouldn't work because
                    
                    for color in colors:
                        print(color)
                        
                    would output : 
                    
                    0   [[  0   0   0]
                        [255 255 255]]
                        
                    1   [[255 255 255]
                        [  0   0   0]]
                        
                    but we need : 
                    
                    0   [  0   0   0]
                    1   [255 255 255]                    
                    2   [255 255 255]
                    3   [  0   0   0]
                                                                         
            )
            -For every color in 'colors', it checks the whole database for the closest color and assigns the index to 'image_index'
            -Appends the 'image_index' ( which is the index of the closest file ) to 'file_names_list'
            -Returns 'file_names_list' after the loop is finished
        
    NOTE :  Searching algorithm can be replaced with a better one because :
    
                1. This one is not very efficient ( This function usually takes the most time )
                2. Finding the absolute closest image causes repetition of images
                
                So a less precise ( possibly a little random ) and more efficient algorithm could be used

    '''
    show_info("Choosing best images from the database")

    
    colors = np.array(colors)

    if colors.ndim > 2:
        product = 1
        for shape in colors.shape[:-1]:
            product *= shape
        
        colors.shape = (product, 3)    
    elif colors.ndim == 1:
        raise IndexError("'colors' argument must be at least 2 dimensional")    
                
           
    json_file = open(json_file, "r")
        
    avg_file_col = json.load(json_file)
    avg_file_col = np.array(avg_file_col)
    
    file_names_list = []
      
    for _, color in zip(tqdm(range(len(colors))), colors):
        
        smallest_difference = []
        image_index = 0
    
        for i, avg_color in enumerate(avg_file_col):
            current_difference = abs(avg_color - color)
            
            if len(smallest_difference) == 0:
                smallest_difference = current_difference  
                image_index = i
            elif np.average(current_difference) < np.average(smallest_difference[1]):
                
                smallest_difference = current_difference
                image_index = i
                
        
        file_names_list.append(database_list[image_index])
                

    return file_names_list
     
def generate_name(export_path, word="result"):
    
    '''
    
    Function Description:
    
    *This function automatically generates a name for the export file
    
    What it does :
    
        -Creates a for loop in range of the length of the items that are in the given directory
        -If a file named "result_{s}.jpg" doesn't exist return it.
        
    Example :   If there was a file named 'result_0.jpg' in the given directory,
                the function would return 'result_1.jpg'

    
    '''
    
    for s in range(len(os.listdir(export_path))):
        if not os.path.isfile(os.path.join(export_path, f"{word}_{s}.jpg")):
            return f"{word}_{s}.jpg"
            
            
def get_image(database_path, file_name, single_image_size):
    
    '''
    
    Function Description:
    
    *This is a function that processes the image and returns it, this was created to prevent duplicate code
    
    What it does :
    
        -Reads and resizes( to the size of (crop_size x crop_size) ) the image that is in the given path.
        
    '''
    
    file_path = os.path.join(database_path, file_name)
    file = cv2.imread(file_path)
    file = cv2.resize(file, (single_image_size, single_image_size))
    
    return file

def render(single_image_size, result_image_size, database_path, file_names_list, choice, file_name, export_path):
    
    '''
    
    Function Description :
    
    *This is the last function that is called, 
    it renders every horizantol line and stacks every horizontal line vertically to a bigger array which makes up the whole image
    
    What it does :
    
        -Stacks images that are given for {result_image_size[1]} times horizontally
        -Stacks the whole horizontal line to 'result_image'
        -Repeat until finished
        -Show or/and export according to user choise
        
    NOTE :  In the first loop ( when i == 0 ), sets result image to the first horizontal line
            so that the next could be stacked    
    
    '''
    
    
    show_info("Rendering image")
    
    for i in tqdm(range(result_image_size[1])):      
        horizontal = get_image(database_path, file_names_list[result_image_size[0]*i], single_image_size)  
        
        for file in file_names_list[1 + (result_image_size[0]*i):result_image_size[0]*(i+1)]:   
            file = get_image(database_path, file, single_image_size)
            horizontal = np.hstack((horizontal, file))          
    
        if i == 0:
            result_image = horizontal
        else:
            result_image = np.vstack((result_image, horizontal))   
    
    
    show_info("Rendering is", "finished.")

    
    if choice == "s":        
        cv2.imshow("result", result_image)    
        cv2.waitKey(0)
    elif choice == "*" or choice == "e":
        
        if file_name != "":
            if not file_name.endswith(".jpg"):
                file_name = file_name + ".jpg"
                
            while os.path.isfile(os.path.join(export_path, file_name)):
                if ("The file name you entered already exists, do you want to override? ( y/n ) : ").lower() == 'y':
                    break
                else:
                    file_name = generate_name(export_path, word=os.path.splitext(file_name)[0])
                    
                    
            cv2.imwrite(os.path.join(export_path, file_name), result_image) 
            show_info("Exported file to '", os.path.join(export_path, file_name), "'")
            
        else:
            file_name = generate_name(export_path)
            cv2.imwrite(os.path.join(export_path, file_name), result_image) 
            show_info("Exported file to '", os.path.join(export_path, file_name), "'")

            
        if choice == "*":
            cv2.imshow(file_name, result_image)   
            cv2.waitKey(0)   
             
            
    
def main():
    
    init() 
    
    parser = argparse.ArgumentParser(description="Creates a collage of images.")
    
    parser.add_argument("database_path", action="store",
                         help="Stores the image database path")
    
    parser.add_argument("image_path", action="store",
                         help="Stores the input image path")
    
    parser.add_argument("--quality", "-q", action="store", type=int,
                         help="Image quality (min is 1)",
                         default=8)
    
    parser.add_argument("--size", "-s", action="store", type=int,
                         help="Chunk size, 10-30 works the best",                        
                         default=16)
    
    parser.add_argument("--choice", "-c",action="store",
                         help="User choice, 's' for only showing, 'e' for only exporting, '*' for both",                        
                         default="*")
    
    parser.add_argument("--file_name", "-f", action="store",
                         help="Export file's name, (This argument only takes the name, not the whole path)",                        
                         default="")
    
    parser.add_argument("--export_dir", "-d", action="store",
                         help="Export file's directory, this is not required since the image will be exported to the current directory by default",                        
                         default=".")
    
    parser.add_argument("--scan_database", "-sd", action="store_true",
                         help="Scans the database, this is required on the first run")
    


    args = parser.parse_args()
        
    database_path = args.database_path
    database_list = os.listdir(database_path)
    input_image_path = args.image_path

    quality_size = args.quality
    single_image_size = args.size

    result_shape = (int(new_shape(cv2.imread(input_image_path), quality_size)[1] / quality_size), 
                    int(new_shape(cv2.imread(input_image_path), quality_size)[0] / quality_size))

    show_info("Process", "started")
    start = time()
    
    if args.scan_database:
        average_to_json(database_path, 15)

    choice = args.choice
    

    # If the user chose 's' which stands for 'show only', these variables don't matter
    # But they need to be defined to prevent errors
    export_file_name = ""
    export_path = ""

    if choice == "e" or choice == "*" :
        export_file_name = args.file_name  
        export_path = args.export_dir
        if not os.path.isdir(export_path) and export_path != "":
            os.mkdir(export_path)
                  
        
    

        
    render(single_image_size, result_shape, database_path, 
                    arrange(crop(input_image_path, quality_size), 
                    f"{os.path.basename(os.path.normpath(database_path))}.json", database_list), choice, 
                    export_file_name, export_path)


    end = time()
    show_info("Whole process was finished in", str(timedelta(seconds=(round(end - start)))), "seconds")     
    
if __name__ == "__main__":
    main()    
