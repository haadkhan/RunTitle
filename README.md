# RunTitle

##General Algorithm:

###File Selection:
Only the files which contain the phrase "THIS IN" are selected.
These are the files that contain are deeds of land than deeds of minearl rights.

### Name Extraction:
Alchemy api is used to find out the names in the document. 

### Dependence Relation:
Initially I tried dependency parsing but because it is an OCR file it is kind of hard to find the sentence bounday.(no 
clear stops). How I try to find dependence is looking at the distance between the name and the word grantor or grantee.

Flaws with this appraoch:
Now I am looking at first name. This technique is flawed because the document may contain a synonym for grantee, it may 
it may contain the word grantee earlier etc. It may contain grantees. 



