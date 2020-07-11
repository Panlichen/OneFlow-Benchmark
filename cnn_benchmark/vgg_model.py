from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import oneflow as flow
from model_util import conv2d_layer


def _conv_block(in_blob, index, filters, conv_times):
    conv_block = []
    conv_block.insert(0, in_blob)
    for i in range(conv_times):
        conv_i = conv2d_layer(
            name="conv{}".format(index),
            input=conv_block[i],
            filters=filters,
            kernel_size=3,
            strides=1,
        )
        conv_block.append(conv_i)
        index += 1

    return conv_block


def vgg16(images, need_transpose=False):

    if need_transpose:
        images = flow.transpose(images, name="transpose", perm=[0, 3, 1, 2])

    conv1 = _conv_block(images, 0, 64, 2)
    pool1 = flow.nn.max_pool2d(conv1[-1], 2, 2, "VALID", "NCHW", name="pool1")

    conv2 = _conv_block(pool1, 2, 128, 2)
    pool2 = flow.nn.max_pool2d(conv2[-1], 2, 2, "VALID", "NCHW", name="pool2")

    conv3 = _conv_block(pool2, 4, 256, 3)
    pool3 = flow.nn.max_pool2d(conv3[-1], 2, 2, "VALID", "NCHW", name="pool3")

    conv4 = _conv_block(pool3, 7, 512, 3)
    pool4 = flow.nn.max_pool2d(conv4[-1], 2, 2, "VALID", "NCHW", name="pool4")

    conv5 = _conv_block(pool4, 10, 512, 3)
    pool5 = flow.nn.max_pool2d(conv5[-1], 2, 2, "VALID", "NCHW", name="pool5")

    fc6 = flow.layers.dense(
        inputs=flow.reshape(pool5, [pool5.shape[0], -1]),
        units=4096,
        activation=flow.keras.activations.relu,
        use_bias=True,
        kernel_initializer=flow.truncated_normal(0.816496580927726),
        bias_initializer=flow.constant_initializer(),
        name="fc1",
    )

    fc6 = flow.nn.dropout(fc6, rate=0.5)

    fc7 = flow.layers.dense(
        inputs=fc6,
        units=4096,
        activation=flow.keras.activations.relu,
        use_bias=True,
        kernel_initializer=flow.truncated_normal(0.816496580927726),
        bias_initializer=flow.constant_initializer(),
        name="fc2",
    )
    fc7 = flow.nn.dropout(fc7, rate=0.5)

    fc8 = flow.layers.dense(
        inputs=fc7,
        units=1001,
        use_bias=True,
        kernel_initializer=flow.truncated_normal(0.816496580927726),
        bias_initializer=flow.constant_initializer(),
        name="fc_final",
    )

    return fc8