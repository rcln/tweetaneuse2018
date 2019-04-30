<h2>REFERENCE</h2>
<p>"Modèles en Caractères pour la Détection de Polarité dans les Tweets"
Davide Buscaldi, Joseph Le Roux et Gaël Lejeune DEFT 2018</p>

<ul>
<li>scorer.py:</li>
<ul>
	<li>	compute results</li>
	<li>	Input: gold standard file, path_results</li>
</ul>

<li>char_motifs.py:</li>
<ul>
		<li> third run</li>
		<li>works with python2 only (core algorithm is Python2 for now)</li>
		<li>main option -d data_directory/ </li>
		<li>--> data_directory contains one subdir for each class</li>
 		<li>use the -h option to get help</li>
</ul>
<li>path_to_gold_standard.py:</li>
<ul>
		<li>create tsv-like Gold standard</li>
		<li>takes as input a data_directory</li>
</ul>
<li>DATA_DIRECTORY</li>
<ul>
	<li>Its structure provides the criterion for classification:
	<li>DATASET/SUBSETS/CLASSES/INSTANCES
	<li>SUBSETS are not mandatory
	<li>Please note that the name of the subsets do not matter
	<li>Below is the result of the 'tree' command on the DATASET "dummy_data":</li>
<ul>

<li>├── test -->a SUBSET divided in CLASSES</li>
<li>│   ├── class1 --> the directory name is the name of the CLASS</li>
<li>│   │   ├── 1 --> each text file is an INSTANCE to classify</li>
<li>│   │   ├── 2... </li>
<li>│   └── class2 -->the name of the second CLASS(there can be more than 2)</li>
<li>│       ├── 10 --> the name have to be different in the same SUBSET</li>
<li>│       ├── 6</li>
<li>│       ├── 7...</li>
<li>└── train --> another SUBSET</li>
<li>    ├── class1</li>
<li>    │   ├── 1</li>
<li>    │   ├── 10</li>
<li>    │   ├── 2</li>
<li>    │   ├── 3 ...</li>
<li>    └── class2</li>
<li>        ├── 11</li>
<li>        ├── 12</li>
<li>        ├── 13</li>
<li>        ├── 14</li>
<li>        └── 15</li>
</ul>
</ul>
