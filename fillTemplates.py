__author__ = 'Benjamin'
# -*- coding: utf-8 -*-


import os, xlrd, re, html
from shutil import copyfile
from datetime import datetime

# initialiseer vars en open xlsx file
src = 'collection.xlsx'
book = xlrd.open_workbook(src)
sheet = book.sheet_by_name('Data')
numRows = sheet.nrows - 1
numCols = sheet.ncols
currentRow = 1

#mogelijk voor de config:
showColumns = 7 #bepaald hoeveel kolommen zichtbaar zijn
dateFormat = '%d-%m-%Y'


# set index template vars
platformSheet = book.sheet_by_name('Platforms')
numPlatforms = platformSheet.nrows - 1
optionStart = '<option value="'
optionMiddle = '">'
optionEnd = '</option>\n'
theadStart = '<th class="col-xs-2">'
theadEnd = '</th>\n'
trStart = '<tr data-status="'
trMiddle = '" onclick="document.location = \''
trEnd = '\';">\n'
trows = ''


# index template methods
def buildTHeaders():
    theaders = ''
    curCol = 0
    while curCol < numCols and curCol < showColumns:
        thead = sheet.cell_value(0, curCol)
        if('img' not in str(thead).lower()):
            theaders += (theadStart + thead + theadEnd)
        curCol += 1
    return theaders

# build the dropdown options
def buildOptions():
    options = ''
    curRow = 0
    while curRow < numPlatforms:
        platform = platformSheet.cell_value(curRow, 0)
        options += (optionStart + platform + optionMiddle + platform + optionEnd)
        curRow += 1
    return options

# vul de placeholders [[OPTIONS]], [[THEADERS]] en [[TROWS]] in de indexTemplate
def fillIndexTemplate():
    indexFile = 'site\index.html'
    options = buildOptions()
    theaders = buildTHeaders()
    with open(indexFile, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[OPTIONS]]', options)
    filedata = filedata.replace('[[THEADERS]]', theaders)
    filedata = filedata.replace('[[TROWS]]', trows)

    with open(indexFile, 'w') as file:
        file.write(filedata)

# als er een details map bestaat, wordt de inhoud hier verwijderd, anders wordt hij aangemaakt en wordt de css erin gekopieerd (anders geeft spellen verwijderen problemen).
detailsDirectory = 'site\details'
templatesDirectory = 'code\\templates'
cssDirectory = 'site\css'
jsDirectory = 'site\js'
if os.path.exists(detailsDirectory):
    for file in os.listdir(detailsDirectory):
        os.remove(detailsDirectory+'\\'+file)
else:
    os.makedirs('site')
    os.makedirs(detailsDirectory)
    os.makedirs(cssDirectory)
    os.makedirs(jsDirectory)
copyfile(templatesDirectory + '\detailpage.css', cssDirectory + '\detailpage.css')
copyfile(templatesDirectory + '\index.css', cssDirectory + '\index.css')
copyfile(templatesDirectory + '\indexTemplate.html', 'site\index.html')
copyfile('code\js\sorttable.js', jsDirectory + '\sorttable.js')
templateName = templatesDirectory + '\detailTemplate.xhtml'


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
def cleanFileName(string):
    return re.sub(r'[^\w\s]','',string)

def removeIllegalCharsFromString(string):
    return html.escape(string.replace('é', 'e'))


# vul de placeholders [[TITLE]], [[DETAILS]] en [[IMAGES]] in de templates
def fillTemplate(title, details, imgs, filename):
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[TITLE]]', removeIllegalCharsFromString(title))
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
    return date.strftime(dateFormat)


# lees de collection.xlsx uit, maak een template pagina voor de regel en haal titel en details op
while currentRow < numRows+1:
    currentCol = 0
    details = ''
    platform = ''
    trow = ''
    imgs = ''

    numTitle = str(currentRow) + ' - ' + cleanFileName(sheet.cell_value(currentRow, 0)) + '.xhtml'
    filename = detailsDirectory + '\\' + numTitle
    title = sheet.cell_value(currentRow, 0)
    initTemplate(filename)
    while currentCol < numCols:
        cellValue = sheet.cell_value(currentRow, currentCol)
        isDate = False
        columnName = sheet.cell_value(0, currentCol)
        if cellValue != '':
            if 'img' in str(columnName).lower():
                imgs += imgSurround(cellValue)
            else:
                if 'date' in str(columnName).lower() or 'datum' in str(columnName).lower():
                    isDate = True
                    cellValue = getDateAsString(cellValue)
                elif columnName == 'Platform':
                    platform = cellValue
                cellValue = removeIllegalCharsFromString(str(cellValue))
                details += columnName + ": " + cellValue + '<br />'

        if 'img' not in str(columnName).lower() and currentCol < showColumns:
            trow += tdSurround(cellValue, isDate)
        currentCol += 1
    trows += trSurround(platform, numTitle, trow)
    fillTemplate(title, details, imgs, filename)
    print(details)
    currentRow += 1

fillIndexTemplate()