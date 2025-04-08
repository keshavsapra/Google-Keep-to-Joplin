import os
import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import traceback # Import traceback for detailed error logging

def sanitize_filename(filename):
    """Removes or replaces characters invalid for filenames."""
    # Remove characters that are definitely invalid on most systems
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace colons, often used in timestamps, with underscores
    sanitized = sanitized.replace(":", "_")
    # Replace '+' sign as it can sometimes cause issues
    sanitized = sanitized.replace("+", "_")
    # Trim leading/trailing whitespace and dots
    sanitized = sanitized.strip().strip('.')
    # Prevent empty filenames or names consisting only of dots
    if not sanitized or all(c == '.' for c in sanitized):
        sanitized = "Untitled Note"
    # Limit filename length (optional, but good practice)
    max_len = 200
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len]
    return sanitized

def convert_keep_html_to_md(html_filepath, output_dir_path): # Renamed parameter
    """
    Converts a single Google Keep HTML file to a Markdown file in the specified output directory.

    Args:
        html_filepath (str): The path to the input HTML file.
        output_dir_path (str): The path to the directory where the output .md file will be saved.
    """
    base_filename = os.path.basename(html_filepath)
    try:
        # --- Read HTML File ---
        print(f"Processing: {base_filename}")
        with open(html_filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # --- Extract Title ---
        title_tag = soup.find('div', class_='title')
        # Use HTML filename (without extension) as fallback title if no title tag found
        title = title_tag.get_text(strip=True) if title_tag else os.path.splitext(base_filename)[0]
        if not title: # Ensure title is not empty
             title = "Untitled Note"

        # --- Sanitize title for Markdown filename ---
        md_filename = sanitize_filename(title) + ".md"
        # --- Construct the CORRECT full output path ---
        # This was the main error in the previous version.
        # It should join the output *directory* with the new *filename*.
        full_md_path = os.path.join(output_dir_path, md_filename)

        # --- Extract Content ---
        content_tag = soup.find('div', class_='note-content')
        if not content_tag:
            content_tag = soup.find('div', class_='content') # Fallback

        markdown_content = "" # Default to empty content
        if content_tag:
             # --- Handle Checkboxes ---
            try:
                for li in content_tag.find_all('li'):
                    checkbox = li.find('input', type='checkbox')
                    if checkbox:
                        text_span = checkbox.find_next_sibling('span')
                        text = text_span.get_text(strip=True) if text_span else ""
                        # Replace the original li content with Markdown checkbox format
                        # Using BeautifulSoup's replace_with method is safer
                        new_tag = soup.new_tag('p') # Use paragraph to avoid nested list issues
                        if checkbox.has_attr('checked'):
                            new_tag.string = f"- [x] {text}"
                        else:
                            new_tag.string = f"- [ ] {text}"
                        li.replace_with(new_tag) # Replace the whole li tag

                content_html = str(content_tag)
                # --- Convert HTML to Markdown ---
                markdown_content = md(content_html, heading_style="ATX", bullets='-')

            except Exception as e_content:
                print(f"  - Warning: Error processing content for {base_filename}: {e_content}")
                # Fallback to using raw content if checkbox processing fails
                try:
                    content_html = str(content_tag)
                    markdown_content = md(content_html, heading_style="ATX", bullets='-')
                    print(f"  - Info: Used raw content conversion for {base_filename} after error.")
                except Exception as e_md:
                     print(f"  - Error: Failed even raw markdown conversion for {base_filename}: {e_md}")
                     markdown_content = "[Content Conversion Failed]"

        else:
            print(f"  - Warning: Could not find content section in {base_filename}. Note will be created with title only.")

        # --- Combine Title and Content for Markdown File ---
        # Use the original extracted/generated title for the H1
        final_md_content = f"# {title}\n\n{markdown_content}"

        # --- Write Markdown File ---
        with open(full_md_path, 'w', encoding='utf-8') as f:
            f.write(final_md_content)

        print(f"  -> Successfully converted to: {md_filename} in 'converted files'")

    except FileNotFoundError:
        print(f"Error: File not found - {html_filepath}")
    except Exception as e:
        print(f"--- ERROR converting file {base_filename} ---")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Details: {e}")
        # Print traceback for more detailed debugging if needed
        # traceback.print_exc()
        print("----------------------------------------------")


def main():
    """
    Main function to select folder, create output directory, and process files.
    """
    # --- Set up Tkinter for folder selection ---
    root = tk.Tk()
    root.withdraw() # Hide the main Tkinter window

    print("Please select the folder containing your Google Keep HTML files.")
    # --- Ask user to select the input directory ---
    input_dir = filedialog.askdirectory(title="Select Google Keep HTML Export Folder")

    if not input_dir:
        print("No folder selected. Exiting.")
        return

    print(f"Selected folder: {input_dir}")

    # --- Define and create the output directory ---
    output_dir = os.path.join(input_dir, "converted files")
    try:
        os.makedirs(output_dir, exist_ok=True) # exist_ok=True prevents error if dir exists
        print(f"Output will be saved in: {output_dir}")
    except OSError as e:
        print(f"Error creating output directory '{output_dir}': {e}")
        return

    # --- Process each HTML file in the input directory ---
    print("\nStarting conversion...")
    file_count = 0
    conversion_errors = 0
    for filename in os.listdir(input_dir):
        # Process only .html files, ignore the script itself if it's in the same folder
        if filename.lower().endswith(".html"):
            file_count += 1
            html_filepath = os.path.join(input_dir, filename)
            # Pass the correct output directory path
            try:
                 convert_keep_html_to_md(html_filepath, output_dir)
            except Exception: # Catch errors from the conversion function itself
                 conversion_errors += 1
                 # Error details are printed within convert_keep_html_to_md

    print("\n--- Conversion Summary ---")
    if file_count == 0:
        print("No HTML files found in the selected directory.")
    else:
        print(f"Attempted conversion for {file_count} HTML file(s).")
        successful_conversions = file_count - conversion_errors
        print(f"Successful conversions: {successful_conversions}")
        if conversion_errors > 0:
             print(f"Files with errors: {conversion_errors} (See details above)")
    print(f"Check the '{os.path.basename(output_dir)}' folder for your Markdown notes.")
    print("--------------------------")


# --- Run the main function ---
if __name__ == "__main__":
    main()
