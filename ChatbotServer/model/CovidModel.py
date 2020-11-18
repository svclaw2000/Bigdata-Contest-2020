import tensorflow as tf
import numpy as np
from data.Covid import Covid
from data.CovidResult import CovidResult
import datetime

class CovidModel:
    def __init__(self, max_date = None):
        # Initialize data
        self.conf_data = None
        self.conf_train_x = None
        self.conf_train_y = None
        self.conf_valid_x = None
        self.conf_valid_y = None
        self.conf_test_x = None
        self.conf_test_y = None

        self.dead_data = None
        self.dead_train_x = None
        self.dead_train_y = None
        self.dead_valid_x = None
        self.dead_valid_y = None
        self.dead_test_x = None
        self.dead_test_y = None

        self.n_steps = 21
        self.n_inputs = 1
        self.n_outputs = 1
        self.n_neurons = 100
        self.learning_rate = 0.001
        self.n_iterations = 2000
        self.n_predictions = 7

        self.conf_sess = None
        self.dead_sess = None
        self.max_date = max_date

    def make_data(self, train_ratio=0.8, valid_ratio=0.1, test_ratio=0.1):
        conf_data = Covid.get_as_dataframe('confirm', self.max_date)
        conf_data = conf_data[conf_data['date'] > datetime.date(2020, 3, 4)]
        self.conf_data = conf_data.pivot(index='locale', columns='date', values='new_confirm')

        total_x, total_y = moving_window(np.array(self.conf_data), self.n_steps)
        n_total = total_x.shape[0]
        total_idx = np.arange(n_total)
        np.random.shuffle(total_idx)
        train_idx, valid_idx, test_idx = np.split(total_idx, [int(n_total * 0.8), int(n_total * 0.9)])

        self.conf_train_x, self.conf_train_y = total_x[train_idx], total_y[train_idx]
        self.conf_valid_x, self.conf_valid_y = total_x[valid_idx], total_y[valid_idx]
        self.conf_test_x, self.conf_test_y = total_x[test_idx], total_y[test_idx]

        dead_data = Covid.get_as_dataframe('dead', self.max_date)
        dead_data = dead_data[dead_data['date'] > datetime.date(2020, 3, 4)]
        self.dead_data = dead_data.pivot(index='locale', columns='date', values='new_dead')

        total_x, total_y = moving_window(np.array(self.dead_data), self.n_steps)
        n_total = total_x.shape[0]
        total_idx = np.arange(n_total)
        np.random.shuffle(total_idx)
        train_idx, valid_idx, test_idx = np.split(total_idx, [int(n_total * 0.8), int(n_total * 0.9)])

        self.dead_train_x, self.dead_train_y = total_x[train_idx], total_y[train_idx]
        self.dead_valid_x, self.dead_valid_y = total_x[valid_idx], total_y[valid_idx]
        self.dead_test_x, self.dead_test_y = total_x[test_idx], total_y[test_idx]

    def make_model(self):
        tf.reset_default_graph()

        self.X = tf.placeholder(tf.float32, [None, self.n_steps, self.n_inputs])
        self.Y = tf.placeholder(tf.int32, [None, self.n_steps, self.n_outputs])

        self.cell = tf.nn.rnn_cell.BasicRNNCell(num_units=self.n_neurons, activation=tf.nn.relu)
        self.rnn_outputs, self.states = tf.nn.dynamic_rnn(self.cell, self.X, dtype=tf.float32)

        self.stacked_rnn_outputs = tf.reshape(tensor=self.rnn_outputs, shape=[-1, self.n_neurons]) #?, 100
        self.stacked_outputs = tf.layers.dense(self.stacked_rnn_outputs, self.n_outputs) #?, 1
        self.predictions = tf.reshape(self.stacked_outputs, [-1, self.n_steps, self.n_outputs]) #?, 21, 1

        self.mse = tf.losses.mean_squared_error(labels=self.Y, predictions=self.predictions)
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.mse)

    def train(self):
        if self.conf_data is None or self.dead_data is None:
            self.make_data()

        if self.conf_sess is not None:
            self.conf_sess.close()
            self.conf_sess = None
        if self.dead_sess is not None:
            self.dead_sess.close()
            self.dead_sess = None
        self.make_model()
        self.conf_sess = tf.Session()
        self.dead_sess = tf.Session()
        self.conf_sess.run(tf.global_variables_initializer())
        self.dead_sess.run(tf.global_variables_initializer())

        count = 0
        best_iter = 0
        previous_loss = 100000
        limit = 30

        for iter in range(self.n_iterations):
            self.conf_sess.run(self.optimizer, feed_dict={self.X: self.conf_train_x, self.Y: self.conf_train_y})
            l_val = self.conf_sess.run(self.mse, feed_dict={self.X: self.conf_valid_x, self.Y: self.conf_valid_y})
            if (iter + 1) % 20 == 0:
                l_train = self.conf_sess.run(self.mse, feed_dict={self.X: self.conf_train_x, self.Y: self.conf_train_y})
                print('Iteration: %04d, Train Loss: %0.4f, Valid Loss: %.4f' %(iter+1, l_train, l_val))

            if l_val > previous_loss:
                count += 1
                if count > limit:
                    break
            else:
                previous_loss = l_val
                best_iter = iter
                count = 0
        print('Iteration: %04d, Train Loss: %0.4f, Valid Loss: %.4f, Best Iter: %d' %(iter+1, l_train, l_val, best_iter))

        count = 0
        best_iter = 0
        previous_loss = 100000
        limit = 30

        for iter in range(self.n_iterations):
            self.dead_sess.run(self.optimizer, feed_dict={self.X: self.dead_train_x, self.Y: self.dead_train_y})
            l_val = self.dead_sess.run(self.mse, feed_dict={self.X: self.dead_valid_x, self.Y: self.dead_valid_y})
            if (iter + 1) % 20 == 0:
                l_train = self.dead_sess.run(self.mse, feed_dict={self.X: self.dead_train_x, self.Y: self.dead_train_y})
                print('Iteration: %04d, Train Loss: %0.4f, Valid Loss: %.4f' %(iter+1, l_train, l_val))

            if l_val > previous_loss:
                count += 1
                if count > limit:
                    break
            else:
                previous_loss = l_val
                best_iter = iter
                count = 0
        print('Iteration: %04d, Train Loss: %0.4f, Valid Loss: %.4f, Best Iter: %d' %(iter+1, l_train, l_val, best_iter))

    def predict(self):
        if self.conf_sess is None or self.dead_sess is None:
            self.train()

        conf_pred_data = self.conf_data.iloc[:, -self.n_steps:]
        dead_pred_data = self.dead_data.iloc[:, -self.n_steps:]

        locales = conf_pred_data.index
        cur_date = conf_pred_data.columns[-1]

        conf_pred_x = np.array(conf_pred_data).reshape(-1, self.n_steps, 1)
        dead_pred_x = np.array(dead_pred_data).reshape(-1, self.n_steps, 1)

        CovidResult.reset_table()
        result = []

        for _ in range(self.n_predictions):
            conf_pred_y = self.conf_sess.run(self.predictions, feed_dict={self.X: conf_pred_x})
            conf_pred_y = [[[int(p[-1])]] for p in conf_pred_y]

            dead_pred_y = self.dead_sess.run(self.predictions, feed_dict={self.X: dead_pred_x})
            dead_pred_y = [[[int(p[-1])]] for p in dead_pred_y]

            cur_date += datetime.timedelta(days=1)
            for l, c, d in zip(locales, conf_pred_y, dead_pred_y):
                result.append(CovidResult(date=cur_date, locale=l, confirm=c[0][0], dead=d[0][0]))
            CovidResult.insert(result)

            conf_pred_x = np.concatenate([conf_pred_x, conf_pred_y], axis=1)[:, 1:]
            dead_pred_x = np.concatenate([dead_pred_x, dead_pred_y], axis=1)[:, 1:]


def moving_window(data, n_steps=50):
    window_size = n_steps + 1
    window = np.array([data[i][j:j+window_size]
                       for j in range(data.shape[1]-window_size)
                       for i in range(data.shape[0])])
    return window[:, :-1].reshape(-1, n_steps, 1), window[:, 1:].reshape(-1, n_steps, 1)