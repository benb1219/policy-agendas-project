import os
import numpy as np
import pandas as pd
import lxml.html as lh
import requests as rq
import time
#

path = os.environ["USERPROFILE"] + "/Desktop/fiscal_notes"
if not os.path.exists(path):
    os.mkdir(path)                                                                                                                             #create the fiscal_notes file on the user's desktop
os.chdir(path)

s = 78                                                                                                 #set the legislative session
while(s <= 87):
    session = str(s)
    for chmbr in ("H", "S"):
        if(chmbr == "H"):
            size = len(lh.fromstring(rq.get("https://capitol.texas.gov/Reports/Report.aspx?LegSess=" + session + "R&ID=housefiled", timeout = 75).content).xpath("//table")) #ascertain the total number of bills
        else:
            size = len(lh.fromstring(rq.get("https://capitol.texas.gov/Reports/Report.aspx?LegSess=" + session + "R&ID=senatefiled", timeout = 75).content).xpath("//table"))
        for num in range(size):
            while(True):
                 try:
                    n = str(num)
                    url = "https://capitol.texas.gov/BillLookup/Text.aspx?LegSess=" + session + "R&Bill=" + chmbr + "B" + n                                                    #get its URL
                    u = rq.get(url, timeout = 75)
                    doc = lh.fromstring(u.content)
                    tb = ""
                    note_num = 1
                    while (True):
                        tb = doc.xpath('//div[@id="content"][2]//table[1]//tr//td[3]/a[' + str(note_num) + ']/@href')
                        if (len(tb) == 0):
                            break
                        if (".htm" not in tb[0]):
                            note_num += 1
                        else:
                            break
                    #tb = doc.xpath('//div[@id="content"][2]//table[1]//tr//td[3]/a[1]/@href')                                                                      #find the URL for each (existing) fiscal report
                    path = os.environ["USERPROFILE"] + "/Desktop/fiscal_notes/" + session + "_" + chmbr
                    if not os.path.exists(path):
                        os.mkdir(path)                                                                                                                             #create the fiscal_notes file on the user's desktop
                    os.chdir(path)

                    for t in tb:                                                                                                                                   #for each existing fiscal report...
                        print(t)
                        last = t[-5]
                        f = rq.get("https://capitol.texas.gov/" + t, timeout = 75)
                        fn = lh.fromstring(f.content)
                        fn_text = ""
                        try:
                            fn_text = fn.xpath("//pre")[0].text_content()
                        except:
                            fn_text = fn.xpath("//body")[0].text_content().encode('ascii', 'ignore').decode('ascii')

                        if last == "I":                                                                                                                            #use the URL to determine which stage the bill is in (introduced, committee, etc)
                            file = open(chmbr + "B" + n + "_Introduced.txt", "w")                                                                                  #write the fiscal report to a file and name it accordingly
                            file.write(fn_text)
                            file.close
                        elif last == "H":
                            file = open(chmbr + "B" + n + "_HouseCommitteeReport.txt", "w")
                            file.write(fn_text)
                            file.close
                        elif last == "E":
                            file = open(chmbr + "B" + n + "_Engrossed.txt", "w")
                            file.write(fn_text)
                            file.close
                        elif last == "S":
                            file = open(chmbr + "B" + n + "_SenateCommitteeReport.txt", "w")
                            file.write(fn_text)
                            file.close
                        elif last == "F":
                            file = open(chmbr + "B" + n + "_Enrolled.txt", "w")
                            file.write(fn_text)
                            file.close
                 except:
                    time.sleep(20)
                    continue
                 break

    s += 1