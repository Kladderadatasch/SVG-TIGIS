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
</head>\n<body>''')

    '''SVG Extent'''

    X = []
    Y = []
    
    for row in range(len(allFields)):
        
        X.append(allFields[row][0])
        Y.append(allFields[row][1])
    
        maximum = []
        if max(X[::]) >= max(Y[::]):
            maximum = max(X)
            maxExt = [i * 50 for i in X]
        else:
            maximum = max(Y)
            maxExt = [i * 50 for i in Y]
            
        #    CM in Pixel converting ?
        pixExt = str(maximum * 50)
        print('''<svg width='''+pixExt+''' height='''+pixExt+'''>\n''')
    
    
    # Grid Computing - Necessary to have the Coordinates as Integers
#    Values need to be converted to pixels
    
    i = min(maxExt)
    while True:

        ticks = str(i/maxExt[])
        print('''<line x1="0" y1="0" x2='''+ticks+'''y2='''+ticks+'''style="stroke:rgb(255,0,0);stroke-width:2" /> ''')
        i = i + 1
        if i == maximum:
            ticks = str(i/maxExt)
            print('''<line x1="0" y1="0" x2='''+ticks+'''y2='''+ticks+'''style="stroke:rgb(255,0,0);stroke-width:2" /> ''')
            break
        


# Rectangle Computing
    for row in range(len(X)):
        rectX = str(X[row])
        rectY = str(Y[row])

        #HTML Body
        print ('''<rect width='''+rectX+''' height='''+rectY+''' \
style="fill:none;stroke-width:3;stroke:rgb(0,0,0)" />''')

    #HTML Framkework
    print("</svg>\n</body>\n</html>")

    print(temp.render())

#run
if __name__ == '__main__':
    print_html()
