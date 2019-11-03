# collage

This is a program that creates a whole image from tiny images in a database. A database of ***1056 memes*** is already existent.

## Configuration:
#### NOTE:
If this is your first time running, it is recommended that that you input **'y'** to the question at index 4.
```
 0 Please input a database path : /meme_databse
 1 Input image path ( Directly write the name if it's in the current directory ) : test_images/1.jpg
 2 End result's quality? ( 1 is the best quality, bigger is worse ) ( Note that better quality will be exponentially slower to compute, recommended is 8 ): 8
 3 Image size of the result image? ( This represents a single image's single edge, input around (10-30) for decent results ) : 15
 4 Do you want to create a new json file to store the average colors of your database? (y/n) ( Input 'y' if this is your first time running) : n
 5 What is your choice for the image? ('s' for only showing, 'e' for only exporting, '*' for both) : *
 6 Export file's name (Press enter for auto-naming) :
 7 Export path (Press enter for current directory) (This has to be a valid directory):
 8 Process started...
```

## Example:
#### Original Image:
![1.jpg](/collage/test_images/1.jpg)
#### Collage:
![karl_stefansson.jpg](/examples/karl_stefansson.jpg)

