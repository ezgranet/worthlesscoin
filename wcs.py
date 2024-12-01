from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import json
import os
import streamlit as st

# Debugging step: print to see if the script is running
print("Streamlit app is starting...")

# File to store counters
COUNTER_FILE = "counters.json"
INPUT_PDF = "template.pdf"  # Specify the input PDF template here
CUSTOM_FONT = "CourierPrime-Regular.ttf"  # Path to the custom font file

# Check if the font file exists
if not os.path.exists(CUSTOM_FONT):
    print(f"Font file not found: {CUSTOM_FONT}")
else:
    print(f"Font file found: {CUSTOM_FONT}")

# Check if the template PDF exists
if not os.path.exists(INPUT_PDF):
    print(f"Input PDF file not found: {INPUT_PDF}")
else:
    print(f"Input PDF file found: {INPUT_PDF}")

# Register the custom font
font_path = "CourierPrime-Regular.ttf"  # Path to the TTF file
font_name = "CourierPrime"  # This is the name you will use in setFont

try:
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    print(f"Font registered successfully: {font_name}")
except Exception as e:
    print(f"Error registering font: {e}")

# Check if font is registered correctly
print("Registered fonts:", pdfmetrics.getRegisteredFontNames())  # Should list "CourierPrime"

# Initialize counters if not exist
if not os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"total_uses": 0, "total_quantity": 0}, f)

# Function to load counters
def load_counters():
    try:
        with open(COUNTER_FILE, "r") as f:
            counters = json.load(f)
        print("Counters loaded:", counters)
        return counters
    except Exception as e:
        print(f"Error loading counters: {e}")
        return {"total_uses": 0, "total_quantity": 0}

# Function to update counters
def update_counters(new_quantity):
    try:
        counters = load_counters()
        counters["total_uses"] += 1
        counters["total_quantity"] += new_quantity
        with open(COUNTER_FILE, "w") as f:
            json.dump(counters, f)
        print("Counters updated:", counters)
        return counters
    except Exception as e:
        print(f"Error updating counters: {e}")
        return {"total_uses": 0, "total_quantity": 0}

# Function to create PDF overlay with custom font
def overlay_text_on_pdf(input_pdf, name, quantity, counters, output_pdf="output.pdf"):
    try:
        # Create a new page with text overlay using ReportLab
        packet = BytesIO()
        can = canvas.Canvas(packet)
        # Format the quantity with leading zeros and ".00" without commas
        formatted_quantity = f"{quantity:012.2f}"
        counters = load_counters()
        total_uses = counters["total_uses"]
        formatted_total_uses = f"{total_uses:08d}"
        can.setFont("CourierPrime", 15)  # Use the correct registered font name
        can.drawString(390, 205, f"{name}")
        can.setFont("CourierPrime", 30)  # Use the correct registered font name
        can.drawString(200, 115, formatted_quantity)
        can.setFont("CourierPrime", 10)  # Use the correct registered font name
        can.drawString(16, 85, formatted_total_uses)

        can.save()

        # Move to the beginning of the BytesIO buffer
        packet.seek(0)
        overlay_pdf = PdfReader(packet)

        # Read the input template
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        # Merge overlay onto each page of the input PDF
        for page in reader.pages:
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        # Write the result to the output file in memory
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        print(f"PDF generated successfully: {output_pdf}")
        return output_buffer  # Return the in-memory PDF buffer

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

# Streamlit App
st.title("WorthlessCoin: a cryptocurrency for everyone!")
# Additional information
st.markdown("""
    ### About
    - One problem with cryptocurrencies is that the energy required to keep up the blockchain ledger is very inefficient. Many people have tried to fix this with new types of blockchain, but WorthlessCoin, minted by Granet Press Limited (a company registered in England & Wales), takes a different approach! Instead of changing the blockchain, WorthlessCoin dispenses with the need for a ledger, by minting an unlimited quantity for anyone that asks! Thus, anyone can own any quantity of WorthlessCoin! 
    - WorthlessCoin is one of many worthless cryptocurrencies, but it's the only one that has the honesty to admit it! 
    - WorthlessCoin also exists to annoy the (England & Wales) Law Commission over their very silly proposals on the property law status of digital assets. Other legal regulatory bodies may be annoyed in future too!
    - To mint WorthlessCoin, enter your name, the quantity of WorthlessCoin you want (integers only) and click MintCoin! A banknote/certificate of title to this utterly meaningless digital asset will be yours. You can then sell this asset to anyone. After selling, you can then get more WorthlessCoin! Unlimited coins, for everyone!
    - The currency symbol for WorthlessCoin is  the null sign ∅ (U+2205)
    - If something is broken or you just want to say something, get in touch with me, Elijah Granet, via e-mail [by clicking this link](mailto:&#101;&#100;&#105;&#116;&#111;&#114;&#64;&#108;&#101;&#103;&#97;&#108;&#115;&#116;&#121;&#108;&#101;&#46;&#99;&#111;&#46;&#117;&#107;)	
    """)

# User Inputs
name = st.text_input("Enter your name", placeholder="Type your name here...")
quantity = st.number_input("Enter a quantity (1 to 1 trillion)", min_value=1, max_value=10**12, step=1)

# Load current counters
counters = load_counters()

# Display current counters
st.write(f"Total number of times the app has been used: **{counters['total_uses']}**")
st.write(f"Sum of all quantities entered: **{counters['total_quantity']}**")

# Generate and Download PDF on Button Click
if st.button("Mint Coin"):
    if name.strip() and quantity > 0:
        # Update counters
        counters = update_counters(quantity)

        # Generate the PDF
        output_pdf = overlay_text_on_pdf(INPUT_PDF, name, quantity, counters)

        if output_pdf:
            # Directly download the PDF without additional clicks
            st.download_button(
                label="Download Banknote",
                data=output_pdf,
                file_name=f"{counters['total_quantity']}.pdf",  # Use dynamic file name
                mime="application/pdf",
                use_container_width=True
            )
            st.success("Coin Minted!")
        else:
            st.error("Failed to generate PDF. Check the logs for details.")
    else:
        st.error("Please provide valid inputs.")
