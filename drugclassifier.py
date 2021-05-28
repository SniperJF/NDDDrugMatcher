
from common import jfc
import tablegeneration as jft


#Function creates File with all drugname/interventions that appear in a given CTO set list. 
#Second parameter is name of file
def printAllInterventions(CTOs, fname):
    allInterventions = set()
    for entry in CTOs:
        allInterventions.add(entry.drugname)
    #Now write to a file
    sortedAllInterventions = sorted(allInterventions, key=None, reverse=False)
    f = open("output/" + fname + ".txt", "w")
    for entry in sortedAllInterventions:
        f.write(entry)
        f.write("\n")
    f.close()
    #At this point I can change function to return either a set: allInterventions or a sorted list: sortedAllInterventions
    #return allInterventions, sortedAllInterventions #Should the need arise to work with either of them

#functions to read in the input files containing what interventions belong to what class.
def readFileAsSet(fname):
    filecontents = set()
    f = open(fname, "r")
    for line in f:
        line = line.strip('\n')
        if line != '':
            filecontents.add(line.lower()) #Add everything lowercased (will be useful for string matching later)
    f.close()
    return filecontents

def writeToFileSorted(data, fname):
    sortedData = sorted(fname, key=None, reverse=False)
    f = open("output/" + fname + ".txt", "w")
    for entry in sortedData:
        f.write(entry)
        f.write("\n")
    f.close()    

def readClassifierFiles():
    drugClassifiers = [] #Will hold drugs, non-drugs, and biomarkers in that order
    drugClassifiers.append(readFileAsSet("input/classifiers/drugs.txt"))
    drugClassifiers.append(readFileAsSet("input/classifiers/biomarkers.txt"))
    drugClassifiers.append(readFileAsSet("input/classifiers/devices.txt"))
    drugClassifiers.append(readFileAsSet("input/classifiers/non-drugs.txt"))
    return drugClassifiers

def printClassifiedCTOs(CTOsList1, CTOsList2):
    if len(CTOsList1) != 4 or len(CTOsList2) != 4:
        print("Error: printClassifidCTOs: CTosLists not correct size") #Four Groups
        return
    printAllInterventions(CTOsList1[0]+CTOsList2[0], "classified-tables/drugs")
    printAllInterventions(CTOsList1[1]+CTOsList2[1], "classified-tables/biomarkers")
    printAllInterventions(CTOsList1[2]+CTOsList2[2], "classified-tables/devices")
    printAllInterventions(CTOsList1[3]+CTOsList2[3], "classified-tables/non-drugs")

def createFinalTables(CTOsListIT, CTOsListST):
    if len(CTOsListIT) != 4 or len(CTOsListST) != 4: #we want 4 groups
        print("Error: createFinalTables:  CTosLists not correct size")
        return    
    #Independent Trial Tables
    table1 = jft.generateTableFromCTOs(jft.Table1Title, CTOsListIT[0])
    table3 = jft.generateTableFromCTOs(jft.Table3Title, CTOsListIT[1])
    table5 = jft.generateTableFromCTOs(jft.Table5Title, CTOsListIT[2])
    table7 = jft.generateTableFromCTOs(jft.Table7Title, CTOsListIT[3])
    jft.createCSVfromTable(table1, "final-tables/NDDCrossTable1")
    jft.createCSVfromTable(table3, "final-tables/NDDCrossTable3")
    jft.createCSVfromTable(table5, "final-tables/NDDCrossTable5")
    jft.createCSVfromTable(table7, "final-tables/NDDCrossTable7")
    #Single Trial Tables (Same code as above but combined for less lines)
    jft.createCSVfromTable( jft.generateTableFromCTOs(jft.Table2Title, CTOsListST[0]) , "final-tables/NDDCrossTable2")
    jft.createCSVfromTable( jft.generateTableFromCTOs(jft.Table4Title, CTOsListST[1]) , "final-tables/NDDCrossTable4")
    jft.createCSVfromTable( jft.generateTableFromCTOs(jft.Table6Title, CTOsListST[2]) , "final-tables/NDDCrossTable6")
    jft.createCSVfromTable( jft.generateTableFromCTOs(jft.Table8Title, CTOsListST[3]) , "final-tables/NDDCrossTable8")

    #Create Hyperlinked Tables:
    for i in range(1,9):
        jft.createHyperLinkedCSV("output/final-tables/", "NDDCrossTable"+str(i))

#CTOsList[0]: drugs
#CTOsList[1]: biomarkers
#CTOsList[2]: devices
#CTOsList[3]: non-drugs

#Function classifies all CTOs into four groups and returns a list of four CTOs
def classifyCTOs(CTOs, drugClassifiers):
    unclassified = set() #List of drugs that we couldn't classify
    classifiedCTOs = []
    classifiedCTOs.append([])
    classifiedCTOs.append([])
    classifiedCTOs.append([])
    classifiedCTOs.append([])
    #Time to Classify!
    for entry in CTOs:
        drugName = entry.drugname.lower() #Match lowercase version so it string matches
        classified_success = False
        #Check Each Category to see if the intervention is in it

        #Can add here skipTreatmentList if we so choose to

        #First let's find exact matches.
        for i in range(len(drugClassifiers)):
            if drugName in drugClassifiers[i]:
                #We have matched to a class
                classifiedCTOs[i].append(entry) #add CTO to this class
                classified_success = True
                break #so we don't add same trial to 2 classes for now
        if not classified_success: #If we still haven't matched then let's try to search for partial match
            for i in range(len(drugClassifiers)): #check each class
                for intervention in drugClassifiers[i]: #check each intervention in that class
                    if intervention in drugName:
                        classifiedCTOs[i].append(entry) #we found a partial match so let's go with that
                        classified_success = True
                        break #so we stop checking for this drug
                if classified_success: #If we found a match in previous class
                    break #movie on to next CTO
        if not classified_success: #if we still haven't found a match...
            #let's just assume it's a non-drug, but also let's make a list of them for improving the system
            classifiedCTOs[3].append(entry)
            unclassified.add(entry.drugname) #Append the normal casing
    return classifiedCTOs, unclassified


#drugclassifier main function to separate intervention matched into groups like non-drug
#disease-modifying drug, biomarkers, devices etc... for both CTOs: 
# CTOsIT (Independent Trials) and CTOsST (Single Trials)
def runDrugClassifier(CTOsIT, CTOsST):

    #First let's save all interventions into a file and call it allinterventions
    printAllInterventions(CTOsIT+CTOsST, "classified-tables/all-interventions")

    #next, load all text files to use to separate items
    drugClassifiers = readClassifierFiles()
    
    #Do classification and return a list of 3 CTOs sets classified
    classifiedCTOsListIT,unclassified1 = classifyCTOs(CTOsIT, drugClassifiers)
    classifiedCTOsListST,unclassified2 = classifyCTOs(CTOsST, drugClassifiers)
    unclassified = unclassified1.union(unclassified2)

    #Create a list with all the unclassified so we can improve later
    if len(unclassified1) != 0:
        jfc.writeListToFileSorted(unclassified, "output/classified-tables/", "unclassified-interventions")

    #create output files to be used for verification
    printClassifiedCTOs(classifiedCTOsListIT, classifiedCTOsListST)

    #finally let's create our final tables as CSV
    createFinalTables(classifiedCTOsListIT, classifiedCTOsListST)

#END CODE

