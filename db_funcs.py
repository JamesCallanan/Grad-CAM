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

def update_trial(trial_uid, performance_metrics, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute(""" UPDATE trials_new 
                            SET 
                              test_acc = %s,
                              test_gc_loss = %s,
                              test_cce_loss = %s,
                              avg_heart_in_mris = %s,
                              avg_fraction_of_gc_heatmap_in_heart = %s,
                              avg_fraction_of_hc_heatmap_in_heart = %s,
                              avg_male_label_in_mris = %s,
                              avg_fraction_of_gc_heatmap_in_male_labels = %s,
                              avg_fraction_of_hc_heatmap_in_male_labels = %s,
                              avg_fat_in_mris = %s,
                              avg_fraction_of_gc_heatmap_in_fat = %s,
                              avg_fraction_of_hc_heatmap_in_fat = %s
                            WHERE 
                            trial_uid = %s 
                        """,
                        ( 
                            performance_metrics['test_acc'],
                            performance_metrics['test_gc_loss'],
                            performance_metrics['test_cce_loss'],
                            performance_metrics['avg_heart_in_mris'],
                            performance_metrics['avg_fraction_of_gc_heatmap_in_heart'],
                            performance_metrics['avg_fraction_of_hc_heatmap_in_heart'],
                            performance_metrics['avg_male_label_in_mris'],
                            performance_metrics['avg_fraction_of_gc_heatmap_in_male_labels'],
                            performance_metrics['avg_fraction_of_hc_heatmap_in_male_labels'],
                            performance_metrics['avg_fat_in_mris'],
                            performance_metrics['avg_fraction_of_gc_heatmap_in_fat'],
                            performance_metrics['avg_fraction_of_hc_heatmap_in_fat']
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