from enum import Enum

# Notes on EXPERIMENT_MODE = 2
# In this mode, the following are independant of sex;
#   -   Body fat percentage
#   -   Size multiplier (heart size, body fat...)
#
# What is new:
#   -   A box in the lower right corner if sex == Male
#   -   Fat is pushed further away from heart to make it easier to detect focus on it using
#       Grad-CAM
# 
# What is not changed:
#   -   Body fat dependance on DCM.
# 
# What is the point?
#   -   Make it easier to tell via Grad-CAM if sex is influencing the algorithm's predictions
#       sex correlates with certain diseases, but there is causal differences in the images 
#       that we would like the algorithm to pick up on instead

class EXPERIMENT_MODE(Enum):
    same_size_male_female = 0
    different_size_male_female = 1
    extreme_diffs = 2

class MRI_SEGMENT_COLOURS(Enum):
    fat = 0.9*255
    ventricle_cavity = 0.8*255
    myocardium = 0.2*255
    is_male = 1*255

# Chosen so they don't overlap with class labels 0,1,2,3
class SEG_MASK_KEYS(Enum):
    LV_cavity = 11
    RV_cavity = 12
    LV_myocardium = 13
    RV_myocardium = 14
    fat = 15
    is_male = 16

NOR_heart_ratios = {
    'RV_radius' : 2.5/17,
    'RV_wall_thickness' : 1/17,
    'LV_radius' : 3.5/17,
    'LV_wall_thickness' : 1.5/17
}

disease_details = {
    'NOR':{
        'RV_wall_thickness' : NOR_heart_ratios['RV_wall_thickness'],
        'RV_radius' : NOR_heart_ratios['RV_radius'],
        'LV_wall_thickness' : NOR_heart_ratios['LV_wall_thickness'],
        'LV_radius' : NOR_heart_ratios['LV_radius'],
        'percentage_male': 0.5
    },
    'DCM':{
        'RV_wall_thickness' : 0.9*NOR_heart_ratios['RV_wall_thickness'],
        'RV_radius' : 1.2*NOR_heart_ratios['RV_radius'],
        'LV_wall_thickness' : 0.8*NOR_heart_ratios['LV_wall_thickness'],
        'LV_radius' : 1.8*NOR_heart_ratios['LV_radius'],
        'percentage_male': 0.5
    },
    'HCM':{
        'RV_wall_thickness' : 1*NOR_heart_ratios['RV_wall_thickness'],
        'common_RV_radius' : NOR_heart_ratios['RV_radius'],# 84% of cases 
        'rare_RV_radius' : 1.2*NOR_heart_ratios['RV_radius'],#16% of cases
        'LV_wall_thickness' : 2.2*NOR_heart_ratios['LV_wall_thickness'],
        'LV_radius' : 0.4*NOR_heart_ratios['LV_radius'],
        'percentage_male': 0.6
    },
    'RV_fatty':{
        'RV_wall_thickness' : 1*NOR_heart_ratios['RV_wall_thickness'],
        'RV_radius' : 1.5*NOR_heart_ratios['RV_radius'],
        'LV_wall_thickness' : 1*NOR_heart_ratios['LV_wall_thickness'],
        'LV_radius' : 1*NOR_heart_ratios['LV_radius'],
        'RV_fat_percentage': [0.7,0.9],
        'LV_fat_percentage': [0,0.4] # 10% of cases 

    },
    'RV_fatty_fibro':{
        'RV_wall_thickness' : NOR_heart_ratios['RV_wall_thickness'],
        'RV_radius' : 1.5*NOR_heart_ratios['RV_radius'],
        'LV_wall_thickness' : 0.9*NOR_heart_ratios['LV_wall_thickness'],
        'common_LV_radius' : 1*NOR_heart_ratios['LV_radius'], #90% of cases
        'rare_LV_radius' : 1.2*NOR_heart_ratios['LV_radius'], #10% of cases
        'RV_fat_percentage': [0.3,0.8],
        'LV_fat_percentage': [0,0.4] # 10% of cases 

    },
    'RV' : { 
        'percentage_male': 2.7/3.7
    }
}

class DISEASE_LABELS(Enum):
  NOR = [1,0,0,0]
  HCM = [0,1,0,0]
  DCM = [0,0,1,0]
  RV = [0,0,0,1]
    
 def get_segment_seg_maps(seg_mask):
    lv_cavity = seg_mask == SEG_MASK_KEYS.LV_cavity.value
    rv_cavity = seg_mask == SEG_MASK_KEYS.RV_cavity.value
    lv_myo    = seg_mask == SEG_MASK_KEYS.LV_myocardium.value
    rv_myo    = seg_mask == SEG_MASK_KEYS.RV_myocardium.value
    fat       = seg_mask == SEG_MASK_KEYS.fat.value
    is_male   = seg_mask == SEG_MASK_KEYS.is_male.value

    lv = np.logical_or(lv_cavity, lv_myo)
    rv = np.logical_or(rv_cavity, rv_myo)

    heart = np.logical_or(lv,rv)

    segment_seg_masks = {
        'heart' : heart,
        'not_heart' : np.logical_not(heart),
        'lv' : lv,
        'rv' : rv,
        'is_male' : is_male,
        'fat' : fat,
        'lv_cavity' : lv_cavity,
        'rv_cavity' : rv_cavity,
        'lv_myo' : lv_myo,
        'rv_myo ' : rv_myo 
    }
    return segment_seg_masks
