#!/usr/bin/env python3
import cx_Oracle
import cgitb
import folium
import cgi


cgitb.enable(format = 'text')
from jinja2 import Environment, FileSystemLoader

#HTML string
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
} .face { stroke:#000; stroke-width:20px; stroke-linecap:round }\n</style>\n
</head>\n<body>''')

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
    
    '''SVG Extent'''

    X = []
    Y = []
    
    for row in range(len(allFields)):
    
        X.append(allFields[row][0]*50)
        Y.append(allFields[row][1]*50)
    
        maximum = []
        if max(X[::]) >= max(Y[::]):
            maximum = max(X)
        else:
            maximum = max(Y)
    
    
            #    CM in Pixel converting ?
    pixExt = str(maximum)
    print('''<svg width='''+pixExt+''' height='''+pixExt+'''>\n''')
    

#    Grid Computing - Necessary to have the Coordinates as Integers
#    Static values so far, not fitted to screen size

    i = 1
    while True:
    
        ticks = str(int((i/len(allFields))*maximum))
        print('''<line x1='''+ticks+''' y1="0" x2='''+ticks+''' y2='''+str(maximum)+''' style="stroke:rgb(0,0,0);stroke-width:2" /> ''')
        print('''<line x1="0" y1='''+ticks+''' x2='''+str(maximum)+''' y2='''+ticks+''' style="stroke:rgb(0,0,0);stroke-width:2" /> ''')
        i = i + 1
        if i == len(allFields):
            ticks = str(int((i/len(allFields))*maximum))
            print('''<line x1='''+ticks+''' y1="0" x2='''+ticks+''' y2='''+str(maximum)+''' style="stroke:rgb(0,0,0);stroke-width:4" /> ''')
            print('''<line x1="0" y1='''+ticks+''' x2='''+str(maximum)+''' y2='''+ticks+''' style="stroke:rgb(0,0,0);stroke-width:4" /> ''')
            break



#   Rectangle Computing
#   Fitted to Screen Size + Centralized
#   Fill + transparency + hovering
#   Labelling + hovering [Owner + Crop + Extent]
#   OnClick [Popup of finds at coordinates]
    for row in range(len(X)):
        rectX = str(X[row])
        rectY = str(Y[row])

        #HTML Body
        print ('''<rect width='''+rectX+''' height='''+rectY+''' \
style="fill:none;stroke-width:3;stroke:rgb(255,0,0)" />''')

    #HTML Framkework
    print("</svg>\n</body>\n</html>")

    print(temp.render())

#run
if __name__ == '__main__':
    print_html()
