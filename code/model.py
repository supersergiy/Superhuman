from __future__ import print_function
from collections import OrderedDict
import time

import torch
from torch import nn
from torch.nn import functional as F

import loss
from rsunet import RSUNet


class TrainNet(RSUNet):
    """
    RSUNet for training.
    """
    def __init__(self, opt):
        super(TrainNet, self).__init__(opt.in_spec, opt.out_spec, opt.depth,
                                       momentum=opt.momentum)
        self.in_spec = opt.in_spec
        self.out_spec = opt.out_spec
        self.loss_fn = loss.BCELoss()

    def forward(self, sample):
        """Run forward pass and compute loss."""
        # Forward pass.
        inputs = [sample[k] for k in sorted(self.in_spec)]
        preds = super(TrainNet, self).forward(*inputs)
        # Evaluate loss.
        return self.eval_loss(preds, sample)

    def eval_loss(self, preds, sample):
        self.loss = OrderedDict()
        self.nmsk = OrderedDict()
        for i, k in enumerate(sorted(self.out_spec)):
            label = sample[k]
            mask = sample[k+'_mask'] if k+'_mask' in sample else None
            self.loss[k], self.nmsk[k] = self.loss_fn(preds[i], label, mask)
        return (list(self.loss.values()), list(self.nmsk.values()))

    def save(self, fpath):
        torch.save(super(TrainNet, self).state_dict(), fpath)

    def load(self, fpath):
        super(TrainNet, self).load_state_dict(torch.load(fpath))


class InferenceNet(RSUNet):
    """
    RSUNet for inference.
    """
    def __init__(self, opt):
        if opt.activation == 'relu':
		super(InferenceNet, self).__init__(opt.in_spec, opt.out_spec, opt.depth,
                                           use_bn=(not opt.no_BN), activation=F.relu)
        else:
		super(InferenceNet, self).__init__(opt.in_spec, opt.out_spec, opt.depth,
                                           use_bn=(not opt.no_BN), activation=F.elu)
        self.in_spec = opt.in_spec
        self.out_spec = opt.out_spec
        self.scan_spec = opt.scan_spec
        self.activation = F.sigmoid

    def forward(self, x):
        preds = super(InferenceNet, self).forward(x)
        return [self.activation(x) for x in preds]

    def load(self, fpath):
        super(InferenceNet, self).load_state_dict(torch.load(fpath))
