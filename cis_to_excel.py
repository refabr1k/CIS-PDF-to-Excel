import re
import sys
import json
import csv
import pandas as pd
import tika
tika.initVM()
from tika import parser


cispdf, outfile = "",""

if len(sys.argv) < 3:
	print("[!] Please provide input and output filename!")
	print("Usage: python {} <input.pdf> <output>\n".format(sys.argv[0]))
	print("Note: For <output>, no need to provide file extension.")
	exit()
else:
    cispdf = sys.argv[1]
    outfile = sys.argv[2]


# json file - converted CIS benchmark to json format with 
cisjson = "{}.json".format(outfile)
cisexcel = "{}.xlsx".format(outfile)

# excel file


# cis text output
cistext = 'cis_text.txt'

#---------------------------------------------------
print("[+] Converting '{}' to text...".format(cispdf))
# tika write get text from pdf
raw = parser.from_file(cispdf)
data = raw['content']

print("[+] creating temp text file...")
# write pdf to text
f = open(cistext,'w', encoding='utf-8')
f.write(data)

# Remove blank lines

with open(cistext, 'r', encoding='utf-8') as filer:
	with open('temp.txt', 'w', encoding='utf-8') as filew:
		for line in filer:
			if not line.strip():
				continue
			if line:
				# start writing
				filew.write(line)

#-------------------------------------------------------
				

flagStart, flagDesc, flagAudit, flagRecom, flagComplete = False, False, False, False, False
cis_title, cis_desc, cis_audit, cis_recom = "","","",""
listObj = []


print("[+] Converting to Json...")
with open("temp.txt", 'r', encoding='utf-8') as filer:
	for line in filer:
		if not line.strip():
			continue
		if line.strip():

			x = {} #json object
			if re.match(r"^[0-9]\.[0-9]", line):
				# flagStart = True		# identified CIS title			
				cis_title, cis_desc, cis_audit, cis_recom = line,"","",""
				flagStart, flagDesc, flagAudit, flagRecom, flagComplete = True, False, False, False, False
				# cis_title, cis_desc, cis_audit, cis_recom = "","","",""

			if flagStart:
				# Get description - capture everything between 'Description:' and 'Rationale:'
				if "Description:" in line:	
					flagDesc = True
					
				if flagDesc:
					if "Description:" in line:
						continue
					cis_desc = cis_desc + line

				if "Rationale:" in line:
					flagDesc = False

																
				# # Get Audit - capture everything between 'Audit:' and 'Remediation:'
				if "Audit:" in line:
					flagAudit = True

				if flagAudit:
					if ("Audit:" in line):
						continue
					cis_audit = cis_audit + line



				# # Get Remediation - capture everything between 'Remediation:'
				# and 'References:'
				# or sometimes 'Additional Information:'
				# or sometimes 'CIS Controls:'
				if "Remediation:" in line:
					flagAudit = False
					flagRecom = True

				if flagRecom:
					if "Remediation:" in line:
						continue
					cis_recom = cis_recom + line

				if ("References:" in line) or ("Additional Information:" in line) or ("CIS Controls:" in line):
					flagRecom = False
					flagComplete = True


				if flagComplete:
					cis_title = cis_title.replace('\n','')
					cis_desc = cis_desc.replace('\n','')
					cis_desc = cis_desc.replace('Rationale:','')
					cis_desc = cis_desc.replace('| P a g e','')
					cis_audit = cis_audit.replace('\n','')
					cis_audit = cis_audit.replace('Remediation:','')
					cis_audit = cis_audit.replace('| P a g e','')
					cis_recom = cis_recom.replace('\n','')
					cis_recom = cis_recom.replace('CIS Controls:','')
					cis_recom = cis_recom.replace('Additional Information:','')
					cis_recom = cis_recom.replace('References:','')
					cis_recom = cis_recom.replace('| P a g e','')

					x['title'] = cis_title
					x['description'] = cis_desc
					x['audit'] = cis_audit
					x['recommendations'] = cis_recom
					# print(x)
					cis_title, cis_desc, cis_audit, cis_recom = "","","",""
					flagStart = False
					# parsed = json.loads(x)
					# print(json.dumps(x, indent=4))
					listObj.append(x)

print("[+] Writing to '{}' ...".format(cisjson))
# print(listObj)
# print(len(listObj))

with open(cisjson, 'w') as json_file:
    json.dump(listObj, json_file, 
                        indent=4,  
                        separators=(',',': '))
print("[+] Creating '{}' ...".format(cisexcel))
df_json = pd.read_json(cisjson)
df_json.to_excel(cisexcel)
print("[+] Done!")

# print(d)			

#print(record[0])

# with open('test.csv', 'w') as ofile:
# 	for i in record:
# 		ofile.write("%s\n" % i)
# 	print("Done")