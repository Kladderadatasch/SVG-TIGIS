#!/usr/bin/env python3
import cx_Oracle
import cgitb
import folium
import cgi


cgitb.enable(format = 'text')
from jinja2 import Environment, FileSystemLoader

#Getting coordinates from DB
def coordinatesHtml():
    conn = cx_Oracle.connect("student/train@geosgen")
    c = conn.cursor()
    c.execute("SELECT HIX,HIY FROM GISTEACH.FIELDS")
    
    list = []
    for row in c:
        list.append(row)
    
    
    conn.close()
    return list

#Render the template
#Create Framework
    #Encapsulate CSS in external files
def print_html():
    env = Environment(loader = FileSystemLoader('.'))
    temp = env.get_template('SVG.html')
    allFields = coordinatesHtml()

    #HTML Framkework
    print('''Content-Type: text/html\n\n\
<!DOCTYPE html>\n\
<head>\n\
<title>SVG Mapping</title>\n\
<style type="text/css" media="screen">\n
body { background:#eee; margin:0 }\n
svg {\n
display:block; border:1px solid #ccc; position:absolute;\n
top:5%; left:5%; width:90%; height:90%; background:#fff;\n
} .face { stroke:#000; stroke-width:20px; stroke-linecap:round }\n''')
    
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

    for row in range(len(allFields)):
        print('''#r'''+str(row)+''' {
fill: #'''+str(colorramp[row])+''';\nstroke-width: 3;\nfill-opacity: 0.5;}\n''')
           

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

    '''Coordinate Transformation'''

    X = []
    Y = []
    
    for row in range(len(allFields)):
    
        X.append(allFields[row][0])
        Y.append(allFields[row][1])
    
    
    maxcoord = []
    if max(X[::]) >= max(Y[::]):
        maxcoord = max(X)
    else:
        maxcoord = max(Y)

    '''Dynamic SVG Extent'''    

    print('''<svg width=100% height=100% >\n''')
    
    '''Grid Computing'''

    gridmaximum = 100
    i = 1
    while True:
    
#        ticks = str(int((i/len(allFields))*maximum))
        ticks = str(float((i/len(allFields))*gridmaximum)) 
        
        print('''<line x1='''+ticks+'''% y1=0 x2='''+ticks+'''% y2='''+str(gridmaximum)+'''% style="stroke:rgb(0,0,0);stroke-width:2" /> ''')
        print('''<line x1=0 y1='''+ticks+'''% x2='''+str(gridmaximum)+'''% y2='''+ticks+'''% style="stroke:rgb(0,0,0);stroke-width:2" /> ''')
        i = i + 1
        if i == len(allFields):
            ticks = str(int((i/len(allFields))*gridmaximum))
            print('''<line x1='''+ticks+'''% y1=0 x2='''+ticks+'''% y2='''+str(gridmaximum)+'''% style="stroke:rgb(0,0,0);stroke-width:4" /> ''')
            print('''<line x1=0 y1='''+ticks+'''% x2='''+str(gridmaximum)+'''% y2='''+ticks+'''% style="stroke:rgb(0,0,0);stroke-width:4" /> ''')
            break



    '''Rectangle Computing'''
    
#   Fitted to Screen Size + Centralized
#   Fill + transparency + hovering
#   Labelling + hovering [Owner + Crop + Extent]
#   OnClick [Popup of finds at coordinates]
   
    for row in range(len(X)):
        rectX = str((X[row]/maxcoord)*100)
        rectY = str((Y[row]/maxcoord)*100)
        
        #HTML Body
        print ('''<rect width='''+rectX+'''% height='''+rectY+'''% class="rectangle" \
id="r'''+str(row)+'''" />''')
       
        
    #HTML Framkework
    print("</svg>\n</body>\n</html>")

    print(temp.render())

#run
if __name__ == '__main__':
    print_html()
