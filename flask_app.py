from flask import Flask, render_template, request
import toolbox

app = Flask(__name__)
app.config["DEBUG"] = True

stc = []
table = []
hd = []
bd = []
hdr = []

@app.route('/', methods=["GET"])
def index():
    try:
        if request.args["button"] == "Resolver":
            stc = request.args["entrada"]
            table = toolbox.truthtable(stc).table()

            d = toolbox.DNF(stc)
            c = toolbox.CNF(stc)

            hd = table[0] + ['POS', 'SOP']

            for i in range(len(table[1:])):
                empty = 1
                for j in c:
                    if j[0] == i:
                        table[i+1].append(j[1])
                        empty = 0

                if empty:
                    table[i+1].append("")
                
                empty = 1
                for j in d:
                    if j[0] == i:
                        table[i+1].append(j[1])
                        empty = 0                       

                if empty:
                    table[i+1].append("")

            

            bd = table[1:]
            km = toolbox.kmap(stc)
            kgrp = [sorted([(j[0]+1, j[1]+1) for j in i]) for i in km.groups]
            print(kgrp)


            return render_template("main_page.html", sentence=stc, head=hd, body=bd, dnf=d, cnf=c, km=km.map, kg=kgrp)

        elif request.args["button"] == "Aleatorio":
            hdr = toolbox.generate(4)
            return render_template("main_page.html", holder=hdr)

    except KeyError as e:
        return render_template("main_page.html")



if __name__ == '__main__':
    app.run()
