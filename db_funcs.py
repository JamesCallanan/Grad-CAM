import psycopg2
from enum import Enum

class Model_Metrics(Enum):
  VAL_ACC = 'val_acc'
  VAL_LOSS = 'val_loss'
  TRAIN_ACC = 'train_acc'
  TRAIN_LOSS = 'train_loss'

class Order_By(Enum):
  ASC = 'asc'
  DESC = 'desc'

class Experiment_Number(Enum):
  EXP_1_NORMAL_LOSS = 11
  EXP_1_HEATMAP_LOSS = 12
  EXP_2_NORMAL_LOSS = 21
  EXP_2_HEATMAP_LOSS = 22
  EXP_2_NORMAL_LOSS_NO_LABELS = 23

def insert_search(search, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute(f"""INSERT INTO search 
                        ( search_id ,
                          experiment_number,
                          num_models,
                          num_epochs,
                          hyperparam_ranges,
                          git_commit_id,
                          data_path,
                          tensorboard_folder_path,
                          keras_tuner_folder_path,
                          search_duration_seconds
                        ) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT DO NOTHING
                        """, 
                        ( 
                          search['search_id'],
                          search['experiment_number'],
                          search['num_models'],
                          search['num_epochs'],
                          search['hyperparam_ranges'],
                          search['git_commit_id'],
                          search['data_path'],
                          search['tensorboard_folder_path'],
                          search['keras_tuner_folder_path'],
                          search['search_duration_seconds']
                        )                       
                       )
    conn.close()


def insert_trial(trial, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute(f"""INSERT INTO trials_new 
                          ( kt_trial_id,
                            search_id,
                            model_path,
                            val_loss,
                            val_acc,
                            train_loss,
                            train_acc,
                            learning_rate
                          )
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                          ON CONFLICT DO NOTHING
                        """,
                        (
                          trial['kt_trial_id'],
                          trial['search_id'],
                          trial['model_path'],
                          trial['val_loss'],
                          trial['val_acc'],
                          trial['train_loss'],
                          trial['train_acc'],
                          trial['learning_rate']
                        )
                      )
    conn.close()

def update_trial_with_test_metrics(trial_uid, performance_metrics, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        if 'val_loss' in performance_metrics: #We probably want to evaluate on train, val and test datasets e.g. for heatmaps loss experiments
          cursor.execute(""" UPDATE trials_new 
                              SET 
                                train_acc = %s,
                                train_loss = %s,
                                val_acc = %s,
                                val_loss = %s,
                                test_acc = %s,
                                test_gc_loss = %s,
                                test_cce_loss = %s,
                                avg_NOR_heart_in_mris = %s,
                                avg_NOR_fraction_of_gc_heatmap_in_heart = %s,
                                avg_NOR_fraction_of_hc_heatmap_in_heart = %s,
                                avg_NOR_fat_in_mris = %s,
                                avg_NOR_fraction_of_gc_heatmap_in_fat = %s,
                                avg_NOR_fraction_of_hc_heatmap_in_fat = %s,
                                avg_NOR_male_label_in_mris = %s,
                                avg_NOR_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_NOR_fraction_of_hc_heatmap_in_male_labels = %s,
                                avg_RV_heart_in_mris = %s,
                                avg_RV_fraction_of_gc_heatmap_in_heart = %s,
                                avg_RV_fraction_of_hc_heatmap_in_heart = %s,
                                avg_RV_fat_in_mris = %s,
                                avg_RV_fraction_of_gc_heatmap_in_fat = %s,
                                avg_RV_fraction_of_hc_heatmap_in_fat = %s,
                                avg_RV_male_label_in_mris = %s,
                                avg_RV_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_RV_fraction_of_hc_heatmap_in_male_labels = %s,
                                avg_DCM_heart_in_mris = %s,
                                avg_DCM_fraction_of_gc_heatmap_in_heart = %s,
                                avg_DCM_fraction_of_hc_heatmap_in_heart = %s,
                                avg_DCM_fat_in_mris = %s,
                                avg_DCM_fraction_of_gc_heatmap_in_fat = %s,
                                avg_DCM_fraction_of_hc_heatmap_in_fat = %s,
                                avg_DCM_male_label_in_mris = %s,
                                avg_DCM_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_DCM_fraction_of_hc_heatmap_in_male_labels = %s,
                                avg_HCM_heart_in_mris = %s,
                                avg_HCM_fraction_of_gc_heatmap_in_heart = %s,
                                avg_HCM_fraction_of_hc_heatmap_in_heart = %s,
                                avg_HCM_fat_in_mris = %s,
                                avg_HCM_fraction_of_gc_heatmap_in_fat = %s,
                                avg_HCM_fraction_of_hc_heatmap_in_fat = %s,
                                avg_HCM_male_label_in_mris = %s,
                                avg_HCM_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_HCM_fraction_of_hc_heatmap_in_male_labels = %s
                              WHERE 
                              trial_uid = %s 
                          """,
                          ( 
                              performance_metrics['train_acc'],
                              performance_metrics['train_loss'],
                              performance_metrics['val_acc'],
                              performance_metrics['val_loss'],                            
                              performance_metrics['test_acc'],
                              performance_metrics['test_gc_loss'],
                              performance_metrics['test_cce_loss'],
                              performance_metrics['NOR']['avg_heart_in_mris'],
                              performance_metrics['NOR']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['NOR']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['NOR']['avg_fat_in_mris'],
                              performance_metrics['NOR']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['NOR']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['NOR']['avg_male_label_in_mris'],
                              performance_metrics['NOR']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['NOR']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              performance_metrics['RV']['avg_heart_in_mris'],
                              performance_metrics['RV']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['RV']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['RV']['avg_fat_in_mris'],
                              performance_metrics['RV']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['RV']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['RV']['avg_male_label_in_mris'],
                              performance_metrics['RV']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['RV']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              performance_metrics['DCM']['avg_heart_in_mris'],
                              performance_metrics['DCM']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['DCM']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['DCM']['avg_fat_in_mris'],
                              performance_metrics['DCM']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['DCM']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['DCM']['avg_male_label_in_mris'],
                              performance_metrics['DCM']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['DCM']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              performance_metrics['HCM']['avg_heart_in_mris'],
                              performance_metrics['HCM']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['HCM']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['HCM']['avg_fat_in_mris'],
                              performance_metrics['HCM']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['HCM']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['HCM']['avg_male_label_in_mris'],
                              performance_metrics['HCM']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['HCM']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              trial_uid
                          )
                        )
        else: #We probably just want to evaluate test dataset related losses e.g. for normal loss experiments
          cursor.execute(""" UPDATE trials_new 
                              SET 
                                test_acc = %s,
                                test_gc_loss = %s,
                                test_cce_loss = %s,
                                avg_NOR_heart_in_mris = %s,
                                avg_NOR_fraction_of_gc_heatmap_in_heart = %s,
                                avg_NOR_fraction_of_hc_heatmap_in_heart = %s,
                                avg_NOR_fat_in_mris = %s,
                                avg_NOR_fraction_of_gc_heatmap_in_fat = %s,
                                avg_NOR_fraction_of_hc_heatmap_in_fat = %s,
                                avg_NOR_male_label_in_mris = %s,
                                avg_NOR_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_NOR_fraction_of_hc_heatmap_in_male_labels = %s,
                                avg_RV_heart_in_mris = %s,
                                avg_RV_fraction_of_gc_heatmap_in_heart = %s,
                                avg_RV_fraction_of_hc_heatmap_in_heart = %s,
                                avg_RV_fat_in_mris = %s,
                                avg_RV_fraction_of_gc_heatmap_in_fat = %s,
                                avg_RV_fraction_of_hc_heatmap_in_fat = %s,
                                avg_RV_male_label_in_mris = %s,
                                avg_RV_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_RV_fraction_of_hc_heatmap_in_male_labels = %s,
                                avg_DCM_heart_in_mris = %s,
                                avg_DCM_fraction_of_gc_heatmap_in_heart = %s,
                                avg_DCM_fraction_of_hc_heatmap_in_heart = %s,
                                avg_DCM_fat_in_mris = %s,
                                avg_DCM_fraction_of_gc_heatmap_in_fat = %s,
                                avg_DCM_fraction_of_hc_heatmap_in_fat = %s,
                                avg_DCM_male_label_in_mris = %s,
                                avg_DCM_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_DCM_fraction_of_hc_heatmap_in_male_labels = %s,
                                avg_HCM_heart_in_mris = %s,
                                avg_HCM_fraction_of_gc_heatmap_in_heart = %s,
                                avg_HCM_fraction_of_hc_heatmap_in_heart = %s,
                                avg_HCM_fat_in_mris = %s,
                                avg_HCM_fraction_of_gc_heatmap_in_fat = %s,
                                avg_HCM_fraction_of_hc_heatmap_in_fat = %s,
                                avg_HCM_male_label_in_mris = %s,
                                avg_HCM_fraction_of_gc_heatmap_in_male_labels = %s,
                                avg_HCM_fraction_of_hc_heatmap_in_male_labels = %s
                              WHERE 
                              trial_uid = %s 
                          """,
                          (                            
                              performance_metrics['test_acc'],
                              performance_metrics['test_gc_loss'],
                              performance_metrics['test_cce_loss'],
                              performance_metrics['NOR']['avg_heart_in_mris'],
                              performance_metrics['NOR']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['NOR']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['NOR']['avg_fat_in_mris'],
                              performance_metrics['NOR']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['NOR']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['NOR']['avg_male_label_in_mris'],
                              performance_metrics['NOR']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['NOR']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              performance_metrics['RV']['avg_heart_in_mris'],
                              performance_metrics['RV']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['RV']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['RV']['avg_fat_in_mris'],
                              performance_metrics['RV']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['RV']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['RV']['avg_male_label_in_mris'],
                              performance_metrics['RV']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['RV']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              performance_metrics['DCM']['avg_heart_in_mris'],
                              performance_metrics['DCM']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['DCM']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['DCM']['avg_fat_in_mris'],
                              performance_metrics['DCM']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['DCM']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['DCM']['avg_male_label_in_mris'],
                              performance_metrics['DCM']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['DCM']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              performance_metrics['HCM']['avg_heart_in_mris'],
                              performance_metrics['HCM']['avg_fraction_of_gc_heatmap_in_heart'],
                              performance_metrics['HCM']['avg_fraction_of_hc_heatmap_in_heart'],
                              performance_metrics['HCM']['avg_fat_in_mris'],
                              performance_metrics['HCM']['avg_fraction_of_gc_heatmap_in_fat'],
                              performance_metrics['HCM']['avg_fraction_of_hc_heatmap_in_fat'],
                              performance_metrics['HCM']['avg_male_label_in_mris'],
                              performance_metrics['HCM']['avg_fraction_of_gc_heatmap_in_male_labels'],
                              performance_metrics['HCM']['avg_fraction_of_hc_heatmap_in_male_labels'],
                              trial_uid
                          )
                        )
    conn.close()
                                                        

def get_trial_by_trial_uid(trial_uid, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
      cursor.execute("SELECT * FROM trials_new WHERE trial_uid = %s", (trial_uid,))
      results = cursor.fetchall()
    conn.close()
    return results


def get_search_by_id(search_id, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
      cursor.execute(f"SELECT * FROM search WHERE search_id = '%s'", (search_id,))
      results = cursor.fetchall()
    conn.close()
    return results


def get_all_trials_new(database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute("SELECT * FROM trials_new")
        results = cursor.fetchall()
    conn.close()
    return results
  
def get_all_trials_by_search_id(search_id, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute("SELECT * FROM trials_new WHERE search_id=%s",(search_id,))
        results = cursor.fetchall()
    conn.close()
    return results

def get_all_searches(database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute("SELECT * FROM search")
        results = cursor.fetchall()
    conn.close()
    return results


def get_trial_uid_by_performance_metric(metric, ordering, database_connection_details):
  if metric in Model_Metrics._member_names_ and ordering in Order_By._member_names_ :
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute(f"SELECT trial_uid FROM trials_new ORDER BY {metric} {ordering}")
        results = cursor.fetchall()
    conn.close()
    return results
  elif metric not in Model_Metrics._member_names_:
    return 'Error - Requested to order trials_new by an invalid metric name. Metric param should be in Config.Model_Metrics._member_names_'
  elif ordering not in Order_By._member_names_:
    return 'Error - Requested to order trials_new by an invalid ordering option. Ordering param be in Config.Order_By._member_names_'  
  else:
    return 'Error - Requested to order trials_new by an invalid metric name or ordering option. Metric param should be in Config.Model_Metrics._member_names_ . Ordering param be in Config.Order_By._member_names_'


def get_trial_and_search_data_by_trial_uid(trial_uid, database_connection_details):
  conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
  cursor = conn.cursor()
  with conn:
      cursor.execute("""SELECT
                          trials_new.search_id,
                          experiment_number,
                          num_models,
                          num_epochs,
                          hyperparam_ranges,
                          git_commit_id,
                          data_path,
                          tensorboard_folder_path,
                          keras_tuner_folder_path,
                          search_duration_seconds,
                          trial_uid,
                          kt_trial_id,
                          model_path,
                          val_loss,
                          val_acc,
                          train_loss,
                          train_acc,
                          avg_male_label_in_mris,
                          avg_fraction_of_heatmap_in_male_labels,
                          avg_heart_in_mris,
                          avg_fraction_of_heatmap_in_heart
                          learning_rate
                        FROM trials_new
                        INNER JOIN search ON trials_new.search_id = search.search_id
                        WHERE trials_new.trial_uid = %s""", (trial_uid,)
      )
      results = cursor.fetchone()
  conn.close()
  search = {
    'search_id' : results[0], 
    'experiment_number' : results[1], 
    'num_models' : results[2], 
    'num_epochs' : results[3], 
    'hyperparam_ranges' : results[4], 
    'git_commit_id' : results[5], 
    'data_path' : results[6], 
    'tensorboard_folder_path' : results[7],
    'keras_tuner_folder_path' : results[8],
    'search_duration_seconds' : results[9]
  }
  trial = {
    'trial_uid' : results[10],
    'kt_trial_id' : results[11],
    'search_id' : results[12],
    'model_path' : results[13],
    'val_loss' : results[14],
    'val_acc' : results[15],
    'train_loss' : results[16],
    'train_acc' : results[17],
    'avg_male_label_in_mris' : results[18],
    'avg_fraction_of_heatmap_in_male_labels' : results[19],
    'avg_heart_in_mris' : results[20],
    'avg_fraction_of_heatmap_in_heart' : results[21],
    'learning_rate' : results[22]
  }

  return trial, search

def get_trial_uid_and_model_paths_with_no_test_accuracies( experiment_number , database_connection_details ):
  conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
  cursor = conn.cursor()
  with conn:
    cursor.execute("""
                      WITH exp1_nor_searches AS (
                      SELECT search_id FROM search WHERE experiment_number = %s 
                      AND tensorboard_folder_path != '' 
                      AND tensorboard_folder_path IS NOT NULL
                      )
                      SELECT trial_uid, model_path FROM trials_new WHERE search_id IN (SELECT search_id FROM exp1_nor_searches)
                      AND test_acc is NULL;
                  """, (experiment_number,))
    results = cursor.fetchall()
  conn.close()
  return results

def get_experiment_test_metrics( experiment_number , database_connection_details ):
  conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
  cursor = conn.cursor()
  with conn:
    cursor.execute( """WITH search_ids AS (
                        SELECT search_id FROM search WHERE experiment_number = %s
                      ) SELECT  test_acc ,
                                test_gc_loss ,
                                test_cce_loss ,
                                avg_NOR_heart_in_mris ,
                                avg_NOR_fraction_of_gc_heatmap_in_heart ,
                                avg_NOR_fraction_of_hc_heatmap_in_heart ,
                                avg_NOR_fat_in_mris ,
                                avg_NOR_fraction_of_gc_heatmap_in_fat ,
                                avg_NOR_fraction_of_hc_heatmap_in_fat ,
                                avg_NOR_male_label_in_mris ,
                                avg_NOR_fraction_of_gc_heatmap_in_male_labels ,
                                avg_NOR_fraction_of_hc_heatmap_in_male_labels ,
                                avg_RV_heart_in_mris ,
                                avg_RV_fraction_of_gc_heatmap_in_heart ,
                                avg_RV_fraction_of_hc_heatmap_in_heart ,
                                avg_RV_fat_in_mris ,
                                avg_RV_fraction_of_gc_heatmap_in_fat ,
                                avg_RV_fraction_of_hc_heatmap_in_fat ,
                                avg_RV_male_label_in_mris ,
                                avg_RV_fraction_of_gc_heatmap_in_male_labels ,
                                avg_RV_fraction_of_hc_heatmap_in_male_labels ,
                                avg_DCM_heart_in_mris ,
                                avg_DCM_fraction_of_gc_heatmap_in_heart ,
                                avg_DCM_fraction_of_hc_heatmap_in_heart ,
                                avg_DCM_fat_in_mris ,
                                avg_DCM_fraction_of_gc_heatmap_in_fat ,
                                avg_DCM_fraction_of_hc_heatmap_in_fat ,
                                avg_DCM_male_label_in_mris ,
                                avg_DCM_fraction_of_gc_heatmap_in_male_labels ,
                                avg_DCM_fraction_of_hc_heatmap_in_male_labels ,
                                avg_HCM_heart_in_mris ,
                                avg_HCM_fraction_of_gc_heatmap_in_heart ,
                                avg_HCM_fraction_of_hc_heatmap_in_heart ,
                                avg_HCM_fat_in_mris ,
                                avg_HCM_fraction_of_gc_heatmap_in_fat ,
                                avg_HCM_fraction_of_hc_heatmap_in_fat ,
                                avg_HCM_male_label_in_mris ,
                                avg_HCM_fraction_of_gc_heatmap_in_male_labels ,
                                avg_HCM_fraction_of_hc_heatmap_in_male_labels 
                       FROM trials_new WHERE val_acc > 0.95 
                        AND search_id IN (SELECT search_id FROM search_ids);
                    """, (experiment_number,)
                  )
    results = cursor.fetchall()
  conn.close()

  trial_results = []
  for trial_result in results:
    trial_result_dict = {
                      'test_acc' : trial_result[0] ,
                      'test_gc_loss' : trial_result[1] ,
                      'test_cce_loss' : trial_result[2] ,
                      'avg_NOR_heart_in_mris' : trial_result[3] ,
                      'avg_NOR_fraction_of_gc_heatmap_in_heart' : trial_result[4] ,
                      'avg_NOR_fraction_of_hc_heatmap_in_heart' : trial_result[5] ,
                      'avg_NOR_fat_in_mris' : trial_result[6] ,
                      'avg_NOR_fraction_of_gc_heatmap_in_fat' : trial_result[7] ,
                      'avg_NOR_fraction_of_hc_heatmap_in_fat' : trial_result[8] ,
                      'avg_NOR_male_label_in_mris' : trial_result[9] ,
                      'avg_NOR_fraction_of_gc_heatmap_in_male_labels' : trial_result[10] ,
                      'avg_NOR_fraction_of_hc_heatmap_in_male_labels' : trial_result[11] ,
                      'avg_RV_heart_in_mris' : trial_result[12] ,
                      'avg_RV_fraction_of_gc_heatmap_in_heart' : trial_result[13] ,
                      'avg_RV_fraction_of_hc_heatmap_in_heart' : trial_result[14] ,
                      'avg_RV_fat_in_mris' : trial_result[15] ,
                      'avg_RV_fraction_of_gc_heatmap_in_fat' : trial_result[16] ,
                      'avg_RV_fraction_of_hc_heatmap_in_fat' : trial_result[17] ,
                      'avg_RV_male_label_in_mris' : trial_result[18] ,
                      'avg_RV_fraction_of_gc_heatmap_in_male_labels' : trial_result[19] ,
                      'avg_RV_fraction_of_hc_heatmap_in_male_labels' : trial_result[20] ,
                      'avg_DCM_heart_in_mris' : trial_result[21] ,
                      'avg_DCM_fraction_of_gc_heatmap_in_heart' : trial_result[22] ,
                      'avg_DCM_fraction_of_hc_heatmap_in_heart' : trial_result[23] ,
                      'avg_DCM_fat_in_mris' : trial_result[24] ,
                      'avg_DCM_fraction_of_gc_heatmap_in_fat' : trial_result[25] ,
                      'avg_DCM_fraction_of_hc_heatmap_in_fat' : trial_result[26] ,
                      'avg_DCM_male_label_in_mris' : trial_result[27] ,
                      'avg_DCM_fraction_of_gc_heatmap_in_male_labels' : trial_result[28] ,
                      'avg_DCM_fraction_of_hc_heatmap_in_male_labels' : trial_result[29] ,
                      'avg_HCM_heart_in_mris' : trial_result[30] ,
                      'avg_HCM_fraction_of_gc_heatmap_in_heart' : trial_result[31] ,
                      'avg_HCM_fraction_of_hc_heatmap_in_heart' : trial_result[32] ,
                      'avg_HCM_fat_in_mris' : trial_result[33] ,
                      'avg_HCM_fraction_of_gc_heatmap_in_fat' : trial_result[34] ,
                      'avg_HCM_fraction_of_hc_heatmap_in_fat' : trial_result[35] ,
                      'avg_HCM_male_label_in_mris' : trial_result[36] ,
                      'avg_HCM_fraction_of_gc_heatmap_in_male_labels' : trial_result[37] ,
                      'avg_HCM_fraction_of_hc_heatmap_in_male_labels' : trial_result[38]
    }
    trial_results.append(trial_result_dict)
    return trial_results

# def update_trial_with_heatmap_data(trial_updated, database_connection_details): 
#     conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
#     cursor = conn.cursor()
#     with conn:
#         cursor.execute( """ UPDATE trials_new 
#                             SET 
#                               average_fraction_of_heart_in_mri_batch = %s,
#                               average_fraction_of_pos_gradients_in_heart_in_batch_of_mris = %s,
#                               average_fraction_of_neg_gradients_in_heart_in_batch_of_mris = %s
#                             WHERE 
#                             trial_uid = %s 
#                         """,
#                         ( 
#                             trial_updated['average_fraction_of_heart_in_mri_batch'],
#                             trial_updated['average_fraction_of_pos_gradients_in_heart_in_batch_of_mris'],
#                             trial_updated['average_fraction_of_neg_gradients_in_heart_in_batch_of_mris'],
#                             trial_updated['trial_uid']
#                         )
#                       )
#     conn.close()


# def get_trial_uids_without_heatmap_overlap_metrics(database_connection_details):
#   conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
#   cursor = conn.cursor()
#   with conn:
#       cursor.execute(f""" SELECT trial_uid FROM trials_new 
#                           WHERE 
#                                   average_fraction_of_heart_in_mri_batch                        IS NULL 
#                               AND average_fraction_of_pos_gradients_in_heart_in_batch_of_mris   IS NULL 
#                               AND average_fraction_of_neg_gradients_in_heart_in_batch_of_mris   IS NULL
#                       """
#                     )
#       results = cursor.fetchall()
#   conn.close()
#   return results