__author__ = 'Benjamin'

import os, xlrd, re
from shutil import copyfile
from datetime import datetime

# initialiseer vars en open xlsx file
src = '..\collection.xlsx'
book = xlrd.open_workbook(src)
sheet = book.sheet_by_name('Data')
num_rows = sheet.nrows - 1
num_cols = sheet.ncols
current_row = 1

# set index template vars
platformSheet = book.sheet_by_name('Platforms')
num_platforms = platformSheet.nrows - 1
buttonStart = '<button type="button" class="btn btn-success btn-filter" data-target="'
buttonMiddle = '">'
buttonEnd = '</button>\n'
theadStart = '<th class="col-xs-2">'
theadEnd = '</th>\n'
trStart = '<tr data-status="'
trMiddle = '" onclick="document.location = \''
trEnd = '\';">\n'
trows = ''


# index template methods
def buildButtons():
    buttons = ''
    curRow = 0
    while curRow < num_platforms:
        platform = platformSheet.cell_value(curRow, 0)
        buttons += (buttonStart + platform + buttonMiddle + platform + buttonEnd)
        curRow += 1
    return buttons

def buildTHeaders():
    theaders = ''
    curCol = 0
    while curCol < num_cols:
        thead = sheet.cell_value(0, curCol)
        theaders += (theadStart + thead + theadEnd)
        curCol += 1
    return theaders

# vul de placeholders [[BUTTONS]], [[THEADERS]] en [[TROWS]] in de indexTemplate
def fillIndexTemplate():
    indexFile = '..\index.html'
    buttons = buildButtons()
    theaders = buildTHeaders()
    with open(indexFile, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[BUTTONS]]', buttons)
    filedata = filedata.replace('[[THEADERS]]', theaders)
    filedata = filedata.replace('[[TROWS]]', trows)

    with open(indexFile, 'w') as file:
        file.write(filedata)

# als er nog geen details map bestaat, wordt deze hier gemaakt en de css wordt erin gekopieerd.
detailsDirectory = '..\details'
if not os.path.exists(detailsDirectory):
    os.makedirs(detailsDirectory)
copyfile('..\detailTemplate.css', detailsDirectory + '\detailTemplate.css')
copyfile('..\indexTemplate.html', '..\index.html')

# als er nog geen images map bestaat, wordt deze hier gemaakt.
imgDirectory = '..\images'
if not os.path.exists(imgDirectory):
    os.makedirs(imgDirectory)

templateName = '..\detailTemplate.xhtml'


def trSurround(platform, link, tds):
    return trStart + platform + trMiddle + 'details/' + link + trEnd + tds + '</tr>'


def tdSurround(string):
    return '<td>' + string + '</td>\n'


# Verwijderd leestekens uit de filenaam, anders kan windows de file niet aanmaken of de link niet geopend worden
def cleanString(string):
    return re.sub(r'[^\w\s]','',string)


# vul de placeholders [[TITLE]] en [[DETAILS]] in de templates
def fillTemplate(title, details, filename):
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[TITLE]]', title)
    filedata = filedata.replace('[[DETAILS]]', details)

    with open(filename, 'w') as file:
        file.write(filedata)


def initTemplateAndImgFolderForTitle(title, filename, row):
    copyfile(templateName, filename)
    titleImgDirectory = imgDirectory + '\\' + str(row) + cleanString(title)
    if not os.path.exists(titleImgDirectory):
        os.makedirs(titleImgDirectory)


def getDateAsString(date):
    date = datetime(*xlrd.xldate_as_tuple(date, book.datemode))
    return date.strftime('%d %B %Y')


# lees de collection.xlsx uit, maak een template pagina voor de regel en haal titel en details op
while current_row < num_rows:
    current_col = 0
    details = ''
    platform = ''
    trow = ''

    numTitle = str(current_row) + ' - ' + cleanString(sheet.cell_value(current_row, 0)) + '.xhtml'
    filename = '..\details\\' + numTitle
    title = sheet.cell_value(current_row, 0)
    initTemplateAndImgFolderForTitle(title, filename, current_row)
    while current_col < num_cols:
        cellValue = sheet.cell_value(current_row, current_col)
        if cellValue != '':
            if sheet.cell_value(0, current_col) == 'Release date':
                cellValue = getDateAsString(cellValue)
            if sheet.cell_value(0, current_col) == 'Platform':
                platform = cellValue
            details += sheet.cell_value(0, current_col) + ": " + str(cellValue) + '<br />'
        trow += tdSurround(cellValue)
        current_col += 1
    trows += trSurround(platform, numTitle, trow)
    fillTemplate(title, details, filename)
    print(details)
    current_row += 1

fillIndexTemplate()