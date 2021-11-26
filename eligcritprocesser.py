#This file was born out of necessity. I need to run a lot of my existing code, but modified, to process these trials where
#the eligibility criteria contains a Neurodegenerative Disease (NDD) meaning the subjects of the trial may have that NDD.
#Because of this, these trials are of interest and I have created these csv files containing a list of NDD the trials 
#mentioned, the 3 files created contain either 
# 1) a single NDD detected that we then found was a new NDD in an existing trial with another NDD
# 2) multiple NDD detected that we then found at least one was new compared to existing NDD listed as condition in a trial
#    we were already tracking as of interest (since it had a NDD listed in conditions)
# 3) multple NDD detected in a trial that had no NDD listed as conditions. Truly a new trial discovered. This one needs us
#    to pull data from our raw files so we can get all the trial info.

# For all three of these I need to classify the interventions listed to generate new tables (or append to existing?)
# For now my big focus is to get the drug ones, but will expand to all intervention types. All that code I wrote/is done
# for the other NDD trials, I just have to adapt it so it works here without crashing :D
#TODO

#Imports
import tablegeneration as jft

#Parameters: These are 1,2,and3 from above comment. The fourth one is out matchedCTO objects useful for 1,2 checks.
#ec1matchedtrials: Stores NCTID, Trial Condition List, NDD listed in eligibility criteria text, and raw eligibility criteria text
#ec2matchedtrials: Stores NCTID, Trial Condition List, NDD listed in eligibility criteria text,
#                  New NDD appearing in Elig Crit Text, and raw eligibility criteria text
#ecnewtrials:      Stores NCTID, NDD listed in eligibility criteria text, and raw eligibility criteria text
#matchedCTOS:      Clinical Trial Objects. All NDD trials in a beautifully formatted way. Useful for 1 and 2 checks.
def eligibilitycritprocessor(ec1matchedtrials, ec2matchedtrials, ecnewtrials, matchedCTO): 
    #First let's build tableSTCTOs which we can use for 1 and 2. 
    tableSTCTOsEC1 = buildtableSTCTOs(ec1matchedtrials,ec2matchedtrials, matchedCTO)
    #tableSTFinal = jft.generateTableFromCTOsWithEC(jft.Table25Title, tableSTCTOsEC1)
    #jft.createCSVfromTable(tableSTFinal, "final-tables/NDDCrossTable25")

    #Next we just need to look at the intervention list and find our new additions of 1 and 2 #TODO
    #TODO 3 as well
    return tableSTCTOsEC1, [] #TODO second list

def buildtableSTCTOs(ec1matchedtrials, ec2matchedtrials, matchedCTO):
    matchedNCTIDset = set() #We need a list of NCTIDs of Trials of interest. Set so we remove dups
    for ctrial in ec1matchedtrials:
        matchedNCTIDset.add(ctrial[0]) #add NCTID, no duplicates allowed
    for ctrial in ec2matchedtrials:
        matchedNCTIDset.add(ctrial[0]) #add NCTID, no duplicates allowed 
    #Next we want to get the last posted date of all of these so we sort and store by that order.
    matchedNCTIDList = [] #Will hold all NCTID of Trials we want, And also stores the last updated date
    for ctrial in matchedNCTIDset:
        matchedNCTIDList.append([matchedCTO[ctrial].nctid,matchedCTO[ctrial].lastpostedDate])
 
    #Let's sort by post date so new stuff appears first (so descending order)
    matchedNCTIDList.sort(key = lambda row: row[1], reverse=True)

    #now that we have our list let's get our eligibility criteria version of Table 10 data basically.
    ectableSTCTOs = jft.generateCTOTableST(matchedNCTIDList, matchedCTO)
    return ectableSTCTOs