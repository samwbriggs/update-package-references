import glob
import os
from bs4 import BeautifulSoup

def getSolutionDirectoryFromUser():
    solutionDirectory = input("Copy and then paste the path where your solution resides: ")
    # If the input contains quotes (Windows automatically copies paths with quotes) remove them.
    return solutionDirectory.replace("\"", "")

def generatePackageReferences(workingDirectory):
    '''Builds <PackageReference> tags from existing <Reference> tags in a proj file within Visual Studio.'''

    # Find proj files within the working directory.
    projectFiles = []
    try:
        vbProjFiles = glob.glob(f"{workingDirectory}\**\*.vbproj", recursive=True)
        csProjFiles = glob.glob(f"{workingDirectory}\**\*.csproj", recursive=True)
        if vbProjFiles:
            projectFiles.extend(vbProjFiles)
        if csProjFiles:
            projectFiles.extend(csProjFiles)
    except Exception as e:
        print("An exception ocurred while retrieving proj files: ", e)

    print("The following files were found:\n")
    for filePath in projectFiles:
        print(filePath)

    correctFiles = input("\nAre these the correct proj files? Y/N: ")
    if not correctFiles.lower() in ["y", "yes"]:
        exit()

    writeFile = open("NewReferences.vbproj", "w")
    
    for filePath in projectFiles:
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                data = file.read()
        except Exception as e:
            print("An exception ocurred while attempting to read proj files: ", e)

        bsData = BeautifulSoup(data, "xml")
        modifiedPackageReferenceTags = []
        for referenceTag in bsData.find_all("Reference"):
            nugetReference = referenceTag.find_all(string=lambda text: text and "nuget" in text.lower())
            if nugetReference:
                packageAttributes = referenceTag.get('Include')
                packageAttributes = "Include=" + packageAttributes
                if referenceTag.SpecificVersion:
                    packageAttributes = packageAttributes + ", SpecificVersion=" + referenceTag.SpecificVersion.get_text()
                packageAttributes = packageAttributes.replace("=", "=\"")
                packageAttributes = packageAttributes.replace(",", "\"") + "\""
                
                modifiedPackageReferenceTag = f"<PackageReference {packageAttributes} />"
                modifiedPackageReferenceTags.append(modifiedPackageReferenceTag)

        writeFile.write(f"<!--{filePath}-->\n")
        for tag in modifiedPackageReferenceTags:
            writeFile.write(tag + "\n")
        writeFile.write("\n")

    writeFile.close()

workingDirectory = getSolutionDirectoryFromUser()
generatePackageReferences(workingDirectory)