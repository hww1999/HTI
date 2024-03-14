# High Throughput Imaging 

The aim of this project is to assist in understanding the morphology for keratinocytes and fibroblasts (cells found within the skin) when treated with different 
types and doses of cytokines. 

![poster](https://github.com/hww1999/HTI/blob/main/Poster.pptx.png)

## Installation 

```bash
git clone git@github.com:hww1999/HTI.git
conda create --name image_analysis python=3.9.18
conda activate image_analysis
pip install -r requirements.txt
```

For more details on downloading and setting up conda environment you can visit [conda](https://docs.anaconda.com/free/miniconda/index.html)

## How to Run 

All the source code can be found here [src](https://github.com/hww1999/HTI/tree/main/Final/src)

<div align="center">

**Jupyter Notebooks** 


| Purpose | File |
|---------|------|
|Data Cleaning| [Cleaning](https://github.com/hww1999/HTI/blob/main/Final/Jupyter%20Notebooks/01.%20data_cleaning.ipynb)|
|Principal Component Analysis| [PCA](https://github.com/hww1999/HTI/blob/main/Final/Jupyter%20Notebooks/02.%20pca_1.ipynb)|
|Corr Filtering| [Filtering](https://github.com/hww1999/HTI/blob/main/Final/Jupyter%20Notebooks/03.%20corr_filtering.ipynb)|
|Visualisation| [Dashboard](https://github.com/hww1999/HTI/blob/main/Final/Dashboard/app.py)|

</div>

## Background

**The Role of Skin in Immune-Defense**: 
While often overlooked, the skin plays an important role in immune defense. It aids in protecting the individual from infection, UV radiation, and irritants. The skin also interacts with immune cells and contains about twice as many T-cells as blood cells (T-cells are “a type of white blood cell” that help to fight infection [1]). CD4 T-cells secrete cytokines, a type of chemical signal, to “coordinate inflammatory responses” in the skin and immune cells [2]. 

**The Goal**:
By studying the potential effects of cytokines on skin cells, researchers hope to derive insights that lead to advancements in the field of human immunology research. 

**The Process**:
Researchers at the Benaroya Research Institute (BRI) conducted a series of experiments to treat two skin cell types (keratinocytes and fibroblasts) with a variety of cytokines at different doses. Then, they used high-content imaging to stain various cell components such as the nucleus, cytoskeleton, mitochondria. These images are (A) segmented into several regions of interest and then (B) measured for morphological changes for each staining. By comparing the images for different treatments and cell regions, the researchers hope to identify insight into what impact cytokines have on the cells.

**The Problem**: 
A challenge when performing analyses on cell-imaging data stems from the sheer volume of the data. In the process described above, the researchers conducted 8 experiments. One of the experiments resulted in 408 images, where each image contained up to hundreds of cellular objects. For each cellular object, various measurements were recorded, resulting in 157 corresponding features for each object. Thus, the question is, how do you identify patterns in these measurements, given this scale?


## Pipeline

The solution pipeline developed for this project can be broken down into the following parts 

**Data Ingestion & Preprocessing**
1. Column Dropping
2. Data Imputation


**Outlier Detection**

For each feature, the data is grouped by the type of cytokine and the dosage before outlier detection is performed. The outliers are considered to be those points which are beyond a certain threshold of standard deviation. Once outlier points are determined for each feature, now it's checked that for how many features is a specific row an outlier. For example row 1 might be an outlier in 80% of the features and row 2 might be an outlier in 60% of the features. Assuming we keep a threshold of 70% we will drop row 1 but keep row 2. This helps in identifying the images which were not good and should not be considered in the future analysis. 

**Dimensionality Reduction**

The dimensionality reduction is done in two parts. In the first part principal component analysis is performed and a cumulative weight for a specific feature is calculated across all components. The features which have a cumulative weight below a certain threshold are dropped as they are making almost zero contribution in explaining the variance of the data. In the second part of dimensionality reduction correlation heatmaps are used to identify the set of features which are strongly correlated across all types of cytokine treatments. From these sets now only one feature is kept and rest are dropped (this part involves manual identification of those features from the main dashboard). 


**Statistical Tests**
1. To identify that difference in values does not occur because of differences in wells and plates, t-test is performed between wells with experiments of the same cytokine at the same dosage level and ANOVA AND TUKEY are performed between plates with untreated experiments. This provides confirmation that tests performed are valid or maybe can give guidelines for future improvements (The visualization for this part can be found in the dashboard)
2. To test that if a feature has a shared effect on a set of cytokines on a given plate and at a given dosage treatment. This is to provide initial insight as to if there are sets of cytokines that have a shared MOA for a given feature. (@Matthew Review w/team)*
3. To test that if, with a specific cytokine, different dosage levels are having a statistically significant effect on a specific feature, we have conducted the one way ANOVA test and tukey 

**Dashboard**

To build an open-source interactive dashboard, we decided to use open-source tools Dash, Plotly and Python to build the dashboard from scratch. With the upload module and a homepage, we managed to provide the users with a multi-page dashboard to display statistical analyses of experiments of interest. Trying to deliver the various statistical insights, we have following pages in which the users have the flexibility of choosing cytokines, dosages and the variable of interest:
1. Stats_Plate and Stats_Well to validate the independence between plates and wells used for experiments using graphs and tables of statistical experiment results
2. Stats_Dose and Stats_Cytokine to investigate and evaluate the impact of different proteins of different dosage levels on the cells using graphs and tables of statistical experiment results
3. Heatmap to show correlation between variables
4. Violin plots to show distributions of experiment outcomes
5. Dendrogram to show the clustering of parameters and to disclose underlying patterns


## Conclusion

We conducted a variety of statistical tests and learned:
1. For keratinocytes, we observed that untreated cells that were placed on three separate plates within the same experiment were significantly different for most features. This suggests that there may be an outside factor, such as contamination, that may be driving these differences.
2. For keratinocytes, we observed that cells treated with cytokine IL26 at 100 ng/mL had significantly different mean values for the granularity-related features compared to cells treated with the same cytokine at 11 ng/mL, implying that IL26 may be involved in strong immune responses to damages in keratinocytes’ granularity features.

We examined similarities between cytokine treatments and identified distinct clusters, which in the examined case, aligned with what investigators saw in the lab. Additionally, we identified the distinguishing features for a couple treatments (vs untreated)

## Future Work
1. Further investigate which cytokines share a similar mode of action with specific cell features via clustering methods
2. Perform analyses across experiments and compare results
3. Investigate whether cytokines impact different kinds of cells (e.g. fibroblasts vs keratinocytes) in measurably different ways
4. Explore methods for further reducing the number of features (e.g. self-organizing maps)

## Acknowledgements

We would like to thank Benaroya Research Institute for sponsoring our project, and would particularly express our gratitude to the following individuals:
- Dr. Caroline Stefani - BRI, Principal Investigator & Imaging Core Manager
- Dr. Hannah DeBerg - BRI, Bioinformatics Group Manager

Additionally, we are grateful for the guidance and support of our professor, Dr. Megan Hazen, throughout the capstone project.

## Reference
[1]. https://www.cancer.gov/publications/dictionaries/cancer-terms/def/t-cell

[2]. The sponsors provided details on cell biology and provided cell imagery throughout the poster

[3]. Caicedo, J., Cooper, S., Heigwer, F. et al. Data-analysis strategies for image-based cell profiling. Nat Methods 14, 849–863 (2017). https://doi.org/10.1038/nmeth.4397

[4]. Garcia-Fossa, F., Cruz, M. C., Haghighi, M., de Jesus, M. B., Singh, S., Carpenter, A. E., & Cimini, B. A. (2023). Interpreting image-based profiles using similarity clustering and single-cell visualization. Current Protocols, 3, e713. doi: 10.1002/cpz1.713


