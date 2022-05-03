Code for thesis and short MIDL paper submission, both entitled 'Integrating feature attribution methods into the loss function of deep learning classifiers'.

Unfortunately, many of these notebooks cannot be re-run without setting up a database that contains the same tables as mine does. The database containing data from my experiments is on my local machine. Thus, without ngrok set up, no one can query/insert into it.

I have not yet included the code used to perform the hyperparam searches and train the networks. I plan on doing so.

Below is a description of a selection of files in this repo:

# DataGenerator
Functions to generate datasets of synthetic cardiac MRIs can be found here.
The function 'make_mri_and_seg_mask()' can be followed to see how an individual cardiac MRI was produced.

# Tests_and_Plots.ipynb
This contains the implementation of the statistical tests for the thesis/paper. Some plots from the thesis are contained there too.

# Heatmap_images.ipynb
This shows how the HiResCAM heatmaps that are overlayed on the cardiac MRIs, were produced.

# db_funcs.py
Contains functions that were used to insert into or pull data from the DB on my local machine when running above code in Google Colab instances.
