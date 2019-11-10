import os, time, sys
import numpy as np
import tensorflow as tf
from pathlib import Path, PurePath
from libreco.dataset import DatasetPure, DatasetFeat
from libreco.algorithms import SVD, SVDpp, Als, Ncf, Bpr, userKNN, itemKNN, FmPure, DeepFmPure
from libreco.evaluate import rmse, rmse_tf, MAP_at_k, AP_at_k
from libreco import baseline_als
from libreco import NegativeSampling
from libreco.utils import export_model_pickle, export_model_joblib, export_model_tf, export_feature_transform
# from libreco.utils import export_model_pickle, export_model_joblib
import pickle
import cProfile
np.set_printoptions(precision=4, edgeitems=7)


if __name__ == "__main__":
    t0 = time.time()
#    dataset = DatasetPure()
#    path = str(Path.joinpath(Path(__file__).parent, "ml-1m", "ratings.dat"))
#    path = str(Path.joinpath(Path(__file__).parent, "tianchi_recommender", "testB_pure.csv"))
#    dataset.build_dataset(data_path=path, sep=",", length="all", shuffle=True,
#                          convert_implicit=True, build_negative=True, num_neg=2, batch_size=256,
#                          build_tf_dataset=False)
#    dataset.leave_k_out_split(4, data_path="ml-1m/ratings.dat", length=100000, sep="::",
#                              convert_implicit=True, build_negative=True, batch_size=256, num_neg=1)
#    print("num_users: {}, num_items: {}".format(dataset.n_users, dataset.n_items))
#    print("data size: ", len(dataset.train_user_implicit) + len(dataset.test_user_implicit))
#    print("data processing time: {:.2f}".format(time.time() - t0))

    conf = {
    #    "data_path": "../tianchi_recommender/testB_pure.csv",
        "data_path": "../ml-1m/ratings.dat",
        "length": 1000000,
        "convert_implicit": True,
        "build_negative": True,
        "num_neg": 1,
    #    "batch_size": 2048,
    #    "lower_upper_bound": [1, 5],
        "sep": "::",
    }

    dataset = DatasetPure()
    dataset.build_dataset(**conf)
    #    dataset.leave_k_out_split(4, data_path="ml-1m/ratings.dat", length=100000, sep="::",
    #                              convert_implicit=True, build_negative=True, batch_size=256, num_neg=1)
    print("num_users: {}, num_items: {}".format(dataset.n_users, dataset.n_items))
    if conf.get("convert_implicit"):
        print("data size: ", len(dataset.train_user_implicit) + len(dataset.test_user_implicit))
    else:
        print("data size: ", len(dataset.train_user_indices) + len(dataset.test_user_indices))
    print("data processing time: {:.2f}".format(time.time() - t0))
    print()

    als = Als(n_factors=300, n_epochs=200, reg=10.0, alpha=1, task="ranking", neg_sampling=True)
    als.fit(dataset, use_cg=True, cg_steps=3, use_cython=False, verbose=1)
    print("predict: ", als.predict(1, 5))
    print(als.recommend_user(1, 7))

#    import cProfile
#    cProfile.run('svd.fit(dataset)')

#    svd = SVDpp(n_factors=32, n_epochs=200, lr=0.001, reg=0.0, batch_size=4096, task="ranking",
#                neg_sampling=True)  # concat ?
#    svd.fit(dataset, verbose=1)
#    print(svd.predict(1,2))
#    print(svd.recommend_user(1, 7))

#    ncf = Ncf(embed_size=32, lr=0.001, n_epochs=200, reg=0.1, batch_size=2048,
#              dropout_rate=0.5, task="ranking", neg_sampling=True)
#    ncf.fit(dataset)

#    svd = SVD(n_factors=32, n_epochs=200, lr=0.001, reg=0.001, batch_size=256, task="ranking",
#                neg_sampling=True)  # concat ?
#    svd.fit(dataset, verbose=1)
#    print(svd.predict(1,2))
#    print(svd.recommend_user(1, 7))

#    bpr = Bpr(lr=0.001, n_epochs=10000, reg=0.0, n_factors=16, batch_size=256, k=20,
#              method="knn", neg_sampling=True)
#    bpr.fit(dataset, verbose=1)
#    print(bpr.predict(1, 2))
#    print(bpr.recommend_user(1, 7))

#    user_knn = userKNN(sim_option="cosine", k=5, min_support=1, baseline=False, task="ranking", neg_sampling=True)
#    user_knn.fit(dataset, verbose=1)
#    t1 = time.time()
#    print("predict: ", user_knn.predict(0, 5))
#    print("recommend: ", user_knn.recommend_user(0, 7, like_score=4.0, random_rec=False))
#    print("predict time: ", time.time() - t1)

#    item_knn = itemKNN(sim_option="sklearn", k=40, min_support=1, baseline=False, task="ranking", neg_sampling=True)
#    item_knn.fit(dataset, verbose=1)
#    t1 = time.time()
#    print("predict: ", item_knn.predict(0, 5))
#    print("recommend: ", item_knn.recommend_user(0, 7, like_score=4.0, random_rec=False))
#    print("predict time: ", time.time() - t1)

#    fm = FmPure(lr=0.001, n_epochs=20000, reg=0.001, n_factors=100, batch_size=1024, task="ranking", neg_sampling=True)
#    fm.fit(dataset, verbose=1)
#    print(fm.predict(1959, 1992))
#    print(fm.recommend_user(19500, 7))

#    deepFm = DeepFmPure(lr=0.001, n_epochs=1, reg=0.0, embed_size=100, batch_size=2048, dropout_rate=0.0,
#                        task="ranking", neg_sampling=True, network_size=[100, 100, 100])
#    deepFm.fit(dataset, verbose=1)
#    print(deepFm.predict(1959, 1992))
#    print(deepFm.recommend_user(19500, 7))

    print("train + test time: {:.4f}".format(time.time() - t0))


