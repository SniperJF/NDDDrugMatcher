#Pre processing the query files to only handle the NDD trials we want for speeding up matching and not dealing with large files
#Also sorts by NCTID resulting csvs (stores to output folder)
#Current Runtime: 1 minute 36 seconds. 

import csv
#import json #For JSON Export/Imports
from common import jfc


# Row Contents
# Row[0] studies.nct_id
# Row[1] studies.official_title
# Row[2] conditions.name
# Row[3] interventions.name
# Row[4] intervention_other_names.name
# Row[5] studies.last_update_posted_date
# Row[6] studies.phase
# Row[7] studies.acronym
# Row[8] studies.enrollment
# Row[9] outcomes.time_frame
# Row[10] studies.study_first_posted_date
# Row[11] studies.overall_status


matchentries = [] #store matches
nddoutcomes = [] #stores nctid, outcome title/desc of relevant entries that match matchentries
ndddesignoutcomes = [] #stores design outcomes nctid, measure, time frame, description (fills in missing stuff from normal outcomes)
with open("queries/chartsv4A.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    for row in csv_data:
        #Since we want time range 2010 to 2021 we are going to splice it from the string. Example 2018-06-23 we will take the
        #2018 which is first 4 characters , cast to number, then compare if that value is in our range! else continue
        if int(row[5][0:4]) < 2010 or int(row[5][0:4]) > 2021: #so 2009 or 2022 would not show up
            continue #Remove these two lines to disable dating limits

        toappend = False #becomes true when we find something with a matching NDD
        #Check diseases in disease section
        for disease in jfc.diseaseLongChecked: #check standard names
            if disease in row[2]:
                toappend = True
                break
        #Check acronyms
        if (toappend == False) and (row[2] in jfc.diseaseAcronymsChecked):
            toappend = True
        #Removed row[7] acronym check because it was useless and got all false positives
        #Check studies on healthy individuals that mention disease in the title of the trial.
        if (toappend == False) and ("Healthy Volunteers" in row[2]):
            for disease in jfc.diseaseinTitleChecked:
                if disease in row[1]:
                    toappend = True
        if toappend:
            matchentries.append(row)
#print(matchentries)
diseasechecked = []
for entry in matchentries:
    if not (entry[2] in diseasechecked):
        diseasechecked.append(entry[2])
diseasechecked.sort()
#Write all Disease Name Variations we matched to our NDD for verification purposes
jfc.writeListToFileSorted(diseasechecked, "output/", "ListofDiseaseNameMatched")

#next we sort the resulting list by NCTID
sorted_matchentries = sorted(matchentries, key=lambda row: row[0], reverse=False) #sort by nctid

#lets write to csv all matches for trials on these diseases to pass to the next file.
#This script should only have to run once too.
with open('output/nddtrials.csv', 'w', newline='') as csv_outfile:
    outfile = csv.writer(csv_outfile)
    outfile.writerows(sorted_matchentries)
    #outfile.writerows(matchentries)

#now let's add all of the outcome rows that match trials we care about that are in nddtrials.csv (since rest we don't care)

matchnctid = {"NCT00000000"} #to speed up search let's make a set with all NCTIDs we care about
for row in matchentries:
    if row[0] not in matchnctid:
        matchnctid.add(row[0])

with open("queries/chartsv4B.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    for row in csv_data:
        if row[0] in matchnctid: #compare NCTID of matchentry with the row in chartsv4B if match then this is from a trial we care about
                nddoutcomes.append(row) #if we found a match in nddtrials we insert and move on to next row in chartsv4B

#next we sort the resulting list by NCTID
sorted_nddoutcomes = sorted(nddoutcomes, key=lambda row: row[0], reverse=False) #sort by nctid

with open('output/nddoutcomes.csv', 'w', newline='') as csv_outfile:
    outfile = csv.writer(csv_outfile)
    outfile.writerows(sorted_nddoutcomes)

#let's do the same with design_outcomes (chartsv4C)
with open("queries/chartsv4C.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    for row in csv_data:
        if row[0] in matchnctid: #compare NCTID of matchentry with the row in chartsv4B if match then this is from a trial we care about
                ndddesignoutcomes.append(row) #if we found a match in nddtrials we insert and move on to next row in chartsv4B

#next we sort the resulting list by NCTID
sorted_ndddesignoutcomes = sorted(ndddesignoutcomes, key=lambda row: row[0], reverse=False) #sort by nctid

with open('output/ndddesignoutcomes.csv', 'w', newline='') as csv_outfile:
    outfile = csv.writer(csv_outfile)
    outfile.writerows(sorted_ndddesignoutcomes)

#END CODE