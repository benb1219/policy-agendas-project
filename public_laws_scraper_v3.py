import os
import lxml.html as lh
import requests as rq
import csv
import time
import PyPDF2 as pypdf2
import re

pdf = open("CommitteesCodebook_May112017.pdf", "rb")
pdfReader = pypdf2.PdfFileReader(pdf)
codebook = ""
for n in range(pdfReader.numPages):
    codebook += pdfReader.getPage(n).extractText().replace("\n", "")
codebook = codebook.replace("VeteransÕ", "Veteran's")
codebook = codebook.replace("VeteranÕs", "Veteran's")
codebook = codebook.split("SENATE COMMITTEES")
house_codebook = codebook[0][4166:]
senate_codebook = codebook[1][58:]
print(house_codebook)
print(senate_codebook)



def find_nth(full, sub, n):
    start = full.find(sub)
    while(start >= 0 and n > 1):
        start = full.find(sub, start + len(sub))
        n -= 1
    return start

def get_major_code_and_idx(c, codebook):
    committee = ""
    codebook = codebook.replace(",", "")
    if(codebook[1] == "1"):
        if(c == "Committee on House Administration"):
            committee = c[13:]
        else:
            committee = c[6:]
    else:
        committee = c[7:]
    code = " "
    z = 0
    committee = committee.replace("Veterans'", "Veteran's")
    committee = committee.replace("Oversight and Reform", "Oversight and Government Reform")
    committee = committee.replace(",", "")
    committee = committee.strip()
    if (codebook[1] == "1" and committee == "Homeland Security"):
        committee = "Select Committee on Homeland Security"

    code_idx = codebook.find(committee)
    n = 1

    while (True):
        if (z > 100 or code_idx == -1):
            return "?", "?"

        z += 1
        code_idx -= 1
        if (codebook[code_idx].isspace()):
            continue
        elif(codebook[code_idx] == ")"):
            if(re.match(r'[(]\d+', codebook[code_idx - 4:code_idx])):
                break
        elif(codebook[code_idx] == ";" or codebook[code_idx] == "("):
            back_look_idx = code_idx
            full_before = False
            while(True):
                if(codebook[back_look_idx - 4:back_look_idx] == "Full"):
                    full_before = True
                    break
                elif(re.match(r'[(]\d+[)]', codebook[back_look_idx - 4:back_look_idx + 1])):
                    break
                back_look_idx -= 1
            if(not full_before):
                break


        n += 1
        code_idx = find_nth(codebook, committee, n)

    if (code != "?"):
        while (codebook[code_idx:code_idx + 4] != "Full"):
            code_idx += 1

        idx = code_idx - 1
        while(codebook[idx].isspace()):
            idx -= 1
        while (not codebook[idx].isspace()):
            idx -= 1

        code = codebook[idx:code_idx]
    return code, idx

def get_subcommittee_code(sub_c, major_c, chmbr):
    subcommittee = sub_c[sub_c.find(" on "):][4:].replace(",", "")
    sub_c = sub_c.replace(",", "")
    cbook = ""
    if(chmbr == 0):
        cbook = house_codebook
    else:
        cbook = senate_codebook

    major_committee, major_idx = get_major_code_and_idx(major_c, cbook)
    if(major_committee == "?"):
        return "?"
    cbook = cbook[major_idx:].replace(",", "")
    sub_idx = cbook.find(subcommittee)
    n_idx = 2
    while(re.match(r'[a-zA-Z]', cbook[sub_idx + len(subcommittee) + 1].strip()) and sub_idx != -1):
        sub_idx = find_nth(cbook, subcommittee, n_idx)
        n_idx += 1
    if(sub_idx == -1):
        return "?"
    sub_idx -= 1
    while(cbook[sub_idx].isspace()):
        sub_idx -= 1
    if(re.match(r'\d{5}', cbook[sub_idx - 4:sub_idx + 1])):
        return cbook[sub_idx - 4:sub_idx + 1]

    while(True):
        if(cbook[sub_idx] == "("):
            break
        sub_idx -= 1

    while(not re.match(r'\d{5}', cbook[sub_idx - 4:sub_idx + 1])):
        if(cbook[sub_idx - 4:sub_idx] == "Full"):
            return "?"
        sub_idx -= 1
    return cbook[sub_idx - 4:sub_idx + 1]



with open("reconcile_bbrown_OG.csv", newline = "") as og_file:
    with open("reconcile_bbrown.csv", "w", newline = "") as file:
        readr = csv.reader(og_file)
        writr = csv.writer(file)
        writr.writerow(next(readr))

        skip = 0
        for r in readr:
            new_r = r
            url = r[-5]

            # if(skip < 215):
            #     skip += 1
            #     continue


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
            com = doc.xpath("//*[@id='committees_main']//table//tr//th")[4:]
            h_dict = dict()
            s_dict = dict()
            curr_com = ""
            only_senate_com = ""
            stop_senate = False
            last_house = ""
            for c_com_html in com:
                c_com = c_com_html.text_content()
                if("House" in c_com):
                    if(last_house != "" and last_house != curr_com):
                        continue
                    if("Subcommittee" not in c_com):
                        curr_com = c_com
                        h_dict[curr_com] = []
                        if(len(h_dict.keys()) == 2):
                            last_house = curr_com
                    else:
                        subcom_arr = h_dict.get(curr_com)
                        subcom_arr.append(c_com)
                        h_dict[curr_com] = subcom_arr

                elif("Senate" in c_com and not stop_senate):
                    if ("Subcommittee" not in c_com):
                        if(only_senate_com != ""):
                            stop_senate = True
                            continue
                        curr_com = c_com
                        only_senate_com = curr_com
                        s_dict[curr_com] = []
                    else:
                        subcom_arr = s_dict.get(curr_com)
                        subcom_arr.append(c_com)
                        s_dict[curr_com] = subcom_arr





            c_col = 11
            for major in h_dict.keys():
                if (c_col == 13):
                    break
                code, c_idx = get_major_code_and_idx(major, house_codebook)
                sub_c = h_dict.get(major)
                if(len(sub_c) == 0):
                    new_r[c_col] = code
                    c_col += 1
                else:
                    for sub in sub_c:
                        sub_code = get_subcommittee_code(sub, major, 0)
                        new_r[c_col] = sub_code
                        c_col += 1
                        if(c_col == 13):
                            break


            if(len(s_dict.keys()) > 0):
                s_major = list(s_dict.keys())[0]
                code, c_idx = get_major_code_and_idx(s_major, senate_codebook)
                sub_c = s_dict.get(s_major)
                if (len(sub_c) == 0):
                       new_r[13] = code
                else:
                       sub_code = get_subcommittee_code(sub_c[0], s_major, 1)
                       new_r[13] = sub_code




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


