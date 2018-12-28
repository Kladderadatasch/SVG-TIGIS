#!/usr/bin/env python3
import cx_Oracle
import cgitb
import folium
import cgi


cgitb.enable(format = 'text')
from jinja2 import Environment, FileSystemLoader

#Getting coordinates from DB
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


#Render the template
#Create Framework
    #Encapsulate CSS in external files
def print_html():
    env = Environment(loader = FileSystemLoader('.'))
    temp = env.get_template('SVG.html')
    XFields = coordinatesHtml(x = True, y = False)
    YFields = coordinatesHtml(x = False, y = True)
    Points = coordinatesHtml(coord = "Points")

    #HTML Framkework
    print('''Content-Type: text/html\n\n\
<!DOCTYPE html>\n\
<head>\n\
<title>SVG Mapping</title>\n\
<link href="../styling.css" rel="stylesheet" type="text/css" >\n\
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


    print('''</style>\n</head>\n<body>''')

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

    for row in range(len(XFields)):
        lowX = str((XFields[row][0]/maxX)*100)
        highX = str((XFields[row][1]/maxX)*100)

        lowY = str((YFields[row][0]/maxY)*100)
        highY = str((YFields[row][1]/maxY)*100)

        print ('''<polygon points="'''+lowX+''' '''+lowY+''', '''+highX+''' '''+lowY+''', \
'''+highX+''' '''+highY+''', '''+lowX+''' '''+highY+'''" class="fields" id="r'''+str(row)+'''" />''')

    for row in range(len(Points)):
        X = str((Points[row][0]/maxX)*100)
        Y = str((Points[row][1]/maxX)*100)

        print ('''<circle cx="'''+X+'''" cy="'''+Y+'''" r="1" fill="blue" />''')


    print("</svg>\n</svg>\n")
    print("</body>\n</html>")

    print(temp.render())

#run
if __name__ == '__main__':
    print_html()
