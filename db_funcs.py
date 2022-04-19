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

def insert_search(search, database_connection_details):
    conn = psycopg2.connect(database="postgres", user = database_connection_details['user'], host = database_connection_details['ngrok_host'] , port = database_connection_details['ngrok_port'])
    cursor = conn.cursor()
    with conn:
        cursor.execute(f"""INSERT INTO search 
                        ( search_id ,
                          search_type,  #exp1_normal_loss or exp1_gc_loss
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
                          search['search_type'],
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
                          )
                          VALUES (%s,%s,%s,%s,%s,%s,%s)
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
                          search_type,
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
                          train_acc
                        FROM trials_new
                        INNER JOIN search ON trials_new.search_id = search.search_id
                        WHERE trials_new.trial_uid = %s""", (trial_uid,)
      )
      results = cursor.fetchone()
  conn.close()
  search = {
    'search_id' : results[0], 
    'search_type' : results[1], 
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
    'train_acc' : results[17]
  }

  return trial, search


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


# def get_trial_uids_without_grad_cam_overlap_metrics(database_connection_details):
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