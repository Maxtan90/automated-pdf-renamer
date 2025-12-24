import tkinter as tk
from tkinter import filedialog
import os
import fitz
from glob import glob

# Dictionary mapping error types to tips
error_tips = {
    "FileDataError": "The PDF file might be corrupted or not a valid PDF file. Try opening it with a PDF reader.",
    "IndexError": "The PDF might be missing the expected text fields. Verify the PDF content.",
    "KeyError": "The expected keys were not found in the PDF. Check the text structure of the PDF.",
    "PermissionError": "You do not have the required permissions to rename the file. Check your file permissions.",
    "FileNotFoundError": "The specified file was not found. Ensure the file path is correct."
}

def rename_files():
    folder_path = filedialog.askdirectory()
    if folder_path:
        pdf_list = glob(os.path.join(folder_path, '*.pdf'))
        error_messages = []  # List to collect error messages
        for pdf in pdf_list:
            try:
                with fitz.open(pdf) as pdf_obj:
                    text = pdf_obj[0].get_text()

                # Extract the invoice number
                invoice_number = text.split('Invoice No: ')[1].split('\n')[0].strip()

                # Extract the client name
                lines = text.split('\n')
                client_name = ""
                for i, line in enumerate(lines):
                    if line.strip().lower().startswith("attn:"):
                        client_name = lines[i + 1].strip()
                        break
                if not client_name:  # If no "Attn:" line found, fall back to extracting after "TOTAL"
                    client_name = text.split('TOTAL\n')[1].split('\n')[0].strip()

                # Construct the new file name
                new_file_name = f"{client_name} - {invoice_number}.pdf"
                new_file_path = os.path.join(folder_path, new_file_name.replace(' ', '_'))

                # Rename the PDF file
                os.rename(pdf, new_file_path)
            except Exception as e:
                # Only include the file name and error type in the error message
                error_type = str(e).split(':')[0]
                error_tip = error_tips.get(error_type, "An unknown error occurred. Please check the file.")
                error_messages.append(f"Error processing file {os.path.basename(pdf)}: {error_type}\nTip: {error_tip}")

        if error_messages:
            # Truncate the message if it's too long for the window
            error_message = "\n\n".join(error_messages)
            if len(error_message) > 500:  # Adjust the length as necessary
                error_message = error_message[:500] + "...\n(too many errors to display)"
            result_label.config(text=f"Errors encountered:\n{error_message}")
        else:
            result_label.config(text="Files renamed successfully!")

# Create the main window
window = tk.Tk()
window.title("PDF File Renamer")

# Create a button to trigger file renaming
rename_button = tk.Button(window, text="Rename PDF Files", command=rename_files)
rename_button.pack(padx=20, pady=10)

# Create a label to show the result
result_label = tk.Label(window, text="", wraplength=400)  # Set wraplength to keep text within the window
result_label.pack(pady=5)

# Run the main event loop
window.mainloop()
