from google_images_search import GoogleImagesSearch
from credentials import project_cx, developers_api_key, email, password
import tkinter as tk
from tkinter import messagebox, ttk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from io import BytesIO
import zipfile
import threading

# Initialize Google Images Search
gis = GoogleImagesSearch(developers_api_key, project_cx)

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Images Downloader")
        self.root.geometry("550x480")
        self.root.resizable(False, False)
        self.root.config(bg="#ffffff")

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Google Images Downloader", font=("Helvetica", 26, "bold"), bg="#ffffff")
        title_label.pack(pady=15)

        # Image search topic
        tk.Label(self.root, text="Image Search Topic:", bg="#ffffff", font=("Helvetica", 14)).pack(pady=5)
        self.entry_topic = tk.Entry(self.root, width=70, font=("Helvetica", 12), borderwidth=2)
        self.entry_topic.pack(pady=5)

        # Number of images
        tk.Label(self.root, text="Number of Images:", bg="#ffffff", font=("Helvetica", 14)).pack(pady=5)
        self.entry_number = tk.Entry(self.root, width=10, font=("Helvetica", 12), borderwidth=2)
        self.entry_number.pack(pady=5)

        # Email address
        tk.Label(self.root, text="Your Email Address:", bg="#ffffff", font=("Helvetica", 14)).pack(pady=5)
        self.email_entry = tk.Entry(self.root, width=70, font=("Helvetica", 12), borderwidth=2)
        self.email_entry.pack(pady=5)

        # Download button
        self.download_button = tk.Button(self.root, text="Send Images via Email", command=self.start_download, 
                                          font=("Helvetica", 16, "bold"), bg="#4CAF50", fg="white", width=25, height=2)
        self.download_button.pack(pady=20)

        # Status
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg="#ffffff")
        self.status_label.pack(pady=5)

        # Progress bar
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=10)

        self.progress = ttk.Progressbar(self.progress_frame, length=500, mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=5)

        self.progress_label = tk.Label(self.progress_frame, text="0%", font=("Helvetica", 12), bg="#ffffff")
        self.progress_label.pack(side=tk.LEFT, padx=5)

    def start_download(self):
        # Run the download in a separate thread to keep the GUI responsive
        threading.Thread(target=self.download_images).start()

    def download_images(self):
        query = self.entry_topic.get()
        try:
            num_images = int(self.entry_number.get())
        except ValueError:
            self.show_error("Input Error", "Please enter a valid number for the number of images.")
            return

        recipient_email = self.email_entry.get()

        if not query or not num_images or not recipient_email:
            self.show_error("Input Error", "Please fill in all fields.")
            return

        try:
            # Start progress bar
            self.update_status("Searching and sending images...")
            self.progress['value'] = 0
            self.progress['maximum'] = num_images
            self.progress_label.config(text="0%")
            self.progress.start()

            # Search and gather images using Google Images Search API
            search_params = {
                'q': query,
                'num': num_images,
                'fileType': 'jpg',
                'imgSize': 'medium',
                'safe': 'high'
            }

            # Attempt to search for images
            try:
                gis.search(search_params=search_params)
            except Exception as e:
                self.show_error("API Error", f"Error occurred: {e}")
                return

            # Create a ZIP file in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, image in enumerate(gis.results(), start=1):
                    img_data = BytesIO()
                    try:
                        image.download(img_data)
                        img_name = f"{query}_{i}.jpg"
                        img_data.seek(0)  # Move the buffer position to the beginning
                        zip_file.writestr(img_name, img_data.read())  # Add the image to the zip
                    except Exception as e:
                        print(f"Error downloading image {i}: {e}")
                        continue

                    # Update progress bar
                    self.progress['value'] = i
                    self.progress_label.config(text=f"{int((i/num_images)*100)}%")
                    self.root.update_idletasks()

            zip_buffer.seek(0)  # Move buffer position back to the start

            # Send email with downloaded images in a ZIP
            self.send_email_with_zip(recipient_email, zip_buffer)

            self.update_status(f"Sent {num_images} images to {recipient_email}")
            self.show_info("Success", f"{num_images} images sent successfully to {recipient_email}!")

        except Exception as e:
            self.show_error("Error", f"An error occurred: {e}")

        finally:
            # Stop progress bar
            self.progress.stop()

    def send_email_with_zip(self, recipient_email, zip_data):
        """ Function to send email with ZIP attachment """
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = email  # Email from the credentials file
        sender_password = password  # Password from the credentials file

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = 'Downloaded Images'

        # Email body
        msg.attach(MIMEText('Here are the images you requested in a ZIP file.', 'plain'))

        # Add ZIP file as an attachment
        part = MIMEApplication(zip_data.getvalue(), Name='images.zip')
        part['Content-Disposition'] = 'attachment; filename="images.zip"'
        msg.attach(part)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            self.show_error("Email Error", f"An error occurred while sending email: {e}")

    def update_status(self, message):
        self.status_label.config(text=message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()
