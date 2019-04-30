<h2>REFERENCE</h2>
"Modèles en Caractères pour la Détection de Polarité dans les Tweets"
Davide Buscaldi, Joseph Le Roux et Gaël Lejeune

DEFT 2018

scorer.py:	compute results
		Input: gold standard file, path_results

char_motifs.py: third run
		works with python2 only (core algorithm is Python2)
		main option -d data_directory/
		--> data_directory contains one subdir for each class
 		use the -h option to get help
path_to_gold_standard.py: create tsv-like Gold standard
		takes as input a data_directory

DATA_DIRECTORY
	Its structure provides the criterion for classification:
	DATASET/SUBSETS/CLASSES/INSTANCES
	SUBSETS are not mandatory
	Please note that the name of the subsets do not matter
	Below is the result of the 'tree' comamnd on the DATASET "dummy_data":

├── test -->a SUBSET divided in CLASSES
│   ├── class1 --> the directory name is the name of the CLASS
│   │   ├── 1 --> each text file is an INSTANCE to classify
│   │   ├── 2... 
│   └── class2 -->the name of the second CLASS(there can be more than 2)
│       ├── 10 --> the name have to be different in the same SUBSET
│       ├── 6
│       ├── 7...
└── train --> another SUBSET
    ├── class1
    │   ├── 1
    │   ├── 10
    │   ├── 2
    │   ├── 3 ...
    └── class2
        ├── 11
        ├── 12
        ├── 13
        ├── 14
        └── 15
