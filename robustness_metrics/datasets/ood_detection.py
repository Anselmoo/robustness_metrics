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

# Lint as: python3
"""Define datasets for OOD detection tasks."""

import abc
from typing import Callable, Optional

from robustness_metrics.common import types
from robustness_metrics.datasets import base
from robustness_metrics.datasets import tfds as rm_tfds
import tensorflow as tf


def _set_label_to_one(feature):
  feature["label"] = tf.ones_like(feature["label"])
  return feature


def _set_label_to_zero(feature):
  feature["label"] = tf.zeros_like(feature["label"])
  return feature


def _keep_common_fields(feature, spec):
  """Delete the keys of feature that are not in spec."""
  if not isinstance(feature, dict): return feature
  common_keys = set(feature.keys()) & set(spec.keys())
  return {
      key: _keep_common_fields(feature[key], spec[key]) for key in common_keys
  }


def _concatenate(in_ds: tf.data.Dataset,
                 out_ds: tf.data.Dataset) -> tf.data.Dataset:
  """Concatenate in_ds and out_ds, making sure they have compatible specs."""
  in_spec = in_ds.element_spec
  out_spec = out_ds.element_spec

  def format_in_ds(feature):
    feature = _set_label_to_one(feature)
    return _keep_common_fields(feature, out_spec)

  def format_out_ds(feature):
    feature = _set_label_to_zero(feature)
    return _keep_common_fields(feature, in_spec)

  return in_ds.map(format_in_ds).concatenate(out_ds.map(format_out_ds))


class OodDetectionDataset(base.Dataset, metaclass=abc.ABCMeta):
  """A dataset made of a pair of one in- and one out-of-distribution datasets.

  In this binary (detection) task, the in-distribution dataset has labels 1 and
  the out-of-distrbution dataset has labels 0.

  See https://arxiv.org/pdf/2106.03004.pdf for more background.
  """

  @property
  def info(self) -> base.DatasetInfo:
    return base.DatasetInfo(num_classes=2)

  @abc.abstractproperty
  def in_dataset(self) -> base.Dataset:
    """The in-distribution dataset."""

  @abc.abstractproperty
  def out_dataset(self) -> base.Dataset:
    """The out-of-distribution dataset."""

  def load(self,
           preprocess_fn: Optional[Callable[[types.Features], types.Features]]
           ) -> tf.data.Dataset:

    in_ds = self.in_dataset.load(preprocess_fn)
    out_ds = self.out_dataset.load(preprocess_fn)
    return _concatenate(in_ds, out_ds)


@base.registry.register("cifar10_vs_cifar100")
class Cifar10VsCifar100Dataset(OodDetectionDataset):
  """The CIFAR-10 vs. CIFAR-100 ood detection dataset."""

  @property
  def in_dataset(self) -> base.Dataset:
    return rm_tfds.Cifar10Dataset()

  @property
  def out_dataset(self) -> base.Dataset:
    return rm_tfds.Cifar100Dataset()


@base.registry.register("cifar100_vs_cifar10")
class Cifar100VsCifar10Dataset(OodDetectionDataset):
  """The CIFAR-100 vs. CIFAR-10 ood detection dataset."""

  @property
  def in_dataset(self) -> base.Dataset:
    return rm_tfds.Cifar100Dataset()

  @property
  def out_dataset(self) -> base.Dataset:
    return rm_tfds.Cifar10Dataset()