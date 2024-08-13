"""OLD:Script handling ML model training
-> Refer to retraining/main_retraining.py for all things ML
"""
# Imports
import pickle
import sys
import time
import os
from os.path import join
from random import shuffle
import pandas as pd
import json

pth = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(pth)
sys.path.append(pth)

from ml.errors import error_analysis
from ml.config_train import CONFIG_TR
from ml.ml_classif import train_classif_models, text_to_tokens, VOCABULARY

from ml.performance import assess_performance


def summarize_performance(df_pred, df_pred_tr, mdl, X_test, y_test_cv, feats):
    """Assess prediction performance of the model mdl"""
    print("INFO:---DO_performance---")
    # PRED_COLS = ["id", "url", "actual", "pred", "filtered_text"]
    y_train = df_pred_tr["actual"]
    y_pred_tr = df_pred_tr["pred"]

    y_test = df_pred["actual"]
    y_pred_te = df_pred["pred"]

    assess_performance(y_train, y_test, y_pred_tr, y_pred_te, mdl, feats, X_test, y_test_cv)


def train():
    """Main function to train LV1 and LV2 classifiers + data exploration steps
    Save a performance report in config[dir_output]
    Save an error analysis report  in inter/ml/errors/error_analysis.csv
    """
    print("SCENARIO: {}".format(CONFIG_TR["scenario"]))

    with open(CONFIG_TR["fp_dataset"], "r", encoding='utf-8') as f:
        df = json.loads(f.read().encode('raw_unicode_escape').decode())
    shuffle(df)
    df = pd.DataFrame(df)

    if CONFIG_TR["SAMPLING"] is not None:
        df = df.head(CONFIG_TR["SAMPLING"])
    print("INFO initial data size :{}".format(len(df)))
    print("INFO data columns :{}".format(",".join(list(df.columns))))

    # preprocINFO data size :2556
    df = text_to_tokens(df)

    print("INFO final data size :{}".format(len(df)))

    # for optimization only:
    # with open(join(CONFIG_TR["dir_inter"], "preprocessed_dataset.pkl"), "wb+") as f:
    #     pickle.dump(df, f)
    # with open(join(CONFIG_TR["dir_inter"], "preprocessed_dataset.pkl"), "rb+") as f:
    #     df = pickle.load(f)

    if CONFIG_TR["DO_ML"]:
        df_pred, df_pred_tr, mdl, X_test, y_test_cv, feats, all_feats_test = train_classif_models(df)

    if CONFIG_TR["DO_PERFORMANCE"]:
        # evaluate performance
        summarize_performance(df_pred, df_pred_tr, mdl, X_test, y_test_cv, feats)

    # ERROR analysis
    error_analysis(df_pred, all_feats_test)

    print("INFO ----- ALL DONE---------")

if __name__ == '__main__':
    tic_tic = time.time()
    train()
    print("Total time in seconds (main): {}".format(time.time() - tic_tic))

