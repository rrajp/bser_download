from flask import Flask, render_template, send_file
import pandas as pd
import requests
import os

app = Flask(__name__)


@app.route('/bser/')
def front():
    return render_template("bser_template.html")


@app.route('/bser/<uid>/<start>/<end>')
def bser(uid, start, end):
    try:
        urllist = ["", "http://rajresults.nic.in/resbserx19.asp", "http://rajresults.nic.in/rajartsbser2019.asp",
                   "http://rajresults.nic.in/sciencebser19.asp", "http://rajresults.nic.in/commercebser19.asp",
                   "http://rajresults.nic.in/resbserx20.asp", "http://rajresults.nic.in/rajartsbser2020.asp",
                   "http://rajresults.nic.in/Science2020bser.aspx", "http://rajresults.nic.in/commercebser20.asp"]
        url = urllist[int(uid)]
        data = dict()
        d = {}
        # print("1")
        for number in range(int(start), int(end)):
            
            if int(uid)==7:
                payload = f"__VIEWSTATE=%2FwEPDwUJNTYyNjA1MzQ5ZGQBbFD3Bib8uKtFlUVNWkFLFiLZog8Z7GZFOxYiL9pAqg%3D%3D&__VIEWSTATEGENERATOR=8CEC9530&__EVENTVALIDATION=%2FwEdAATy50P743NFHbR3f01aGgVZWB%2Ft8XsfPbhKtaDxBSD9Ly%2B%2FyJEA4EQNtbaAJJ0rSlW%2FDdi58i%2FdsQ6aLnYJIUBmmxYXPqGJ1qSdfy3cGnODfjAXDvqJzw2znNJXTaGrWCk%3D&txtRollNo={number}&btnResult=Submit"
            else:
                payload = "roll_no=" + str(number) + "&B1=Submit"
                
            headers = {
                'Host': 'rajresults.nic.in',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': '25',
                'Origin': 'http://rajresults.nic.in',
                'Connection': 'keep-alive',
                'Referer': 'http://rajresults.nic.in/resbserx19.htm',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }

            response = requests.request("POST", url, headers = headers, data = payload)
            print(response.status_code)
            resp = pd.read_html(response.text.encode('utf8'))
            if "commerce" in url:
                resp[2].columns = resp[2].iloc[1, :].tolist()
            elif "science" in url:
                resp[2].columns = resp[2].iloc[1, :].tolist()
            elif "art" in url:
                resp[2].columns = resp[2].iloc[1, :].tolist()
            else:
                resp[2].columns = resp[2].iloc[0, :].tolist()

            resp[2] = resp[2][1:]
            resp[2].set_index(resp[2].columns[0], inplace = True)

            marks = resp[2].stack().to_frame().T

            for i in marks.columns:
                if i[0].startswith(('Total', 'Percentage', 'Result', 'Subject')):
                    try:
                        marks.drop(i[0], axis = 1, inplace = True)
                    except:
                        continue

            for ind in resp[2].index:
                if ind.startswith(('Total', 'Percentage', 'Result')):
                    marks[ind.split(':')[0], ind.split()[0]] = resp[2].loc[ind]['Total'].split(':')[-1]

            resp[1].set_index(0, inplace = True)

            info = resp[1].stack().to_frame().T
            info.reset_index(inplace = True)
            info.rename(columns = lambda x: ' ' + str(x), inplace = True)

            final = info.merge(marks, how = 'inner', right_index = True, left_index = True)
            d[number] = final
        output = pd.concat(d, axis = 0)
        output.drop(['index'], axis = 1, level = 0, inplace = True)

        def datatype(x):
            if type(x) == float:
                return x
            elif type(x) == int:
                return x
            elif x.isdigit():
                return int(x)
            else:
                return x

        output = output.applymap(datatype)
        output.fillna('-', inplace = True)
        output.set_index((' Roll Number', ' 1'), inplace = True)
        output.to_excel(os.path.join(os.getcwd(), 'result.xlsx'))
        return send_file(os.path.join(os.getcwd(), 'result.xlsx'), as_attachment = True)
        # return output
    except Exception as e:
        print(e.args[0])
        return None


if __name__ == '__main__':
    app.run()
