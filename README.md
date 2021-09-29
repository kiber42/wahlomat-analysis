# wahlomat-analysis
Analysis of answers provided by political parties to the Wahl-O-Mat

`wahlomat_import_helper.py` simplifies importing the answers from the pdf summary sheet available from [Wahl-O-Mat](https://wahl-o-mat.de/) after a poll has been completed.  Several imported answers are provided as yaml files in this repository (see `data` directory).

`wahlomat_plot.py` creates two plots for each yaml file provided as a command line argument.  These plots show how the parties would rank each other based on a set of wahlomat answers.  One plot uses the numerical correlation (the parties' answers yes/neutral/no are mapped to the numerical values +1/0/-1, respectively), while the other plot uses the scoring system used by the wahlomat.  The parties are sorted to create clusters of high correlation.

The plots provide insights beyond the individual answers: parties with similar views can be easily identified.  This may help to form a first opinion of less well known parties.  Large clusters of parties with high correlation indicate that there are multiple parties that may be hard to distinguish and are possibly stealing votes from each other.  The selection of questions underlying this analysis creates an unknown bias, but certain patterns are stable over many elections.
