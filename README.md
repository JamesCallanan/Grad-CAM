Code for thesis and short [paper](https://jamescallanan.github.io/assets/ShortPaper.pdf), both entitled 'Integrating feature attribution methods into the loss function of deep learning classifiers'.

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


#Experiment 1/CCE loss.ipynb , #Experiment 1/Heatmap loss.ipynb, #Experiment 2/CCE loss.ipynb , #Experiment 2/Heatmap loss.ipynb
These were the notebooks run to train models for the respective experiments using the different loss functions. These notebooks had to be repetitively run. I believe the Colab notebooks where running into OOM errors with larger numbers of models trained. If replicating the experiment, you would not need to train so many models. 30 models was excessive as the effect size was so large. I recall n = 3 to 5 (3-5 models) being sufficient given the observed effect size, a high power and low alpha level (0.01). This would need to be verified though. I used pinguoin.power_ttest() to do this at the time.
