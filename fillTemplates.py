__author__ = 'Benjamin'
# -*- coding: utf-8 -*-


import os, xlrd, re, html, configparser
from shutil import copyfile
from datetime import datetime

# initialize vars and open xlsx file
src = 'collection.xlsx'
book = xlrd.open_workbook(src)
sheet = book.sheet_by_name('Data')
numRows = sheet.nrows - 1
numCols = sheet.ncols
currentRow = 1

# read config file
config = configparser.RawConfigParser()
config.read(r'config.txt')
showColumns = int(config.get('config', 'showColumns'))
dateFormat = config.get('config', 'dateFormat')
background = config.get('config', 'background')
altImage = config.get('config', 'altImage')
indexTitle = config.get('config', 'indexTitle')
imgTarget = ''
if 'Y' == config.get('config', 'OpenImgOnNewTab'):
    imgTarget = ' target="_blank"'

# set index template vars
platformSheet = book.sheet_by_name('Platforms')
numPlatforms = platformSheet.nrows - 1
trows = ''


def replacePlaceholder(placeholder, replacement, filepath):
    with open(filepath, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(placeholder, replacement)

    with open(filepath, 'w') as file:
        file.write(filedata)
    file.close()

# if there's a details folder, it removes the contents - otherwise the folder is created and filled with css (otherwise removing rows in the xlsx gives problems).
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
replacePlaceholder('[[BACKGROUND]]', background, cssDirectory + '\detailpage.css')
replacePlaceholder('[[BACKGROUND]]', background, cssDirectory + '\index.css')
copyfile(templatesDirectory + '\indexTemplate.html', 'site\index.html')
copyfile('code\js\sorttable.js', jsDirectory + '\sorttable.js')
templateName = templatesDirectory + '\detailTemplate.xhtml'


# index template methods
def buildTHeaders():
    theaders = ''
    contentLabels = ''
    curCol = 0
    while curCol < numCols and curCol < showColumns:
        thead = sheet.cell_value(0, curCol)
        if(curCol == 0):
            contentLabels += 'td:nth-of-type(1):before { content: "' + thead + '";}\n'
            theaders += ('<th class="col-xs-2">' + thead + '</th>\n')
        elif('img' not in str(thead).lower()):
            contentLabels += 'td:nth-of-type(' + str(curCol + 1) + '):before { content: "' + thead + '";}\n'
            theaders += ('<th class="col-xs-1">' + thead + '</th>\n')
        curCol += 1
    replacePlaceholder('[[CONTENTLABELS]]', contentLabels, cssDirectory + '\index.css')
    return theaders

# build the dropdown options
def buildOptions():
    options = ''
    curRow = 0
    while curRow < numPlatforms:
        platform = platformSheet.cell_value(curRow, 0)
        options += ('<option value="' + platform + '">' + platform + '</option>\n')
        curRow += 1
    return options

# replace the placeholders [[OPTIONS]], [[THEADERS]] and [[TROWS]] in the indexTemplate
def fillIndexTemplate():
    indexFile = 'site\index.html'
    options = buildOptions()
    theaders = buildTHeaders()
    with open(indexFile, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[INDEXTITLE]]', indexTitle)
    filedata = filedata.replace('[[OPTIONS]]', options)
    filedata = filedata.replace('[[THEADERS]]', theaders)
    filedata = filedata.replace('[[TROWS]]', trows)

    with open(indexFile, 'w') as file:
        file.write(filedata)
    file.close()


def trSurround(platform, link, tds):
    return '<tr data-status="' + platform + '" onclick="document.location = \'' + 'details/' + link + '\';">\n' + tds + '</tr>'


def tdSurround(string, isDate):
    if (isDate):
        return '<td sorttable_customkey="' + datetime.strptime(string, dateFormat).strftime('%Y%m%d') + '">' + string + '</td>\n'
    else:
        return '<td>' + string + '</td>\n'


def imgSurround(imgUrl):
    return '<a href="' + imgUrl + '"' + imgTarget + '><img src="' + imgUrl + '"/></a>\n'


# removes the punctuation marks from the filename, otherwise windows can't create the file or the link can't be opened
def cleanFileName(string):
    return re.sub(r'[^\w\s]','',string)

def removeIllegalCharsFromString(string):
    return html.escape(string.replace('é', 'e'))


# replace the placeholders [[TITLE]], [[DETAILS]] and [[IMAGES]] in the templates
def fillDetailsTemplate(title, details, imgs, filename):
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('[[TITLE]]', removeIllegalCharsFromString(title))
    filedata = filedata.replace('[[DETAILS]]', details)
    if(imgs == ''):
        filedata = filedata.replace('[[IMAGES]]', '<img src="' + altImage +'" />')
    else:
        filedata = filedata.replace('[[IMAGES]]', imgs)

    with open(filename, 'w') as file:
        file.write(filedata)
    file.close()


def initTemplate(filename):
    copyfile(templateName, filename)


def getDateAsString(date):
    date = datetime(*xlrd.xldate_as_tuple(date, book.datemode))
    return date.strftime(dateFormat)


# read the collecion.xlsx, make a template page for each row and fetch title and details
while currentRow < numRows+1:
    currentCol = 0
    details = ''
    trow = ''
    imgs = ''

    numTitle = str(currentRow) + ' - ' + cleanFileName(sheet.cell_value(currentRow, 0)) + '.xhtml'
    filename = detailsDirectory + '\\' + numTitle
    title = sheet.cell_value(currentRow, 0)
    platform = sheet.cell_value(currentRow, 1)
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
                cellValue = removeIllegalCharsFromString(str(cellValue))
                details += columnName + ": " + cellValue + '<br />'

        if 'img' not in str(columnName).lower() and currentCol < showColumns:
            trow += tdSurround(cellValue, isDate)
        currentCol += 1
    trows += trSurround(platform, numTitle, trow)
    fillDetailsTemplate(title, details, imgs, filename)
    print(details)
    currentRow += 1

fillIndexTemplate()