![logo.jpg](/examples/logo.jpg)
# collage

This is a program that creates a whole image from tiny images in a database. A database of ***1056 memes*** is already existent.

## Installation:
#### Clone:
```
git clone https://github.com/ArdaOzcan/collage.git
```
#### Change Directory:
```
cd collage/collage
```

## Configuration:
After you downloaded and changed your directory, you need some libraries:
```
pip install -r requirements.txt
```
Now run:
```
python collage.py -h
```
Which shows you the help menu

## Example:
```
python collage.py "meme_database" "test_images/1.jpg" --quality 7
```
#### Original Image:
![1.jpg](/collage/test_images/1.jpg)
#### Collage:
![karl_stefansson.jpg](/examples/karl_stefansson.jpg)

