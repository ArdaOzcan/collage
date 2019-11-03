import cv2
import numpy as np
import json
from time import time
import os
import math
from datetime import timedelta

def average_to_json(meme_database_path, precision):
    
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
    
    file_names = os.listdir(meme_database_path)
    print("Creating a json file to store average colors of database...")  
    start =  time()
    
    files_avg_col = []
    
    for i, file in enumerate(file_names):
        image = get_image(meme_database_path, file, precision) 
        avarage_color = np.average(image, (0, 1)).astype(int) 
        files_avg_col.append(avarage_color.tolist()[::-1])     
               
    with open("avg_colors.json", "w") as json_file:
        json.dump(files_avg_col, json_file)   
        
    end = time()
    print(f"Process finished in {timedelta(seconds=(round(end - start)))} seconds")     
       

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
                            340/7 ( shape/crop_size ) would be 48,57...
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
    so the function 'arrange(colors, json_file, memes)' can use the returned list to find the closest color.
    
    What it does :

        -Resizes the image (see 'new_shape()')
        -Crops the image using numpy indexing ( A single chunk has the size of (crop_size x crop_size) )
        -Appends 'current_average' to 'average_list'
        -Returns 'average_list' after the loop is finished

    NOTE :  'files_avg_col' list is converted to an integer array with .astype(int) because numpy.average() returns a float array
            Reversed the 'current_average' array before appending to 'average_list' because cv2 uses BGR format for colors 
              
    '''
    
    print("Cropping the image into pieces...")
    
    image = cv2.imread(image)
    image = cv2.resize(image, tuple(new_shape(image, crop_size)[::-1]))

    
    
    average_list = []   
    for y_index in range(0, image.shape[0], crop_size):
        
        for x_index in range(0, image.shape[1], crop_size):
            
            cropped_image = image[y_index:y_index+crop_size, x_index:x_index+crop_size]
            current_average = np.average(cropped_image, (0, 1))[::-1]     
            average_list.append(current_average.astype(int))   
            
    return average_list
        
        
def arrange(colors, json_file, memes):
    
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
    print("Choosing best images from the database...")

    
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
      
    for color in colors:
        
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
                
        
        file_names_list.append(memes[image_index])
                

    return file_names_list
     
def generate_name(export_path):
    
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
        if not os.path.isfile(os.path.join(export_path, f"result_{s}.jpg")):
            return f"result_{s}.jpg"
            
            
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
    
    
    print("Rendering image...")
    
    for i in range(result_image_size[1]):      
        horizontal = get_image(database_path, file_names_list[result_image_size[0]*i], single_image_size)  
        
        for file in file_names_list[1 + (result_image_size[0]*i):result_image_size[0]*(i+1)]:   
            file = get_image(database_path, file, single_image_size)
            horizontal = np.hstack((horizontal, file))          
    
        if i == 0:
            result_image = horizontal
        else:
            result_image = np.vstack((result_image, horizontal))   
    
    
    print("Rendering is finished.")

    
    if choice == "s":        
        cv2.imshow("result", result_image)    
        cv2.waitKey(0)
    elif choice == "*" or choice == "e":
        
        if file_name != "":
            if not file_name.endswith(".jpg"):
                file_name = file_name + ".jpg"
                
            while os.path.isfile(os.path.join(export_path, file_name)):
                if input("The file name you entered already exists, do you want to override? ( y/n ) : ").lower() == 'y':
                    break
                else:                  
                    file_name = input("Please enter a new file name : ")
                    if not file_name.endswith(".jpg"):
                        file_name = file_name + ".jpg"
                    
            cv2.imwrite(os.path.join(export_path, file_name), result_image) 
            print(f"Exported file to '{os.path.join(export_path, file_name)}', 2 {export_path}")
            
        else:
            cv2.imwrite(os.path.join(export_path, generate_name(export_path)), result_image) 
            print(f"Exported file to '{os.path.join(export_path, file_name)}', 3 {export_path}")

            
        if choice == "*":
            cv2.imshow("result", result_image)   
            cv2.waitKey(0)   
             
            
    
        
meme_database_path = input("Please input a database path : ")
memes = os.listdir(meme_database_path)
input_image_path = input("Input image path ( Directly write the name if it's in the current directory ) : ")

quality_size = int(input("End result's quality? ( 1 is the best quality, bigger is worse ) ( Note that better quality will be exponentially slower to compute, recommended is 8 ): "))
single_image_size = int(input("Image size of the result image? ( This represents a single image's single edge, input around (10-30) for decent results ) : "))

result_shape = (int(new_shape(cv2.imread(input_image_path), quality_size)[1] / quality_size), 
                int(new_shape(cv2.imread(input_image_path), quality_size)[0] / quality_size))

if input("Do you want to create a new json file to store the average colors of your database? (y/n) ( Input 'y' if this is your first time running ): ").lower() == "y":
    average_to_json(meme_database_path, int(input("How precise should the average color be? (An integer) : ")))

choice = ""
while choice != "s" and choice != "e" and choice != "*":
    choice = input("What is your choice for the image? ('s' for only showing, 'e' for only exporting, '*' for both) : ").lower()



# If the user chose 's' which stands for 'show only', these variables don't matter
# But they need to be defined to prevent errors
export_file_name = ""
export_path = "_placeholder_"

if choice == "e" or choice == "*" :
    export_file_name = input("Export file's name (Press enter for auto-naming) : ")  
    export_path = input("Export path (Press enter for current directory): ")
    if not os.path.isdir(export_path) and export_path != "":
        os.mkdir(export_path)
    
        

        
    
print("Process started...")
start = time()

render(single_image_size, result_shape, meme_database_path, 
                arrange(crop(input_image_path, quality_size), 
                "avg_colors.json", memes), choice, 
                export_file_name, export_path)


end = time()
print(f"Whole process was finished in {timedelta(seconds=(round(end - start)))} seconds")     
