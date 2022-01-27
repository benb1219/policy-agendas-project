import os
import lxml.html as lh
import requests as rq
import csv
import time
import PyPDF2 as pypdf2
import re

# pdf = open("CommitteesCodebook_May112017.pdf", "rb")
# pdfReader = pypdf2.PdfFileReader(pdf)
# codebook = ""
# for n in range(pdfReader.numPages):
#     codebook += pdfReader.getPage(n).extractText().replace("\n", "")
# codebook = codebook.replace("VeteransÕ", "Veteran's")
# codebook = codebook.replace("VeteranÕs", "Veteran's")
# codebook = codebook.split("SENATE COMMITTEES")
# house_codebook = codebook[0][4172:]
# senate_codebook = codebook[1]
# print(house_codebook)
# print(senate_codebook)

house_codebook = ""
house_codebook += "Agriculture Committee 10200 "
house_codebook += "Appropriations Committee 10300 "
house_codebook += "Armed Services Committee National Security Committee Armed Services Committee 10400 "
house_codebook += "Banking and Financial Services Committee Banking, Finance, and Urban Affairs Committee Banking, Currency, and Housing Banking and Currency Financial Services 10500 "
house_codebook += "Budget Committee 10600 "
house_codebook += "Education and the Workforce Committee Economic and Educational Opportunities Education and Labor 10800 "
house_codebook += "Commerce Committee Energy and Commerce Interstate and Foreign Commerce Committee 10900 "
house_codebook += "International Relations Committee Foreign Affairs Committee International Relations Committee Foreign Affairs Committee 11000 "
house_codebook += "Government Reform and Oversight Committee Post Office and Civil Service Committee Oversight and Government Reform Government Reform Government Operations Committee Expenditures in the Executive Departments 11100 "
house_codebook += "House Administration Committee House Oversight Committee House Administration Committee 11200 "
house_codebook += "Resources Committee Natural Resources Interior and Insular Affairs Committee Public Lands 11400 "
house_codebook += "Judiciary Committee 11500 "
house_codebook += "Transportation and Infrastructure Committee 11800 "
house_codebook += "Rules Committee 11900 "
house_codebook += "Science Committee Science, Space, and Technology Science and Technology Science and Astronautics 12000 "
house_codebook += "Small Business Committee Select Committee on Small Business 12100 "
house_codebook += "Standards of Officials Conduct Select Committee on Standards and Conduct Ethics 12200 "
house_codebook += "Veteran's Affairs Committee 12300 "
house_codebook += "Ways and Means Committee 12400 "
house_codebook += "Homeland Security 13900 "
house_codebook += "Intelligence 15100 "


senate_codebook = ""
senate_codebook += "Agriculture, Nutrition, and Forestry Committee Agriculture and Forestry 20200 "
senate_codebook += "Appropriations 20300 "
senate_codebook += "Armed Services Committee 20400 "
senate_codebook += "Banking, Housing, and Urban Affairs Banking and Currency 20500 "
senate_codebook += "Budget Committee 20600 "
senate_codebook += "Commerce, Science, and Transportation Interstate and Foreign Commerce 20700 "
senate_codebook += "Energy and Natural Resources Interior and Insular Affairs Public Lands 20800 "
senate_codebook += "Environment and Public Works 20900 "
senate_codebook += "Finance Committee 21100 "
senate_codebook += "Foreign Relations Committee 21200 "
senate_codebook += "Governmental Affairs Committee Government Operations Expenditures in the Executive Departments Homeland Security and Governmental Affairs 21300 "
senate_codebook += "Judiciary Committee 21600 "
senate_codebook += "Health, Education, Labor, and Pensions Labor and Human Resources Committee Human Resources Labor and Public Welfare 21700 "
senate_codebook += "Rules and Administration Committee 21800 "
senate_codebook += "Small Business Committee 21900 "
senate_codebook += "Veteran's Affairs Committee 22000 "
senate_codebook += "Aging 25000 "
senate_codebook += "Ethics 25100 "
senate_codebook += "Indian Affairs 25200 "
senate_codebook += "Intelligence 25300 "



def find_nth(full, sub, n):
    start = full.find(sub)
    while(start >= 0 and n > 1):
        start = full.find(sub, start + len(sub))
        n -= 1
    return start




with open("reconcile_bbrown_OG.csv", newline = "") as og_file:
    with open("reconcile_bbrown.csv", "w", newline = "") as file:
        readr = csv.reader(og_file)
        writr = csv.writer(file)
        writr.writerow(next(readr))
        for r in readr:
            new_r = r
            url = r[-5]


            print("Working on " + r[1] + "...")

            new_r[14] = 0
            new_r[15] = 0
            new_r[16] = 0

            # author data
            u = rq.get(url, timeout = 75)
            doc = lh.fromstring(u.content)
            a_data = doc.xpath("//table//tr//td//a")[0].text_content()
            last = a_data.split(",")[0][5:]
            new_r[10] = last
            party = a_data.split("[")[1][0]
            if(party == "D"):
                new_r[9] = 1
            else:
                new_r[9] = 0

            # committee data
            u = rq.get(url + "/committees", timeout = 75)
            doc = lh.fromstring(u.content)
            for i in range(10):
                c_report = doc.xpath("//table//tr[" + str(i) + "]//td//a")
                if(len(c_report) > 0 and "Rept." in c_report[0].text_content()):
                    for item in c_report:
                        chmbr = item.text_content()[0:2]
                        rept = item.text_content()[9:]
                        if(chmbr == "H."):
                            new_r[7] = rept
                        elif(chmbr == "S."):
                            new_r[8] = rept
                    break

            # committee codes
            com = doc.xpath("//table//tr[2]//td")[0].text_content().split("|")
            for c_com in com:
                print(c_com)
                c_com = c_com.strip()
                chmbr_com = c_com.split("; ")

                for i in range(2):
                    if (c_com[0] == "S"):
                        codebook = senate_codebook
                    else:
                        codebook = house_codebook
                    dash_split = chmbr_com[i].split(" - ")
                    if(len(dash_split) > 1):
                        committee = dash_split[1]
                    else:
                        committee = dash_split[0]

                    #print(committee)


                    committee = committee.replace("Veterans'", "Veteran's")
                    committee = committee.replace("Oversight and Reform", "Oversight and Government Reform")

                    committee = committee.strip()

                    auto = False
                    code = " "

                    code_idx = codebook.find(committee)
                    if(code_idx != -1):
                        while(code_idx < len(codebook) and not re.match(r'\d+', codebook[code_idx])):
                            code_idx += 1
                        code_idx_end = code_idx + 1
                        while(code_idx_end < len(codebook) and codebook[code_idx_end] != " "):
                            code_idx_end += 1
                        code = codebook[code_idx:code_idx_end]


                    # if (committee == "Homeland Security"):
                    #     code = 13900
                    #     auto = True

                    # if(not auto):
                    #     z = 0
                    #     code_idx = codebook.find(committee)
                    #     n = 1
                    #     print("for: " + committee)
                    #     print(codebook[code_idx])
                    #     while(True):
                    #         if(z > 100):
                    #             code = "?"
                    #             break
                    #         #print("z: " + str(z))
                    #         z += 1
                    #         code_idx -= 1
                    #         #print(codebook[code_idx])
                    #         if(codebook[code_idx].isspace()):
                    #             continue
                    #         elif(codebook[code_idx] == ")" or codebook[code_idx] == ";" or codebook[code_idx] == "("):
                    #             break
                    #         else:
                    #             n += 1
                    #             code_idx = find_nth(codebook, committee, n)
                    #
                    #     if(code != "?"):
                    #         while(codebook[code_idx:code_idx + 4] != "Full"):
                    #             code_idx += 1
                    #         idx = code_idx - 2
                    #         while(codebook[idx] != " "):
                    #             idx -= 1
                    #         code = codebook[idx:code_idx]

                    print( code )
                    print(c_com[0])
                    if (c_com[0] == "H"):
                        if(i == 0):
                            new_r[11] = code
                        else:
                            new_r[12] = code
                    else:
                        new_r[13] = code
                        break
                    if(len(chmbr_com) < 2):
                        break




            #print(com)
            #/html/body/div[1]/div/main/div[1]/div[3]/div[1]/table/tbody/tr[2]/td


            # action data
            u = rq.get(url + "/actions", timeout = 75)
            doc = lh.fromstring(u.content)
            num = 1
            again = False
            while(True):
                if(not again):
                    action = doc.xpath("//table//tr[" + str(num) + "]//td")
                else:
                    action = doc.xpath("//table//tbody//tr[" + str(num) + "]//td")

                if(len(action) < 2):
                    if(again):
                        break
                    num = 1
                    again = True
                    continue



                date = action[0].text_content()
                event = action[1].text_content()
                #print(date, event, num)
                if(event.split(" ")[0] == "Introduced"):
                    new_r[23] = date
                    new_r[3] = date.split("/")[2]
                elif(event.split(":")[0] == "Passed/agreed to in House"):
                    new_r[24] = date
                elif(event.split(":")[0] == "Passed/agreed to in Senate"):
                    new_r[25] = date
                elif(event.split(" ")[0] == "Signed"):
                    new_r[26] = date
                elif(event.split(" ")[0] == "Vetoed"):
                    new_r[15] = 1
                elif (event.split(":")[0] == "Conference committee actions"):
                    new_r[14] = 1

                num += 1

            writr.writerow(new_r)


