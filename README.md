Code for thesis and short [paper](https://jamescallanan.github.io/assets/ShortPaper.pdf), both entitled 'Integrating feature attribution methods into the loss function of deep learning classifiers'.

Unfortunately, many of these notebooks cannot be re-run without setting up a database that contains the same tables as mine does. The database containing data from my experiments is on my local machine. Thus, without ngrok set up, no one can query/insert into it.

I have not yet included the code used to perform the hyperparam searches and train the networks. I plan on doing so.

Below is a description of a selection of files in this repo:

# DataGenerator

Functions to generate datasets of synthetic cardiac MRIs can be found here.
The function 'make_mri_and_seg_mask()' can be followed to see how an individual cardiac MRI was produced.

# db_funcs.py

Contains functions that were used to insert into or pull data from the DB on my local machine when running above code in Google Colab instances.

# Heatmaps.py

The function make_gradcam_heatmap() returns both a GradCAM and HiResCAM heatmap. Inspiration for implementation came from https://keras.io/examples/vision/grad_cam/

# SQL_CMDs_to_create_tables.txt

Contains the SQL commands used to create the tables used to store results in this experiment. If these commands are used, you should be able to to use scripts in 'Experiment 1' and 'Experiment 2' folders to replicate the experiment.

If you just want to see the data from this experiment, you can check the csv files in the Results directory.

# Results/Heatmap_images.ipynb

This shows how the HiResCAM heatmaps that are overlayed on the cardiac MRIs, were produced.

# Results/Tests_and_Plots.ipynb

This contains the implementation of the statistical tests for the thesis/paper. Some plots from the thesis are contained there too.

# Results/search.csv and Results/trials_new.csv

Contains data collected after performing experiments and computing performance metrics. This could be loaded into a local Postgres database. You could expose this database using ngrok if running 'Results/Tests_and_Plots.ipynb' on Google Colab as opposed to locally.
