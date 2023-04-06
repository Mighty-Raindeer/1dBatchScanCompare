# 1dBatchScanCompare
one dimensional scan gamma analysis for the purposes of annual profile comparisons. Export Onmi pro 6.X ASCII files for both reference and evaluation files to compare. There is no way to see if a beam is fff or not with ascii (to my knowledge) so you will have to split up by those measurements. Upload each and then run gamma, it will save a pdf with all gamma anaysis completed. there is an error bypass in the code so that it will just run through all the data sets without stopping. 

To do:
Clean up output so that it looks better (cpisper lines, better colors, maybe a logo)
add more info to title of page
find out about FFF - you will just have to save as a different ascii file. 
add pdf save to propt
add prompt to tell you if all tests were analyzed and why some weren't (the toughest task imo)


How to use: 

For use with Omnipro / MyQA Accept, an IBA dosimetry software. Export data as 6.x.x ASCII for the profiles you wish to analyze.

** Energies with and without flattening filter will not be seperated automatically, you will need to save them as seperate files**

Run the script, open reference dataset, open matching type measurement dataset, run gamma. 

A matplotlib figure will appear if successful, displaying beam parameters, gamma analysis and a histogram. You can change analysis parameters in the code (it will be added in the future to the GUI)

You do not need to save each figure seperately, simply close the figure and the scirpt will continue on to the next dataset. Once all are complete, close the GUI. The PDF file will be generated in the folder containing the script. Move it to another save location and name it accordingly. 