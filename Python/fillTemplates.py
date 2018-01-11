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

#mogelijk voor de config:
show_columns = 7 #bepaald hoeveel kolommen zichtbaar zijn


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
    while curCol < num_cols and curCol < show_columns:
        thead = sheet.cell_value(0, curCol)
        if('img' not in str(thead).lower()):
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


templateName = '..\detailTemplate.xhtml'


def trSurround(platform, link, tds):
    return trStart + platform + trMiddle + 'details/' + link + trEnd + tds + '</tr>'


def tdSurround(string, isDate):
    if (isDate):
        return '<td sorttable_customkey="' + datetime.strptime(string, '%d-%m-%Y').strftime('%Y%m%d') + '">' + string + '</td>\n'
    else:
        return '<td>' + string + '</td>\n'


def imgSurround(imgUrl):
    return '<img src="' + imgUrl + '"/>\n'


# Verwijderd leestekens uit de filenaam, anders kan windows de file niet aanmaken of de link niet geopend worden
def cleanString(string):
    return re.sub(r'[^\w\s]','',string)


# vul de placeholders [[TITLE]], [[DETAILS]] en [[IMAGES]] in de templates
def fillTemplate(title, details, imgs, filename):
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[TITLE]]', title)
    filedata = filedata.replace('[[DETAILS]]', details)
    if(imgs == ''):
        filedata = filedata.replace('[[IMAGES]]', '<img src="https://www.socabelec.co.ke/wp-content/uploads/no-photo-14.jpg" />')
    else:
        filedata = filedata.replace('[[IMAGES]]', imgs)

    with open(filename, 'w') as file:
        file.write(filedata)


def initTemplate(filename):
    copyfile(templateName, filename)


def getDateAsString(date):
    date = datetime(*xlrd.xldate_as_tuple(date, book.datemode))
    return date.strftime('%d-%m-%Y')


# lees de collection.xlsx uit, maak een template pagina voor de regel en haal titel en details op
while current_row < num_rows+1:
    current_col = 0
    details = ''
    platform = ''
    trow = ''
    imgs = ''

    numTitle = str(current_row) + ' - ' + cleanString(sheet.cell_value(current_row, 0)) + '.xhtml'
    filename = '..\details\\' + numTitle
    title = sheet.cell_value(current_row, 0)
    initTemplate(filename)
    while current_col < num_cols:
        cellValue = sheet.cell_value(current_row, current_col)
        isDate = False
        columnName = sheet.cell_value(0, current_col)
        if cellValue != '':
            if 'img' in str(columnName).lower():
                imgs += imgSurround(cellValue)
            else:
                if 'date' in str(columnName).lower() or 'datum' in str(columnName).lower():
                    isDate = True
                    cellValue = getDateAsString(cellValue)
                elif columnName == 'Platform':
                    platform = cellValue
                details += columnName + ": " + str(cellValue) + '<br />'

        if 'img' not in str(columnName).lower() and current_col < show_columns:
            trow += tdSurround(cellValue, isDate)
        current_col += 1
    trows += trSurround(platform, numTitle, trow)
    fillTemplate(title, details, imgs, filename)
    print(details)
    current_row += 1

fillIndexTemplate()