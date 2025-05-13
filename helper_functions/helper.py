from fpdf import FPDF

def convert_to_pdf(report, output_pdf_path):
    try:
        # Initialize PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add a page
        pdf.add_page()

        # Set document metadata
        pdf.set_title("Medical Consultation Report")
        pdf.set_author("AI Assistant")
        
        # Set fonts
        pdf.set_font("Arial", "B", size=16)  # Title font
        pdf.cell(200, 10, txt="Medical Consultation Report", ln=True, align="C")
        pdf.ln(10)  # Add a line break
        
        # Set font for the report body
        pdf.set_font("Arial", size=12)

        # Add the report content
        lines = report.split('\n')

        for line in lines:
            # Adjust the line length to avoid text running off the page
            pdf.multi_cell(0, 10, line)
        
        # Add footer (e.g., page number)
        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, "C")

        # Output the PDF to the file
        pdf.output(output_pdf_path)
        
        # Log success message
        print(f"PDF generated successfully at {output_pdf_path}")
        return True  # Return success status

    except Exception as e:
        # Log error message
        print(f"Error generating PDF: {e}")
        return False  # Return failure status
