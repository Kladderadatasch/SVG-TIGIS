#!/usr/bin/env python3
import cx_Oracle
import cgitb
import folium
import cgi


cgitb.enable(format = 'text')
from jinja2 import Environment, FileSystemLoader

'''Retrieving coordinates from DB - Essential Data'''
'''First DB connection function'''
def coordinatesHtml(coord = "Fields",x = True, y = False):
    conn = cx_Oracle.connect("student/train@geosgen")
    c = conn.cursor()
    if coord == "Fields":
        if x == True and y == False:
            c.execute("SELECT LOWX,HIX FROM GISTEACH.FIELDS")
            list = []
            for row in c:
                list.append(row)
            return list
        elif x == False and y == True:
            c.execute("SELECT LOWY,HIY FROM GISTEACH.FIELDS")
            list = []
            for row in c:
                list.append(row)
            return list
        else:
            print('''Please select either x or y to be True and the counterpart \
    to be False. Both x = True, y = True or x = False, y = False are not valid.''')
    elif coord == "Points":
        c.execute("SELECT XCOORD,YCOORD FROM GISTEACH.FINDS")
        list = []
        for row in c:
            list.append(row)
        return list

    else:
        print('''"Please select coord = "Fields" or coord = "Points"''')

    conn.close()

'''Retrieving ownership, crops, area, etc. data from DB - Secondary data'''
'''Second DB connection function'''
'''Joining of data made inside DB'''

def dataHtml(fields = True, finds = False):
    conn = cx_Oracle.connect("student/train@geosgen")
    c = conn.cursor()
    if fields == True:
        c.execute("SELECT FIELD_ID,LOWX,LOWY,HIX,HIY,AREA,OWNER,NAME,START_OF_SEASON, END_OF_SEASON FROM GISTEACH.FIELDS, GISTEACH.CROPS WHERE GISTEACH.FIELDS.CROP = GISTEACH.CROPS.CROP")
#        SELECT * FROM GISTEACH.CROPS;
#        JOIN SELECTION IN DB
        list = []
        dict = {'FieldID':[],'LowX':[],'LowY':[],'HiX':[],'HiY':[],'Area':[],'Owner':[],'Crop':[],'StartSeason':[],'EndSeason':[]}
        for row in c:
            list.append(row)
        for row in range(len(list)):
#            Append
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
#            Update - Relative and Y Inverted Coordinates
        maxX = max(dict['HiX'])
        maxY = max(dict['HiY'])
        for row in range(len(list)):
            dict['LowX'][row]= ((dict['LowX'][row]/maxX))*100
            dict['LowY'][row]= (1-(dict['LowY'][row]/maxY))*100
            dict['HiX'][row]= ((dict['HiX'][row]/maxX))*100
            dict['HiY'][row]= (1-(dict['HiY'][row]/maxY))*100
        return dict
    elif finds == True:
        c.execute("SELECT FIND_ID, XCOORD, YCOORD, NAME, PERIOD, USE, DEPTH, FIELD_NOTES FROM GISTEACH.FINDS, GISTEACH.CLASS WHERE GISTEACH.FINDS.TYPE = GISTEACH.CLASS.TYPE")
        list = []
        dict = {'FindID':[],'XCoord':[],'YCoord':[],'Name':[],'Period':[],'Use':[],'Depth':[],'FieldNotes':[]}
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
#            Update - Relative and Y Inverted Coordinates
        maxX = max(dict['XCoord'])
        maxY = max(dict['YCoord'])
        for row in range(len(list)):
            dict['XCoord'][row] = ((dict['XCoord'][row]/maxX))*100
            dict['YCoord'][row] = (1-(dict['YCoord'][row]/maxY))*100
        return dict

    conn.close()


'''Template Creation'''
'''Setting Environment'''

def print_html():
    env = Environment(loader = FileSystemLoader('../'))
    temp = env.get_template('SVG.html')
    XFields = coordinatesHtml(x = True, y = False)
    YFields = coordinatesHtml(x = False, y = True)
    Points = coordinatesHtml(coord = "Points")
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

    for row in range(len(XFields)):
        print('''#r'''+str(row)+''' {
fill: #'''+str(colorramp[row+10])+''';}\n''')


    print('''</style>\n''')
    print('''</head>\n<body>''')

    #remove .face later
#    print('''Content-Type: text/html\n\n\
#<!DOCTYPE html>\n\
#<head>\n\
#<title>SVG Mapping</title>\n\
#<style type="text/css" media="screen">\n
#html, body { margin:0; padding:0; overflow:hidden }\n
#svg { position:fixed; top:0; bottom:0; left:0; right:0 }\n
#</style>\n
#</head>\n<body>''')


    '''Dynamic SVG Extent'''

    print('''<svg viewBox="-5 -4 110 110" >\n''')

    maxX = max(XFields,key=lambda item:item[1])[1]
    maxY = max(YFields,key=lambda item:item[1])[1]

    i = 1
    j = 1

    '''Grid Labelling'''
    '''Static Values for neat positioning'''
    '''Y Axis Inverted'''
    while True:
        xticks = float((i/maxX)*100)
        print('''<text font-size="2" x="'''+str(xticks -0.5)+'''" y="103">'''+str(i)+'''</text>''')
        i = i + 1
        if i == maxX + 1:
            print('''<text font-size="2" x="'''+str(0)+'''" y="103">'''+str(0)+'''</text>''')
            break
    while True:
        yticks = float((j/maxY)*100)
        print('''<text font-size="2" x="-3" y="'''+str(yticks +0.5)+'''" >'''+str(-1*(j-maxY))+'''</text>''')
        j = j + 1
        if j == maxY + 1:
            print('''<text font-size="2" x="-3" y="'''+str(0)+'''" >'''+str(maxY)+'''</text>''')
            break

    '''Grid Computing'''
    i = 1
    j = 1

    while True:
        xticks = str(float((i/maxX)*100))
        print('''<line x1='''+xticks+''' y1=0 x2='''+xticks+''' y2=100 class = "line" /> ''')
        i = i + 1
        if i == maxX:
            break
    while True:
        yticks = str(float((j/maxY*100)))
        print('''<line x1=0 y1='''+yticks+''' x2=100 y2='''+yticks+''' class = "line"/> ''')
        j = j + 1
        if j == maxY:
            break



    '''Rectangle Computing'''


#   Fill + transparency + hovering
#   Labelling + hovering [Owner + Crop + Extent]
#   OnClick [Popup of finds at coordinates]

    for row in range(len(fields['FieldID'])):
   
        lowX = fields['LowX'][row]
        lowY = fields['LowY'][row]
        highX = fields['HiX'][row]
        highY = fields['HiY'][row]
        
        print ('''\n<polygon points="'''+str(lowX)+''' '''+str(lowY)+''', '''+str(highX)+''' '''+str(lowY)+''', \
'''+str(highX)+''' '''+str(highY)+''', '''+str(lowX)+''' '''+str(highY)+'''" class="fields" id="r'''+str(row)+'''" \
onclick="changeClassFromIDr'''+str(row)+'''()" />''')



#    '''Text Computing'''
        i = 1
        print('''<text class="hidden" id="textr'''+str(row)+'''Nr'''+str(i)+'''" x="'''+str(lowX)+'''" y="'''+str(lowY+5)+'''">\
Field ID:'''+str(fields['FieldID'][row])+'''\n</text>''')
        i = i + 1
        print('''<text class="hidden" id="textr'''+str(row)+'''Nr'''+str(i)+'''" x="'''+str(lowX)+'''" y="'''+str(lowY+10)+'''">\
Owner:'''+str(fields['Owner'][row])+'''\n</text>''')
        i = i + 1
        print('''<text class="hidden" id="textr'''+str(row)+'''Nr'''+str(i)+'''" x="'''+str(lowX)+'''" y="'''+str(lowY+15)+'''">\
Area:'''+str(fields['Area'][row])+'''\n</text>''')
        i = i + 1
        print('''<text class="hidden" id="textr'''+str(row)+'''Nr'''+str(i)+'''" x="'''+str(lowX)+'''" y="'''+str(lowY+20)+'''">\
CropID:'''+str(fields['Crop'][row])+'''\n</text>''')

    '''Findings Computing'''
    for row in range(len(finds['FindID'])):
        X = finds['XCoord'][row]
        Y = finds['YCoord'][row]

        print ('''<circle cx="'''+str(X)+'''" cy="'''+str(Y)+'''" r="1" fill="blue" />''')

    '''InfoIcon Computing'''
    print('''<g id="myicon" pointer-events="all" transform="translate(0,0)">\n\
    <circle cx="22" cy="9" r="3.5" fill="none" stroke="gold" stroke-width="0.5"/>\n\
    <circle cx="22" cy="7.7" r="0.5" fill="gold"/>\n\
    <rect x="21.625" y="8.8" width="0.75" height="2.5" fill="gold"/>\n\
  </g>''')
    print("</svg>\n")

    '''PopUp Text'''
    print('''<div id="mypopup">\n\
<h3>Popup title</h3>\n\
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit,\
 sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\
 Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>\n\
<p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\
 Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>\n\
</div>\n''')

    '''JavaScript'''

    for row in range(len(XFields)):
        print('''<script>\nfunction changeClassFromIDr'''+str(row)+'''() {\n''')
        for i in range(len(fields)):
            print('''document.getElementById('textr'''+str(row)+'''Nr'''+str(i+1)+'''').classList.toggle('visible');\n''')
        print('''}\n</script>''')

    '''PopUp Script'''

    print('''<script>\nvar myicon = document.getElementById("myicon");\n\
var mypopup = document.getElementById("mypopup");\n\
myicon.addEventListener("mouseover", showPopup);\n\
myicon.addEventListener("mouseout", hidePopup);\n\
\n\
function showPopup(evt) {\n\
var iconPos = myicon.getBoundingClientRect();\n\
mypopup.style.left = (iconPos.right + 20) + "px";\n\
mypopup.style.top = (window.scrollY + iconPos.top - 60) + "px";\n\
mypopup.style.display = "block";\n\
}\n\
function hidePopup(evt) {\n\
  mypopup.style.display = "none";\n\
}\n</script>''')

    print("</body>\n</html>")
    print(temp.render())

#run
if __name__ == '__main__':
    print_html()
