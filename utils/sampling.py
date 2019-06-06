import time
from collections import defaultdict
import numpy as np


class NegativeSampling:
    def __init__(self, dataset, num_neg, batch_size=64, seed=42, replacement_sampling=False):
        self.dataset = dataset
        self.num_neg = num_neg
        self.batch_size = batch_size
        self.seed = seed
        self.i = 0
        self.item_pool = defaultdict(set)
        if not replacement_sampling:
            self.__init_sampling()

    def __init_sampling(self):
        self.user_negative_pool = {}
        for u in self.dataset.train_user:
            self.user_negative_pool[u] = list(set(range(self.dataset.n_items)) - set(self.dataset.train_user[u]))

    def __call__(self, mode):
        if mode == "train":
            user_indices = self.dataset.train_user_indices
            item_indices = self.dataset.train_item_indices
            label_indices = self.dataset.train_labels
        elif mode == "test":
            user_indices = self.dataset.test_user_indices
            item_indices = self.dataset.test_item_indices
            label_indices = self.dataset.test_labels

        '''
        user, item, label = [], [], []
        for i, u in enumerate(user_indices):
            user.append(user_indices[i])
            item.append(item_indices[i])
            label.append(label_indices[i])
            for _ in range(self.num_neg):
                item_neg = np.random.randint(0, self.dataset.n_items)
                while item_neg in self.dataset.train_user[u]:
                    item_neg = np.random.randint(0, self.dataset.n_items)

                user.append(u)
                item.append(item_neg)
                label.append(0.0)
        return np.array(user), np.array(item), np.array(label)
        '''


        user_implicit = np.tile(user_indices, self.num_neg + 1)
        label_negative = np.zeros(len(user_indices) * self.num_neg, dtype=np.float32)
        label_implicit = np.concatenate([label_indices, label_negative])
        item_negative = []
        for u, i in zip(user_indices, item_indices):
            for _ in range(self.num_neg):
                item_neg = np.random.randint(0, self.dataset.n_items)
                while item_neg in self.dataset.train_user[u]:
                    item_neg = np.random.randint(0, self.dataset.n_items)

                item_negative.append(item_neg)
        item_implicit = np.concatenate([item_indices, item_negative])
        return user_implicit, item_implicit, label_implicit


    def next_batch_without_replacement(self):
        end = min(len(self.dataset.train_user_indices), (self.i + 1) * self.batch_size)
        batch_pos_user = self.dataset.train_user_indices[self.i * self.batch_size: end]
        batch_pos_item = self.dataset.train_item_indices[self.i * self.batch_size: end]
        batch_pos_label = self.dataset.train_labels[self.i * self.batch_size: end]

        batch_user_indices, batch_item_indices, batch_label_indices = [], [], []
        for i, u in enumerate(batch_pos_user):
            batch_user_indices.append(batch_pos_user[i])
            batch_item_indices.append(batch_pos_item[i])
            batch_label_indices.append(batch_pos_label[i])

            batch_user_indices.extend([u] * self.num_neg)
            item_neg = np.random.choice(self.user_negative_pool[u], self.num_neg, replace=False)
            batch_item_indices.extend(item_neg)
            batch_label_indices.extend([0.0] * self.num_neg)
            self.user_negative_pool[u] = list(set(self.user_negative_pool[u]) - set(item_neg))
            if len(self.user_negative_pool[u]) < self.num_neg + 1:
                self.user_negative_pool[u] = list(set(range(self.dataset.n_items)) - set(self.dataset.train_user[u]))
                print("negative pool exhausted")

        self.i += 1
        indices = np.random.permutation(len(batch_user_indices))
        return np.array(batch_user_indices)[indices], \
               np.array(batch_item_indices)[indices], \
               np.array(batch_label_indices)[indices]

    def next_batch(self):
        end = min(len(self.dataset.train_user_indices), (self.i + 1) * self.batch_size)
        batch_pos_user = self.dataset.train_user_indices[self.i * self.batch_size: end]
        batch_pos_item = self.dataset.train_item_indices[self.i * self.batch_size: end]
        batch_pos_label = self.dataset.train_labels[self.i * self.batch_size: end]

        batch_user_indices, batch_item_indices, batch_label_indices = [], [], []
        for i, u in enumerate(batch_pos_user):
            batch_user_indices.append(batch_pos_user[i])
            batch_item_indices.append(batch_pos_item[i])
            batch_label_indices.append(batch_pos_label[i])

            for _ in range(self.num_neg):
                item_neg = np.random.randint(0, self.dataset.n_items)
        #        while item_neg in self.dataset.train_user[u]:
                while self.dataset.train_user[u].__contains__(item_neg):
                    item_neg = np.random.randint(0, self.dataset.n_items)  # resample

                batch_user_indices.append(u)
                batch_item_indices.append(item_neg)
                batch_label_indices.append(0.0)

        self.i += 1
        indices = np.random.permutation(len(batch_user_indices))
        return np.array(batch_user_indices)[indices], \
               np.array(batch_item_indices)[indices], \
               np.array(batch_label_indices)[indices]


class NegativeSamplingFeat:
    def __init__(self, dataset, num_neg, batch_size=64, seed=42, replacement_sampling=False):
        self.dataset = dataset
        self.num_neg = num_neg
        self.batch_size = batch_size
        self.seed = seed
        self.i = 0
        self.item_pool = defaultdict(set)
        if not replacement_sampling:
            self.__init_sampling()

    def __init_sampling(self):
        self.user_negative_pool = {}
        for u in self.dataset.train_user:
            self.user_negative_pool[u] = list(set(range(self.dataset.n_items)) - set(self.dataset.train_user[u]))

    def __call__(self, mode):
        if mode == "train":
            feat_indices = self.dataset.train_feat_indices
            feat_values = self.dataset.train_feat_values
            feat_labels = self.dataset.train_labels
        elif mode == "test":
            feat_indices = self.dataset.test_feat_indices
            feat_values = self.dataset.test_feat_values
            feat_labels = self.dataset.test_labels

        indices, values, labels = [], [], []
        for i, sample in enumerate(feat_indices):
            user = sample[-2]
            indices.append(feat_indices[i])
            values.append(feat_values[i])
            labels.append(feat_labels[i])
            for _ in range(self.num_neg):
                item_neg = np.random.randint(0, self.dataset.n_items)
                while item_neg in self.dataset.train_user[user]:
                    item_neg = np.random.randint(0, self.dataset.n_items)

                sample[-1] = item_neg
                indices.append(sample)
                values.append(feat_values[i])
                labels.append(0.0)
        return np.array(indices), np.array(values), np.array(labels)

    def next_batch_without_replacement(self):  # change to feat version
        end = min(len(self.dataset.train_user_indices), (self.i + 1) * self.batch_size)
        batch_pos_user = self.dataset.train_user_indices[self.i * self.batch_size: end]
        batch_pos_item = self.dataset.train_item_indices[self.i * self.batch_size: end]
        batch_pos_label = self.dataset.train_labels[self.i * self.batch_size: end]

        batch_user_indices, batch_item_indices, batch_label_indices = [], [], []
        for i, u in enumerate(batch_pos_user):
            batch_user_indices.append(batch_pos_user[i])
            batch_item_indices.append(batch_pos_item[i])
            batch_label_indices.append(batch_pos_label[i])

            batch_user_indices.extend([u] * self.num_neg)
            item_neg = np.random.choice(self.user_negative_pool[u], self.num_neg, replace=False)
            batch_item_indices.extend(item_neg)
            batch_label_indices.extend([0.0] * self.num_neg)
            self.user_negative_pool[u] = list(set(self.user_negative_pool[u]) - set(item_neg))
            if len(self.user_negative_pool[u]) < self.num_neg + 1:
                self.user_negative_pool[u] = list(set(range(self.dataset.n_items)) - set(self.dataset.train_user[u]))
                print("negative pool exhausted")

        self.i += 1
        indices = np.random.permutation(len(batch_user_indices))
        return np.array(batch_user_indices)[indices], \
               np.array(batch_item_indices)[indices], \
               np.array(batch_label_indices)[indices]

    def next_batch(self):
        end = min(len(self.dataset.train_user_indices), (self.i + 1) * self.batch_size)
        batch_pos_user = self.dataset.train_user_indices[self.i * self.batch_size: end]
        batch_pos_item = self.dataset.train_item_indices[self.i * self.batch_size: end]
        batch_pos_label = self.dataset.train_labels[self.i * self.batch_size: end]

        batch_user_indices, batch_item_indices, batch_label_indices = [], [], []
        for i, u in enumerate(batch_pos_user):
            batch_user_indices.append(batch_pos_user[i])
            batch_item_indices.append(batch_pos_item[i])
            batch_label_indices.append(batch_pos_label[i])

            for _ in range(self.num_neg):
                item_neg = np.random.randint(0, self.dataset.n_items)
        #        while item_neg in self.dataset.train_user[u]:
                while self.dataset.train_user[u].__contains__(item_neg):
                    item_neg = np.random.randint(0, self.dataset.n_items)  # resample

                batch_user_indices.append(u)
                batch_item_indices.append(item_neg)
                batch_label_indices.append(0.0)

        self.i += 1
        indices = np.random.permutation(len(batch_user_indices))
        return np.array(batch_user_indices)[indices], \
               np.array(batch_item_indices)[indices], \
               np.array(batch_label_indices)[indices]












class PairwiseSampling:
    def __init__(self, dataset, batch_size=None):
        self.dataset = dataset
        self.batch_size = batch_size
        self.i = 0

    def __call__(self, mode):
        if mode == "train":
            user_indices = self.dataset.train_user_indices
            item_indices = self.dataset.train_item_indices
            label_indices = self.dataset.train_labels
        elif mode == "test":
            user_indices = self.dataset.test_user_indices
            item_indices = self.dataset.test_item_indices
            label_indices = self.dataset.test_labels

        user, item, label = [], [], []
        for i, u in enumerate(user_indices):
            user.append(user_indices[i])
            item.append(item_indices[i])
            label.append(label_indices[i])

            item_neg = np.random.randint(0, self.dataset.n_items)
            while item_neg in self.dataset.train_user[u]:
                item_neg = np.random.randint(0, self.dataset.n_items)
            user.append(u)
            item.append(item_neg)
            label.append(0.0)
        return np.array(user), \
               np.array(item), \
               np.array(label)

    def next_mf(self, user_factors, item_factors, bootstrap=False):
        if bootstrap:
            random_i = np.random.choice(len(self.dataset.train_user_indices), 1, replace=True)
        #    random_i = np.random.randint(0, self.dataset.n_users)
            user, item_i = self.dataset.train_user_indices[random_i][0], \
                           self.dataset.train_item_indices[random_i][0]
            item_j = np.random.randint(0, self.dataset.n_items)  # self.dataset.n_items - 1
            while item_j in self.dataset.train_user[user]:
                item_j = np.random.randint(0, self.dataset.n_items)

            x_ui = np.dot(user_factors[user], item_factors[item_i])
            x_uj = np.dot(user_factors[user], item_factors[item_j])
            x_uij = x_ui - x_uj
            return user, item_i, item_j, x_uij

        elif self.batch_size == 1:
            user, item_i = self.dataset.train_user_indices[self.i], \
                           self.dataset.train_item_indices[self.i]
            item_j = np.random.randint(0, self.dataset.n_items)
            while item_j in self.dataset.train_user[user]:
                item_j = np.random.randint(0, self.dataset.n_items)

            x_ui = np.dot(user_factors[user], item_factors[item_i])
            x_uj = np.dot(user_factors[user], item_factors[item_j])
            x_uij = x_ui - x_uj
            self.i += 1
            return user, item_i, item_j, x_uij

        elif self.batch_size > 1:
            batch_item_j, batch_x_uij = [], []
            end = min(len(self.dataset.train_user_indices), (self.i + 1) * self.batch_size)
            batch_user = self.dataset.train_user_indices[self.i * self.batch_size: end]
            batch_item_i = self.dataset.train_item_indices[self.i * self.batch_size: end]
            for user, item_i in zip(batch_user, batch_item_i):
                item_j = np.random.randint(0, self.dataset.n_items)
                while item_j in self.dataset.train_user[user]:
                    item_j = np.random.randint(0, self.dataset.n_items)
                batch_item_j.append(item_j)

                x_ui = np.dot(user_factors[user], item_factors[item_i])
                x_uj = np.dot(user_factors[user], item_factors[item_j])
                x_uij = x_ui - x_uj
                batch_x_uij.append(x_uij)
            self.i += 1
            return batch_user, batch_item_i, np.array(batch_item_j), np.array(batch_x_uij)

        else:
            raise ValueError("either use bootstrap or batch size must be positive integer.")

    def next_mf_tf(self):
        batch_item_j, batch_x_uij = [], []
        end = min(len(self.dataset.train_user_indices), (self.i + 1) * self.batch_size)
        batch_user = self.dataset.train_user_indices[self.i * self.batch_size: end]
        batch_item_i = self.dataset.train_item_indices[self.i * self.batch_size: end]
        for user, item_i in zip(batch_user, batch_item_i):
            item_j = np.random.randint(0, self.dataset.n_items)
            while item_j in self.dataset.train_user[user]:
                item_j = np.random.randint(0, self.dataset.n_items)
            batch_item_j.append(item_j)
        self.i += 1
        return batch_user, batch_item_i, np.array(batch_item_j)

    def next_knn(self, sim_matrix, k=20):
        user, item_i = self.dataset.train_user_indices[self.i], \
                       self.dataset.train_item_indices[self.i]
        item_j = np.random.randint(0, self.dataset.n_items)
        while item_j in self.dataset.train_user[user]:
            item_j = np.random.randint(0, self.dataset.n_items)

        u_items = np.array(list(self.dataset.train_user[user]))
        item_i_neighbors_sim = sim_matrix[item_i, u_items]
        indices = np.argsort(item_i_neighbors_sim)[::-1][:k]
        i_k_neighbors = u_items[indices]
        x_ui = np.sum(item_i_neighbors_sim[indices])

        item_j_neighbors_sim = sim_matrix[item_j, u_items]
        indices = np.argsort(item_j_neighbors_sim)[::-1][:k]
        j_k_neighbors = u_items[indices]
        x_uj = np.sum(item_j_neighbors_sim[indices])

        x_uij = x_ui - x_uj
        self.i += 1
        return user, item_i, i_k_neighbors, item_j, j_k_neighbors, x_uij
















