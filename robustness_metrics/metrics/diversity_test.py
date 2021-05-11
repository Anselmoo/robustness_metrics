# coding=utf-8
# Copyright 2021 The Robustness Metrics Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for robustness_metrics.metrics.diversity."""

from absl.testing import parameterized

import robustness_metrics as rm
import tensorflow as tf


class DiversityTest(parameterized.TestCase, tf.test.TestCase):

  @parameterized.parameters(
      (rm.metrics.diversity.cosine_distance,),
      (rm.metrics.diversity.disagreement,),
      (rm.metrics.diversity.kl_divergence,),
  )
  def testDiversityMetrics(self, metric_fn):
    # TODO(trandustin): Test shapes. Need to change API to make it consistent.
    batch_size = 2
    num_classes = 3
    logits_one = tf.random.normal([batch_size, num_classes])
    logits_two = tf.random.normal([batch_size, num_classes])
    _ = metric_fn(logits_one, logits_two)

  def testAveragePairwiseDiversity(self):
    num_models = 3
    batch_size = 2
    num_classes = 5
    logits = tf.random.normal([num_models, batch_size, num_classes])
    probs = tf.nn.softmax(logits)
    diversity = rm.metrics.AveragePairwiseDiversity()
    diversity.add_batch(probs, num_models=num_models)
    results = diversity.result()
    self.assertLen(results, 3)
    self.assertEqual(results['disagreement'].shape, [])
    self.assertEqual(results['average_kl'].shape, [])
    self.assertEqual(results['cosine_similarity'].shape, [])


if __name__ == '__main__':
  tf.test.main()
