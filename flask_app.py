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
    print("-- Homepage --")
    return render_template("main_page.html")

@app.route('/random', methods=["GET"])
def aleatorio():
    hdr = toolbox.generate(4)
    print("-- Aleatorio --\n{}".format(hdr))
    return render_template("main_page.html", holder=hdr)


@app.route('/results', methods=["GET"])
def resultado():
    print("-- Resultado --\n")
    # stc = request.form.get("entrada")
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


    return render_template("results.html", sentence=stc, head=hd, body=bd, dnf=d, cnf=c, km=km.map, kg=kgrp)

if __name__ == '__main__':
    app.run()
