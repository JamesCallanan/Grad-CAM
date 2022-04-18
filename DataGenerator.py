import numpy as np
from enum import Enum
import tensorflow as tf
import skimage.draw
import random
from MRIDetails import disease_details, MRI_SEGMENT_COLOURS, SEG_MASK_KEYS, EXPERIMENT_MODE


def isMale(percentage_male):
  return random.random() < percentage_male


def getFatPercentage(experiment_mode, disease_class, is_male):

    if experiment_mode == EXPERIMENT_MODE.different_size_male_female.value:
        # Obesity is a causal factor of this disease
        if disease_class == 'DCM':
            if is_male:
                return np.random.normal(loc=28, scale=7.9)
            else:
                return np.random.normal(loc=38.4, scale=9.7) 

        # Obesity is not a causal factor of the others
        else:
            if is_male:
                return np.random.normal(loc=26, scale=7.9)
            else:
                return np.random.normal(loc=36.4, scale=9.7)
    
    # elif experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
    else:
        # Obesity is a causal factor of this disease
        if disease_class == 'DCM':
            return np.random.normal(loc=33, scale=9) 
        # Obesity is not a causal factor for the others
        else:
            return np.random.normal(loc=31, scale=9) 


def getHeartSizeParams(disease_class, size_multiplier):
  length_scale_factor = 25  
  length_scaler = length_scale_factor*size_multiplier

  #HCM
  if disease_class == 'HCM':
    if random.random() < 0.16:
      RV_radius = disease_details['HCM']['rare_RV_radius']
    else:
      RV_radius = disease_details['HCM']['common_RV_radius']
    RV_wall_thickness = disease_details[disease_class]['RV_wall_thickness']
    LV_wall_thickness = disease_details[disease_class]['LV_wall_thickness']
    LV_radius = disease_details[disease_class]['LV_radius']

  #RV
  elif disease_class == 'RV_fatty':
    RV_wall_thickness = disease_details['RV_fatty']['RV_wall_thickness']
    LV_wall_thickness = disease_details['RV_fatty']['LV_wall_thickness']
    LV_radius = disease_details['RV_fatty']['LV_radius']
    RV_radius = disease_details['RV_fatty']['RV_radius']
  
  #RV
  elif disease_class == 'RV_fatty_fibro':
    RV_wall_thickness = disease_details['RV_fatty_fibro']['RV_wall_thickness']
    LV_wall_thickness = disease_details['RV_fatty_fibro']['LV_wall_thickness']
    RV_radius = disease_details['RV_fatty_fibro']['RV_radius']
    if random.random() < 0.1:
      LV_radius = disease_details['RV_fatty_fibro']['rare_LV_radius']
    else:
      LV_radius = disease_details['RV_fatty_fibro']['common_LV_radius']

  #Others
  else:
    RV_wall_thickness = disease_details[disease_class]['RV_wall_thickness']
    RV_radius = disease_details[disease_class]['RV_radius']
    LV_wall_thickness = disease_details[disease_class]['LV_wall_thickness']
    LV_radius = disease_details[disease_class]['LV_radius']

  return RV_wall_thickness*length_scaler, RV_radius*length_scaler, LV_wall_thickness*length_scaler, LV_radius*length_scaler



def make_mri_and_seg_mask(experiment_mode, disease_class, mri_height = 105 , mri_width = 135):
    fatty_LV = False
    is_male = isMale(disease_details[disease_class]['percentage_male'])


    # Establish disease variant if disease_class == 'RV'
    if disease_class == 'RV':
        if random.random() < 0.1:
            fatty_LV = True
        if random.random() < 0.5:
            disease_class = 'RV_fatty'
        else:
            disease_class = 'RV_fatty_fibro'


    # Establish size multiplier
    if experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
        size_multiplier = 1
    # elif experiment_mode == EXPERIMENT_MODE.different_size_male_female.value:
    else:
        if is_male:
            size_multiplier = np.random.normal(loc=1.3, scale=0.15)
        else:
            size_multiplier = np.random.normal(loc=1, scale=0.15)

    # Heart measurements: disease and size dependant
    RV_wall_thickness, RV_radius, LV_wall_thickness, LV_radius = getHeartSizeParams(disease_class, size_multiplier)
  
    # Add minute intra-individual variability to measurements
    variability_percentage = 0.02   #Multiplying this by the value of interest will get the s.d.
    RV_wall_thickness   =   RV_wall_thickness   +   np.random.normal( loc = RV_wall_thickness,  scale = variability_percentage*RV_wall_thickness)
    RV_radius           =   RV_radius           +   np.random.normal( loc = RV_radius,          scale = variability_percentage*RV_radius        )
    LV_wall_thickness   =   LV_wall_thickness   +   np.random.normal( loc = LV_wall_thickness,  scale = variability_percentage*LV_wall_thickness)
    LV_radius           =   LV_radius           +   np.random.normal( loc = LV_radius,          scale = variability_percentage*LV_radius        )

    # More measurement variables
    LV_combined_radius = LV_radius + LV_wall_thickness
    RV_combined_radius = RV_radius + RV_wall_thickness
    heart_len = 2*(RV_combined_radius + LV_combined_radius)


    # Fat measurements: disease, size and sex dependant
    body_fat_percentage = getFatPercentage(experiment_mode, disease_class, is_male)
    body_fat = body_fat_percentage*size_multiplier

    # We are not using the actual recorded max values for variables below 
    # Using those, would make the inter-individual fat variability for the majority harder to distinguish.
    # We want a noticeable distribution of fat_len's
    # The varaible values below give a fat_len that is sometimes as larger or larger than the heart_len

    max_expected_body_fat = 80  #max from 5 mil 'DCM' simulations was 110. But this is extreme, some 1 mill simulations only had max of 100
    max_expected_heart_len = 70 #max from 0.8 mil 'RV' simulations was 57.6 '''
    fat_len = (body_fat/max_expected_body_fat)*max_expected_heart_len
    fat_depth = 4 #arbitrarily chosen - want it to appear significant

    # Get dimensions for the numpy array just small enough to contain the heart and fat
    # These arrays will have different sizes for different people (heart and fat size dependant)
    # But they ALL will be centred in a standard larger numpy array later
    if heart_len > fat_len:
        img_width = int(np.ceil(heart_len)) + 2 # +2 as we need some leeway, draw.disk was sometimes drawing outside array
        LV_centre_x = LV_combined_radius + 1    # adding leeway

    else:
        img_width = int(np.ceil(fat_len)) + 2
        LV_centre_x = LV_combined_radius + (fat_len - heart_len)/2 + 1

    
    # Establish fat offset - reason for differing fat_offsets is explained in 'Notes on EXPERIMENT_MODE = 2' in MRIDetails.py
    if experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
        fat_offset_from_LV_radius = 18
    # elif experiment_mode == EXPERIMENT_MODE.different_size_male_female.value:
    else:
        fat_offset_from_LV_radius = 10


    # Heart dimensions will depend on heart disease 
    # However, I am assuming that ...
    # heart_to_skin_distance should be proportional to a persons size only. We don't expect their other organs to be disproportionately large
    heart_to_skin_distance = fat_offset_from_LV_radius*size_multiplier

    # Other smaller np array dimension
    img_height = int(np.ceil(2*LV_combined_radius + heart_to_skin_distance)) 


    # Constructing smaller np array for MRI and seg mask
    image_shape = (img_height, img_width)
    cardiac_mri = np.zeros( image_shape , dtype=np.uint8)
    seg_mask = np.zeros( image_shape , dtype=np.uint8)


    # Finding locations of the different structures we're putting in the MRI
    fat_centre_x = np.floor(img_width/2)
    RV_centre_x = LV_centre_x + LV_combined_radius + RV_combined_radius - 1 #as sometimes there were gaps between ventricles due to rounding in draw.disk
    LV_centre_y = img_height - 1 - LV_combined_radius
    RV_centre_y = LV_centre_y


    # Filling in structures into 'MRIs' and 'segmentation masks'   

    # Don't want to 'draw' (fill) structures in with a constant value.
    # So we make arrays of different colours with some variance
    fat_image               =   np.random.normal( loc = MRI_SEGMENT_COLOURS.fat.value,              scale = 2 , size = image_shape)
    myocardium_image        =   np.random.normal( loc = MRI_SEGMENT_COLOURS.myocardium.value ,      scale = 2 , size = image_shape)
    ventricle_cavity_image  =   np.random.normal( loc = MRI_SEGMENT_COLOURS.ventricle_cavity.value, scale = 2 , size = image_shape)

    # Filling in LV myocardium (inner ventricle chamber will be overwritten later)
    xx,yy = skimage.draw.disk((np.round(LV_centre_y), np.round(LV_centre_x)), radius=LV_combined_radius)
    cardiac_mri[xx,yy] = myocardium_image[xx,yy]
    seg_mask[xx,yy] = SEG_MASK_KEYS.LV_myocardium.value
    
    # Filling in RV myocardium '''
    xx,yy = skimage.draw.disk((np.round(RV_centre_y), np.round(RV_centre_x)), radius=RV_combined_radius)
    cardiac_mri[xx,yy] = myocardium_image[xx,yy]
    seg_mask[xx,yy] = SEG_MASK_KEYS.RV_myocardium.value 
    
    # Overwriting the myocardiums if they should be diseased/fatty
    if disease_class == 'RV_fatty' or disease_class == 'RV_fatty_fibro':
        # Different patients have different levels of disease progression, hence different fat levels in myocardium
        RV_myocardium_fat_level = np.random.uniform(disease_details[disease_class]['RV_fat_percentage'][0], disease_details[disease_class]['RV_fat_percentage'][1]) 
        upper_fat_content = MRI_SEGMENT_COLOURS.myocardium.value + RV_myocardium_fat_level*(MRI_SEGMENT_COLOURS.fat.value - MRI_SEGMENT_COLOURS.myocardium.value)
        RV_myocardium_fat_image = np.random.uniform(low=MRI_SEGMENT_COLOURS.myocardium.value , high=upper_fat_content , size=image_shape )
        
        # Overwriting RV myocardium
        xx,yy = skimage.draw.disk((np.round(RV_centre_y), np.round(RV_centre_x)), radius=RV_combined_radius)
        cardiac_mri[xx,yy] = RV_myocardium_fat_image[xx,yy]
        
        if fatty_LV: # Only relevant to some individuals
            # Different patients have different levels of disease progression, hence different fat levels in myocardium
            LV_myocardium_fat_level = np.random.uniform(disease_details[disease_class]['LV_fat_percentage'][0], disease_details[disease_class]['LV_fat_percentage'][1]) 
            LV_upper_fat_content = MRI_SEGMENT_COLOURS.myocardium.value + LV_myocardium_fat_level*(MRI_SEGMENT_COLOURS.fat.value - MRI_SEGMENT_COLOURS.myocardium.value)
            LV_myocardium_fat_image = np.random.uniform(low=MRI_SEGMENT_COLOURS.myocardium.value , high=LV_upper_fat_content , size=image_shape )
            
            # Overwriting LV myocardium
            xx,yy = skimage.draw.disk((np.round(LV_centre_y), np.round(LV_centre_x)), radius=LV_combined_radius)
            cardiac_mri[xx,yy] = LV_myocardium_fat_image[xx,yy]  
    
    # Filling in LV cavity
    xx, yy = skimage.draw.disk((np.round(LV_centre_y), np.round(LV_centre_x)), radius=LV_radius)
    cardiac_mri[xx,yy] = ventricle_cavity_image[xx,yy]
    seg_mask[xx,yy] = SEG_MASK_KEYS.LV_cavity.value
    
    # Filling in RV cavity
    xx, yy = skimage.draw.disk((np.round(RV_centre_y), np.round(RV_centre_x)), radius=RV_radius)
    cardiac_mri[xx,yy] = ventricle_cavity_image[xx,yy]
    seg_mask[xx,yy] = SEG_MASK_KEYS.RV_cavity.value
    
    # Filling in subcutaneous fat
    xmin, xmax = 0 , fat_depth
    ymin ,ymax = int(np.round(fat_centre_x - fat_len/2)), int(np.round(fat_centre_x + fat_len/2))
    cardiac_mri[ xmin:xmax, ymin:ymax ] = fat_image[xmin:xmax,ymin:ymax]
    seg_mask[ xmin:xmax, ymin:ymax ] = SEG_MASK_KEYS.fat.value

    # Centering cardiac_mri and seg_mask in larger np arrays 

    # Creating larger arrays
    centred_mri = np.zeros( ( mri_height, mri_width ) , dtype=np.uint8)
    centred_seg_mask = np.zeros( ( mri_height, mri_width ) , dtype=np.uint8)

    mri_x_dim_length = cardiac_mri.shape[1]  #shape[1] = number of cols - columns are perpendicular to x axis
    mri_y_dim_length = cardiac_mri.shape[0]

    x_index = int(np.round(mri_width -1 - mri_x_dim_length)/2)
    y_index = int(np.round(mri_height -1 - mri_y_dim_length)/2)

    centred_mri[ y_index : y_index + mri_y_dim_length , x_index : x_index + mri_x_dim_length] = cardiac_mri
    centred_seg_mask[ y_index : y_index + mri_y_dim_length , x_index : x_index + mri_x_dim_length] = seg_mask

    # Add male identifier id performing experiment 2 - see explanation in 'Notes on EXPERIMENT_MODE = 2' in MRIDetails.py
    if experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
        male_identifier_box_width = 10
        centred_mri_no_sex_identifiers = centred_mri
        if is_male:
            centred_mri[ mri_height - male_identifier_box_width : mri_height - 1, mri_width - male_identifier_box_width : mri_width - 1] = MRI_SEGMENT_COLOURS.is_male.value
            centred_seg_mask[ mri_height - male_identifier_box_width : mri_height - 1, mri_width - male_identifier_box_width : mri_width - 1] = SEG_MASK_KEYS.is_male.value
        
        return centred_mri, centred_seg_mask, centred_mri_no_sex_identifiers
    
    if experiment_mode == EXPERIMENT_MODE.extreme_diffs.value:
        box_width = 20
        if disease_class == 'RV':
            centred_mri[ mri_height - box_width : mri_height - 1, mri_width - box_width : mri_width - 1] = MRI_SEGMENT_COLOURS.is_male.value
        if disease_class == 'NOR':
            centred_mri[ 0 : box_width, mri_width - box_width : mri_width - 1] = MRI_SEGMENT_COLOURS.is_male.value
        if disease_class == 'HCM':
            centred_mri[ mri_height - box_width : mri_height - 1, 0 : box_width] = MRI_SEGMENT_COLOURS.is_male.value
        if disease_class == 'DCM':
            centred_mri[ 0 : box_width, 0 : box_width] = MRI_SEGMENT_COLOURS.is_male.value
    
    return centred_mri, centred_seg_mask


def make_MRI_dataset(dataset_size, DISEASE_LABELS, experiment_mode):
    disease_classes = list(DISEASE_LABELS._member_map_.keys())
    mris_unprocessed, seg_masks, labels = list(), list(), list()
    
    if experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
        mris_no_sex_labels_unprocessed = list()
        
    for disease in disease_classes:
        label = DISEASE_LABELS[disease].value

        for i in range(int(dataset_size/len(disease_classes))):
            if experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
              mri, seg_mask, mris_no_sex_label = make_mri_and_seg_mask( experiment_mode = experiment_mode , disease_class = disease)
              mris_no_sex_labels_unprocessed.append(mris_no_sex_label)
            else:
              mri, seg_mask = make_mri_and_seg_mask( experiment_mode = experiment_mode , disease_class = disease)
 
            mris_unprocessed.append(mri)
            seg_masks.append(seg_mask)
            labels.append(label)

    mris_unprocessed = np.asarray(mris_unprocessed)
    mris_unprocessed = np.expand_dims(mris_unprocessed,-1)  # adding color channel
    mris_unprocessed = mris_unprocessed.repeat(3,-1)        # making 3 RGB channels
    mris_preprocessed = tf.keras.applications.mobilenet.preprocess_input(mris_unprocessed) #preprocessing for use with pre-trained VGG model
   
    seg_masks = np.asarray(seg_masks)
    # seg_masks = np.expand_dims(seg_masks,-1)
    labels = np.asarray(labels)
    
    if experiment_mode == EXPERIMENT_MODE.same_size_male_female.value:
        mris_no_sex_labels_unprocessed = np.asarray(mris_no_sex_labels_unprocessed)
        mris_no_sex_labels_unprocessed = np.expand_dims(mris_no_sex_labels_unprocessed,-1)  # adding color channel
        mris_no_sex_labels_unprocessed = mris_no_sex_labels_unprocessed.repeat(3,-1)        # making 3 RGB channels
        mris_no_sex_labels_preprocessed = tf.keras.applications.mobilenet.preprocess_input(mris_no_sex_labels_unprocessed) #preprocessing for use with pre-trained VGG model

        return {
          'mris_unprocessed' : mris_unprocessed, 
          'mris_preprocessed' : mris_preprocessed,           
          'mris_no_sex_labels_unprocessed' : mris_no_sex_labels_unprocessed, 
          'mris_no_sex_labels_preprocessed' : mris_no_sex_labels_preprocessed,  
          'seg_masks' : seg_masks, 
          'labels' : labels
        }
  
    else:
        return {
            'mris_unprocessed' : mris_unprocessed, 
            'mris_preprocessed' : mris_preprocessed, 
            'seg_masks' : seg_masks, 
            'labels' : labels
        }
