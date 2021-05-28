from common import jfc
import tablegeneration as jft
import drugclassifier as jfd

import csv

#This will take the nddtrials.csv and process from there (to speed it up)

matchentries = []       #chartsv4A study and other main components
nddoutcomes = []        #chartsv4B outcomes
ndddesignoutcomes = []  #chartsv4C design outcomes

finalentries = []

#Cleanup Output Directory
#jfc.cleanOutputFiles() #Comment out for speed boost

#Read in data
with open("output/nddtrials.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    for row in csv_data:
        matchentries.append(row)

with open("output/nddoutcomes.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    for row in csv_data:
        nddoutcomes.append(row)

with open("output/ndddesignoutcomes.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    for row in csv_data:
        ndddesignoutcomes.append(row)

# Row Contents of output/nddtrials.csv
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

# Row Contents of queries/chartsv4B.csv
# Row[0] outcomes.nct_id 
# Row[1] outcomes.title
# Row[2] outcomes.description

# Row Contents of queries/chartsv4C.csv
# Row[0] design_outcomes.nct_id 
# Row[1] design_outcomes.measure
# Row[2] design_outcomes.time_frame
# Row[3] design_outcomes.description

#GOAL: 
#Drug Matched
#NCT_ID
#PHASE
#Diagnosis
#Number of Participants
#Primary Outcome(s)
#Biomarker Outcome(s)
#Year Registered (first posted date)
#Status (with date of last status, use last posted date)

#NEW CODE FOR THE APP (TO MAKE JSON AND KEEP THIS AS OOP
#newest cross ndd tables 4-19-21 on 5-14-21
#Object Oriented Programming Time. Let's make our clinicalTrial objects using diseaseentrylist.csv
matchedCTO = {} #Matched Clinical Trial Object :D
TablesCTO  = [] #Stores All Table contents as Clinical Trial Objects along with matched drug strings (basically the same info as final tables)

currNCTID = "NCT00000000"
for row in matchentries:
    if currNCTID != row[0]: #new NCTID
        matchedCTO[row[0]] = jfc.clinicalTrial(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]) #new trial entry
        currNCTID = row[0]
    else: #still inserting to current NCTID a new condition or intervention so handle it.
        #Try adding condition, intervention, or intervention_other_names
        matchedCTO[row[0]].addCondition(row[2])
        matchedCTO[row[0]].addInterventions(row[3],0)
        matchedCTO[row[0]].addInterventions(row[4],1)
#print('\n'.join(str(matchedCTO[x]) for x in matchedCTO)) #Debug to Print the entire dictionary

#Next let's go ahead and add the outcomes
for row in nddoutcomes:
    matchedCTO[row[0]].addOutcome(row[1],row[2])

#Next let's go ahead and add the design_outcomes (to see if we can fill more info for empty spots)
for row in ndddesignoutcomes:
    matchedCTO[row[0]].addDesignOutcomes(row[1],row[2],row[3])

#Test to see if this worked
#print(matchedCTO["NCT00620191"]) #For Testing the match from the table
#print(matchedCTO["NCT00620191"].generateTableRow())
#print(matchedCTO["NCT04220021"]) #For Testing the match from the table
#print(matchedCTO["NCT04220021"].generateTableRow())

jft.makeJSONmatchedCTO(matchedCTO) #Not used currently but left on since may be useful to have this



#TIME TO MAKE TABLES

#Let's start with Table 2 of Cross NDD
#    Table 10.  All interventions in single trials that included more than 1 neurodegenerative disorder.
# This one is ez
#we will just run through our object dictionary and find ones with length > 1 of the conditions array. Also good to test
#all our system


multiConditionNCTIDList = [] #Will hold all NCTID of Trials that have more than 1 condition listed, Am also going to store the last updated date
#So I can then sort the trials by newest. This will make it look nice.
#multiConditionNCTIDList.append(['NCT00000000', '2000-01-15']) #Test
#print(matchedCTO["NCT03658135"]) #For Testing the match from the table
#print(matchedCTO["NCT03658135"].generateTableRow())
#print(matchedCTO["NCT03658135"].getInterventionDrugsStr())
#multiConditionNCTIDList.append(['NCT03658135', '2019-12-19']) #Test

##TABLE 10 MAIN CODE
for ctrial in matchedCTO:
    if (len(matchedCTO[ctrial].condition) > 1 and 
            matchedCTO[ctrial].condition[0] != "Healthy Volunteers" and 
            matchedCTO[ctrial].condition[1] != "Healthy Volunteers"): #Avoid detecting this false positive
        #Found something to add. Save the NCTID and last posted date
        if len(matchedCTO[ctrial].intervention) > 0 or len(matchedCTO[ctrial].otherIntervention) > 0: #don't add trials without drugs.
            multiConditionNCTIDList.append([matchedCTO[ctrial].nctid,matchedCTO[ctrial].lastpostedDate])
            #may be able to remove this if statement if we re-do our SQL query and remove non-interventional trials?

#Let's sort by post date so new stuff appears first (so descending order)
multiConditionNCTIDList.sort(key = lambda row: row[1], reverse=True)

#Create our final version of Table 10
table10CTOs = jft.generateCTOTable10(multiConditionNCTIDList, matchedCTO)
table10Final = jft.generateTableFromCTOs(jft.Table10Title, table10CTOs)

#Write the new csv
jft.createCSVfromTable(table10Final, "final-tables/NDDCrossTable10")
#with open('output/NDDCrossTable2.csv', 'w', newline='') as csv_outfile:
#    outfile = csv.writer(csv_outfile)    
#    outfile.writerows(table2Final)


#Create Hyperlinked version of NDDCrossTable10.csv
jft.createHyperLinkedCSV("output/final-tables/","NDDCrossTable10")


#TABLE 9 MAIN CODE:
#In this one we are looking for drugs that appear in more than 1 trial. First phase let's find exact match entries
#Second phase later (with old code?) we can try to find partial matches by searching for individual words that match
iTMLP1 = [] #Independent Trial Match List Phase 1, Each entry holds:
# [  Matched Drugname, List of NCTID of Trials Matching (2 or more), Most recent last posted date of the set of trials  ]
# The last one is so that I can sort by newest drugs or also by newest entries the individual dates is for sorting within a drug entry set.
iTMLP2 = [] #Phase 2 of above.

iTMDP1 = {} #Dictionary that we are going to hash into for Phase 1. All we need to store is the key: drug and value: nctid
iTMDP2 = {} #Same for Phase 2. Stands for Independent Trial Match Dictonary Phase 2.

#So my plan for this is to for first pass to simply try hashing the objects using intervention and intervention_other_name as keys
#and then store for value a list of NCTID (so in case of collision we store them all). Store this in iTMDP1

#When done we look through at any key/value pair that has more than 1 trial stored. Then we check to see if there is at least 2 trials
#with different NDD. If so this is what we want so we add an entry into iTMLP1 so we can add it to our Table 1 results.

#Then for the second pass we can try the same hash approach but by using individual words as keys but before we do that we want to 
#look at the word and see if it's a stopword so we can skip those. Other than that we do the same process.

#Phase 1
for ctrial in matchedCTO:
    for drugname in matchedCTO[ctrial].intervention: 
        if jfc.drugnameCheckOK(drugname): #This is how we remove stopwords and other stuff we don't want like Placebo
            #Check if key exists already
            if drugname in iTMDP1: #Yes it exist, so append to existing list of NCTIDs
                iTMDP1[drugname].append(matchedCTO[ctrial].nctid)
            else: #New key so just add new entry
                iTMDP1[drugname] = [matchedCTO[ctrial].nctid] #It's a list of NCTIDs, so we just insert a list with 1 NCTID.
    for drugname in matchedCTO[ctrial].otherIntervention: #Do the same for intervention_other_names as above.
        if jfc.drugnameCheckOK(drugname): #This is how we remove stopwords and other stuff we don't want like Placebo
            if drugname in iTMDP1: 
                iTMDP1[drugname].append(matchedCTO[ctrial].nctid) #Same as above
            else:
                iTMDP1[drugname] = [matchedCTO[ctrial].nctid] #Same as above

#Next let's look at iTMDP1 and find multiple trial drugs and see if there is at least 2 with different NDD listed.
#Make sure we ignore the Healtyh Volunteers category.
for drugname in iTMDP1:
    alreadyAddedDrug = False
    if len(iTMDP1[drugname]) > 1: #We have a drug with multiple NCTIDs so let's see if they are different NDD
        try:
            firstTrialConditions = matchedCTO[iTMDP1[drugname][0]].condition
            for nctid in iTMDP1[drugname]:
                if alreadyAddedDrug:
                    break
                for cond in matchedCTO[nctid].condition:
                    if cond not in firstTrialConditions and cond != "Healthy Volunteers": #Don't count this as a different NDD
                        #we found a trial in the set that has a different NDD, add drug entry to iTMLP1
                        setNCTIDsWDate = []
                        for n in iTMDP1[drugname]:
                            setNCTIDsWDate.append([n,matchedCTO[n].lastpostedDate]) #make a list holding all nctid and last posted date
                        setNCTIDsWDate.sort(key=lambda col: col[1],reverse=True) #Sort Descending Order by Last Posted Date
                        newestLastPostedDate = setNCTIDsWDate[0][1]
                        #Find newest date to store that 
                        newentry = [drugname, [], newestLastPostedDate] #create entry
                        for i in setNCTIDsWDate:
                            newentry[1].append(i[0]) #Fill entry with only the nctids
                        iTMLP1.append(newentry) #append it

                        #Now that we added the set for this drugname let's move on to the next drugname by breaking to outermost loop
                        alreadyAddedDrug = True
                        break
        except:
            print("ERROR: Could not Find Cliical Trial in matchedCTO: ", nctid)
    #else: #Nothing to see here


#Let's sort by newest post date of each set so new stuff appears first (so descending order)
iTMLP1.sort(key = lambda col: col[2], reverse=True)

#Create our final version of Table 9
table9CTOs = jft.generateCTOTable9(iTMLP1, matchedCTO)
table9Final = jft.generateTableFromCTOs(jft.Table9Title, table9CTOs)

#Write the new csv
jft.createCSVfromTable(table9Final, "final-tables/NDDCrossTable9")

#Create Hyperlinked version of NDDCrossTable9.csv
jft.createHyperLinkedCSV("output/final-tables/", "NDDCrossTable9")

#Phase 2 Here. TODO  (Single word matches)

#Make JSONS of Table 1 and 2.  #These would be equivalent to table1Final once rendered as table
jft.makeJSONFromCTOsList(table9CTOs, 1)
jft.makeJSONFromCTOsList(table10CTOs, 2)

#Next we run drugclassifier to separate intervention matched into groups like non-drug, 
#disease-modifying drug, biomarkers, devices etc... for both CTOs 
jfd.runDrugClassifier(table9CTOs, table10CTOs) #9 is Independent Trials, 10 is single trials

#END OF PROGRAM. CREATED BY JORGE FONSECA AND SAM BLACK