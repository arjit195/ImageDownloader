# ImageDownloader

This Python-based application allows you to search for images using the Google Custom Search API, download them, and send the downloaded images to an email address in a ZIP file. 
The application has a user-friendly GUI built with Tkinter and makes use of the google_images_search library to perform image searches.

**Features**
Image Search: Enter a search query to find images from Google.\n
Number of Images: Specify the number of images to download.
Email Delivery: Automatically send the images in a ZIP file to a specified email address.
Progress Bar: Track the download progress using a built-in progress bar.

**Prerequisites**
Before running this application, make sure you have the following installed:

-Python 3.x
-A Google Custom Search Engine (CSE) set up with an API key
-Google Cloud Project with the Custom Search API enabled

**Libraries Used**
google_images_search: For fetching images from Google.
tkinter: For building the GUI.
smtplib & email: To handle email sending.
zipfile: To create a ZIP archive for downloaded images.
requests: HTTP library used by google_images_search.
Pillow: (Optional) For additional image processing tasks.
