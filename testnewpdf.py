from xhtml2pdf import pisa             # import python module

# Define your data
sourceHtml =  "<!DOCTYPE html> <html> <head> <style> table { font-family: arial, sans-serif; border-collapse: collapse; width: 100%; } td, th { border: 1px solid black; text-align: left; padding: 8px; } th { border: 1px solid black; text-align: center; padding: 8px; } </style> </head> <body> <p>Your team has incurred the following costs this quarter.Your WBS will be charged by the end of the week</p> <table border = 2> <tbody> <tr> <th colspan=2>CBCAP Quarterly Invoice</th> </tr> <tr> <td>InvoiceDate</td> <td></td> </tr> <tr> <td>Application Number</td> <td> </td> </tr> <tr> <td>Application Name</td> <td> </td> </tr> <tr> <td>WBS</td> <td> </td> </tr> <tr> <td>Sponser PPMD </td> <td></td> </tr> <tr> <td>Billing Period</td> <td></td> </tr> <tr> <td colspan=2></td> </tr> <tr> <th style = "'float:left; border:none'">Estimate Total</th> <th></th> </tr> <tr> <td colspan=2></td> </tr> <tr> <td colspan=2>Hosting Details:</td> </tr> <tr> <td colspan=2>The inovice cost for All AWS services</td> </tr> <tr> <td colspan=2></td> </tr> <tr> <td>Hosting Total</td> <td></td> </tr> <tr> <td colspan=2>3rd party licence details:</td> </tr> <tr> <td colspan=2>The inovice cost for All 3rd party services cost</td> </tr> <tr> <td>3rd party licenceTotal</td> <td></td> </tr> </tbody> </table> <p>copyrights</p> </body> </html>"
outputFilename = "NEwHTMLTOPDF.pdf"

# Utility function
def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            sourceHtml,                # the HTML to convert
            dest=resultFile)           # file handle to recieve result

    # close output file
    resultFile.close()                 # close output file

    # return True on success and False on errors
    return pisaStatus.err

# Main program
if __name__ == "__main__":
    pisa.showLogging()
    convertHtmlToPdf(sourceHtml, outputFilename)

