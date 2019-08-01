# BananaMind
A crawler that download images from google and a viewer to view and delete them easily

# The Crawler
## The command line
Controled by a command line.
This is a list of the argument :

| Argument | Short hand | Default Vaule | Description |
|-------------|----------|---------------|-------------------|
|help|h|*no value*|Print the help|
|keywords |k|*required*|Define the keyworkds to search for, you can use '-' to exclude a keyword of the search|
|limit|l|*500*|The limit of images to search for. This number is divided by the number a search request and rounded up to the closest and lowest integer, so expect a lower number of image returned|
|name|n|*default*|The name of the output directory, all unallowed character in windows file name will be deleted from it|
|mode|m|*1*|The mode of request, mode 1 will do 5 search over a periode of 5 years, mode 2 will do 60 search over a periode of 5 years.The only accepeted value are 1 and 2. The mode 2 takes longer, but is *suposed* to be more acurate for the same number of image downloaded|


All argument must follow a '-' and be follow by a space and a value between '"'. Only the -k argument is required.

Exemple :
* -k "Banana -fruit" -l "50" -m "2" -n "Bananas"



## Known Issues


### HTTP Error
During the download, sometime (around 10%) the download fail and return a HTTP Error mostly 403: Forbiden, but other as well.

### SSL Error
Sometime during the download or suring the initial requests, and SSL error is return. An ugly work around is commented at the begining of the script if you having issue with SSL Error, just uncomment it.

### No file format
Sometime, the json containing all information about the image will not include its file format, so a file without extention is created. It can be repared by adding a ".jpg" on the file itself most of the time.
A bugfix for this would be to check if the arguent ["ity"] of the json is set and if not, check the link of the image and get the fileformat from there.

### Using '"' in command
If you use '"' in a value of an input argument, the script will fail. Please use only alphanumerical and "_- "

# The Viewer
Use the button or the Left and Right arrows to keep a file or delete it.

File deleted by the viewer can't be recovered.

Images are resized to fit the windows size.

Only suported format are .png and .jpeg.

