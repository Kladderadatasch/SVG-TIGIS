#!/usr/bin/env python3
import cx_Oracle
import cgitb
import folium
import cgi
import re


cgitb.enable(format = 'text')
from jinja2 import Environment, FileSystemLoader

'''Modifying text from DB'''
def replacement(match):
    return match.group().lower()


'''Retrieving ownership, crops, area, etc. data from DB - Secondary data'''
'''Joining of data made inside DB'''

def dataHtml(fields = True, finds = False):
    conn = cx_Oracle.connect("student/train@geosgen")
    c = conn.cursor()
    if fields == True:
        c.execute("SELECT FIELD_ID,LOWX,LOWY,HIX,HIY,AREA,OWNER,NAME,START_OF_SEASON, END_OF_SEASON FROM GISTEACH.FIELDS, GISTEACH.CROPS WHERE GISTEACH.FIELDS.CROP = GISTEACH.CROPS.CROP")
        list = []
        dict = {'FieldID':[],'LowX':[],'LowY':[],'HiX':[],'HiY':[],'Area':[],'Owner':[],'Crop':[],'StartSeason':[],'EndSeason':[],'MaxCoord':[]}
        replace = ['Owner','Crop']
        for row in c:
            list.append(row)
            
#       Append
        for row in range(len(list)):              
            dict['FieldID'].append(list[row][0])
            dict['LowX'].append(list[row][1])
            dict['LowY'].append(list[row][2])
            dict['HiX'].append(list[row][3])
            dict['HiY'].append(list[row][4])
            dict['Area'].append(list[row][5])
            dict['Owner'].append(list[row][6])
            dict['Crop'].append(list[row][7])
            dict['StartSeason'].append(list[row][8])
            dict['EndSeason'].append(list[row][9])
            
#        Modify Text recieved from DB    
        for i in range(len(dict['FieldID'])):    
            for j in range(len(replace)):
                dict[replace[j]][i] = re.sub(r"[A-Z]",replacement,dict[replace[j]][i]).title()
            
#            Update - Relative and Y Inverted Coordinates
        maxX = max(dict['HiX'])
        maxY = max(dict['HiY'])
        if maxX > maxY:
            dict['MaxCoord'].append(maxX)
            maximum = maxX
        else:
            dict['MaxCoord'].append(maxY)
            maximum = maxY
        for row in range(len(list)):
            dict['LowX'][row]= ((dict['LowX'][row]/maximum))*100
            dict['LowY'][row]= (1-(dict['LowY'][row]/maximum))*100
            dict['HiX'][row]= ((dict['HiX'][row]/maximum))*100
            dict['HiY'][row]= (1-(dict['HiY'][row]/maximum))*100

        return dict
    elif finds == True:
        c.execute("SELECT FIND_ID, XCOORD, YCOORD, NAME, PERIOD, USE, DEPTH, FIELD_NOTES FROM GISTEACH.FINDS, GISTEACH.CLASS WHERE GISTEACH.FINDS.TYPE = GISTEACH.CLASS.TYPE")
        list = []
        dict = {'FindID':[],'XCoord':[],'YCoord':[],'Name':[],'Period':[],'Use':[],'Depth':[],'FieldNotes':[]}
        replace = ['Name','Period','Use','FieldNotes']
        for row in c:
            list.append(row)
        for row in range(len(list)):
            dict['FindID'].append(list[row][0])
            dict['XCoord'].append(list[row][1])
            dict['YCoord'].append(list[row][2])
            dict['Name'].append(list[row][3])
            dict['Period'].append(list[row][4])
            dict['Use'].append(list[row][5])
            dict['Depth'].append(list[row][6])
            dict['FieldNotes'].append(list[row][7])
            
#        Modify Text recieved from DB    
        for i in range(len(dict['FindID'])):    
            for j in range(len(replace)):
                dict[replace[j]][i] = re.sub(r"[A-Z]",replacement,dict[replace[j]][i]).title()
 
#            Update - Relative and Y Inverted Coordinates
        c.execute("SELECT HIX, HIY FROM GISTEACH.FIELDS")
        list = []
        corddict = {'HiX':[],'HiY':[]}
        for row in c:
            list.append(row)
        for row in range(len(list)):
            corddict['HiX'].append(list[row][0])
            corddict['HiY'].append(list[row][1])
        maxX = max(corddict['HiX'])
        maxY = max(corddict['HiY'])
        if maxX > maxY:
            maximum = maxX
        else:
            maximum = maxY
        for row in range(len(list)):
            dict['XCoord'][row] = ((dict['XCoord'][row]/maximum))*100
            dict['YCoord'][row] = (1-(dict['YCoord'][row]/maximum))*100
        return dict

    conn.close()


    '''Template Creation'''
    '''Setting Environment'''

def print_html():
    env = Environment(loader = FileSystemLoader('../'))
    temp = env.get_template('SVG.html')
    fields = dataHtml(fields = True)
    finds = dataHtml(fields = False, finds = True)

    '''Creating Header'''
    '''../ seems to be necessary, even .html and .css are in same folder'''
    '''rendering seems to look out in the .py dir'''

    #HTML Framkework
    print('''Content-Type: text/html\n\n\
<!DOCTYPE html>\n\
<head>\n\
<title>SVG Mapping</title>\n\
<link href="../styling.css" rel="stylesheet" type="text/css" >\n\
<link href="../popups.css" rel="stylesheet" type="text/css" >\n\
<style type="text/css" media="screen">\n
''')

    '''Dynamic InLine CSS'''
#   Add CSS above
    colorramp = ["F0F8FF","FAEBD7","00FFFF","7FFFD4","F0FFFF","F5F5DC","FFE4C4",
                 0,"FFEBCD","0000FF","8A2BE2","A52A2A","DEB887","5F9EA0",
                 "7FFF00","D2691E","FF7F50","6495ED","FFF8DC","DC143C",
                 "00FFFF","00008B","008B8B","B8860B","A9A9A9","A9A9A9",
                 6400,"BDB76B","8B008B","556B2F","FF8C00","9932CC","8B0000",
                 "E9967A","8FBC8F","483D8B","2F4F4F","2F4F4F","00CED1",
                 "9400D3","FF1493","00BFFF",696969,696969,"1E90FF",
                 "B22222","FFFAF0","228B22","FF00FF","DCDCDC","F8F8FF",
                 "FFD700","DAA520",808080,808080,8000,"ADFF2F","F0FFF0",
                 "FF69B4","CD5C5C","4B0082","FFFFF0","F0E68C","E6E6FA",
                 "FFF0F5","7CFC00","FFFACD","ADD8E6","F08080","E0FFFF",
                 "FAFAD2","D3D3D3","D3D3D3","90EE90","FFB6C1","FFA07A",
                 "20B2AA","87CEFA",778899,778899,"B0C4DE","FFFFE0","00FF00",
                 "32CD32","FAF0E6","FF00FF",800000,"66CDAA","0000CD","BA55D3",
                 "9370DB","3CB371","7B68EE","00FA9A","48D1CC","C71585",191970,
                 "F5FFFA","FFE4E1","FFE4B5","FFDEAD",80,"FDF5E6",808000,
                 "6B8E23","FFA500","FF4500","DA70D6","EEE8AA","98FB98",
                 "AFEEEE","DB7093","FFEFD5","FFDAB9","CD853F","FFC0CB",
                 "DDA0DD","B0E0E6",800080,663399,"FF0000","BC8F8F",41690,
                 "8B4513","FA8072","F4A460","2E8B57","FFF5EE","A0522D",
                 "C0C0C0","87CEEB","6A5ACD",708090,708090,"FFFAFA","00FF7F",
                 "4682B4","D2B48C",8080,"D8BFD8","FF6347","40E0D0","EE82EE",
                 "F5DEB3","FFFFFF","F5F5F5","FFFF00","9ACD32"]

    for row in range(len(fields['FieldID'])):
        print('''#r'''+str(row)+''' {
fill: #'''+str(colorramp[row+10])+''';}\n''')


    print('''</style>\n''')
    print('''</head>\n<body>''')

    '''Dynamic SVG Extent'''

    print('''<svg viewBox="-5 -4 110 110" >\n\
    <g class="grid>"''')


    '''Grid Labelling'''
    '''Static Values for neat positioning'''
    '''Y Axis Inverted'''

    i = 1
    j = 1

    while True:
        ticks = float((i/fields['MaxCoord'][0])*100)
        print('''<text font-size="2" x="'''+str(ticks -0.5)+'''" y="103">'''+str(i)+'''</text>''')
        print('''<text font-size="2" x="-3" y="'''+str(ticks +0.5)+'''" >'''+str(-1*(j-fields['MaxCoord'][0]))+'''</text>''')
        i = i + 1
        j = j + 1
        if i == fields['MaxCoord'][0] + 1:
            print('''<text font-size="2" x="'''+str(0)+'''" y="103">'''+str(0)+'''</text>''')
            print('''<text font-size="2" x="-3" y="'''+str(0)+'''" >'''+str(fields['MaxCoord'][0])+'''</text>''')
            break

    '''Grid Computing'''
    i = 1
    j = 1

    while True:
        ticks = str(float((i/fields['MaxCoord'][0])*100))
        print('''<line x1='''+ticks+''' y1=0 x2='''+ticks+''' y2=100 class = "line" /> ''')
        print('''<line x1=0 y1='''+ticks+''' x2=100 y2='''+ticks+''' class = "line"/> ''')
        i = i + 1
        if i == fields['MaxCoord'][0]:
            break

    print('''</g>''')


    '''Rectangle Computing'''

    print('''<g class="rectangles">''')
    for row in range(len(fields['FieldID'])):

        lowX = fields['LowX'][row]
        lowY = fields['LowY'][row]
        highX = fields['HiX'][row]
        highY = fields['HiY'][row]

        idX = (highX-((highX-lowX)/2))-2.5
        idY = (highY-((highY-lowY)/2))-2.5
        idW = 5
        idH = 5
        idTX = idX +1.8
        idTY = idY +3.5

        print('''<rect x="'''+str(idX)+'''" y="'''+str(idY)+'''" width="'''+str(idW)+'''" height="'''+str(idH)+'''" class="field_ids" />''')
        print('''<text x="'''+str(idTX)+'''" y="'''+str(idTY)+'''" class="field_id_text">'''+str(fields['FieldID'][row])+'''</text>''' )

        print ('''\n<polygon points="'''+str(lowX)+''' '''+str(lowY)+''', '''+str(highX)+''' '''+str(lowY)+''', \
'''+str(highX)+''' '''+str(highY)+''', '''+str(lowX)+''' '''+str(highY)+'''" class="fields" id="r'''+str(row)+'''" />''')

    print('''</g>''')


    '''Findings Computing'''

    print('''<g class="findings">''')
    for row in range(len(finds['FindID'])):
        X = finds['XCoord'][row]
        Y = finds['YCoord'][row]

        print ('''<circle id="findicon'''+str(finds['FindID'][row])+'''" class="finds" cx="'''+str(X)+'''" cy="'''+str(Y)+'''" r="1.5" />''')

    print('''</g>''')

    print('''<g class="legend" transform="translate(21,71)">\

    <rect id="outerrect" height="19" width="19" y="10" x="60"/>\
    <rect id="innerrect" height="4.6" width="4.6" y="15" x="62"/>\
    <ellipse ry="1.5" rx="1.5" id="circle" cy="25" cx="64"/>\
    <text class="legendtext" id="svg_6" y="18" x="70">Fields</text>\
    <text class="legendtext" id="svg_9" y="25.5" x="70">Finds</text>\

    </g>''')

    print("</svg>\n")

    '''Fields Text'''
    print('''<g class="text">''')
    for row in range(len(fields['FieldID'])):
        print('''<div id="fieldtext'''+str(row)+'''" class="fieldtext">\n\
<h3>Field</h3>\n\
<p>ID: '''+str(fields['FieldID'][row])+'''</p>\n\
<p>Owner: '''+str(fields['Owner'][row])+'''</p>\n\
<p>Crop: '''+str(fields['Crop'][row])+'''</p>\n\
<p>Start Season: '''+str(fields['StartSeason'][row])+'''</p>\n\
<p>End Season: '''+str(fields['EndSeason'][row])+'''</p>\n\
<p>Field Size: '''+str(fields['Area'][row])+'''</p></div>''')


    '''Finds Text'''
    for row in range(len(finds['FindID'])):
        print('''<div id="findtext'''+str(finds['FindID'][row])+'''" class="findtext">\n\
<h3>Artefact: '''+str(finds['Name'][row])+'''</h3>\n\
<p>ID: '''+str(finds['FindID'][row])+'''</p>\n\
<p>Depth: '''+str(finds['Depth'][row])+'''</p>\n\
<p>Period: '''+str(finds['Period'][row])+'''</p>\n\
<p>Use: '''+str(finds['Use'][row])+'''</p>\n\
<p>Field Notes: '''+str(finds['FieldNotes'][row])+'''</p></div>''')

    print('''</g>''')

    '''PopUp Fields Script'''
    print('''<g class="inlineJS">''')
    for row in range(len(fields['FieldID'])):
        print('''<script>\nvar myfield'''+str(row)+''' = document.getElementById("r'''+str(row)+'''");\n\
var myfieldpopup'''+str(row)+''' = document.getElementById("fieldtext'''+str(row)+'''");\n\
myfield'''+str(row)+'''.addEventListener("mouseover", showFieldPopup'''+str(row)+''');\n\
myfield'''+str(row)+'''.addEventListener("mouseout", hideFieldPopup'''+str(row)+''');\n\
\n\
function showFieldPopup'''+str(row)+'''(evt) {\n\
var FieldPos = myfield'''+str(row)+'''.getBoundingClientRect();\n\
myfieldpopup'''+str(row)+'''.style.left = (FieldPos.right + 20) + "px";\n\
myfieldpopup'''+str(row)+'''.style.top = (window.scrollY + FieldPos.top - 60) + "px";\n\
myfieldpopup'''+str(row)+'''.style.display = "block";\n\
}\n\
function hideFieldPopup'''+str(row)+'''(evt) {\n\
  myfieldpopup'''+str(row)+'''.style.display = "none";\n\
}\n</script>''')

    '''PopUp Finds Script'''
    for row in range(len(finds['FindID'])):
        print('''<script>\nvar myicon'''+str(row)+''' = document.getElementById("findicon'''+str(finds['FindID'][row])+'''");\n\
var mypopup'''+str(row)+''' = document.getElementById("findtext'''+str(finds['FindID'][row])+'''");\n\
myicon'''+str(row)+'''.addEventListener("mouseover", showPopup'''+str(finds['FindID'][row])+''');\n\
myicon'''+str(row)+'''.addEventListener("mouseout", hidePopup'''+str(finds['FindID'][row])+''');\n\
\n\
function showPopup'''+str(finds['FindID'][row])+'''(evt) {\n\
var iconPos = myicon'''+str(row)+'''.getBoundingClientRect();\n\
mypopup'''+str(row)+'''.style.left = (iconPos.right + 20) + "px";\n\
mypopup'''+str(row)+'''.style.top = (window.scrollY + iconPos.top - 60) + "px";\n\
mypopup'''+str(row)+'''.style.display = "block";\n\
}\n\
function hidePopup'''+str(finds['FindID'][row])+'''(evt) {\n\
  mypopup'''+str(row)+'''.style.display = "none";\n\
}\n</script>''')

    print("</g>\n</body>\n</html>")
    print(temp.render())

#run
if __name__ == '__main__':
    print_html()
