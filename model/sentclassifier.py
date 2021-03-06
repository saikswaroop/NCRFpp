# -*- coding: utf-8 -*-
# @Author: Jie Yang
# @Date:   2019-01-01 21:11:50
# @Last Modified by:   Jie Yang,     Contact: jieynlp@gmail.com
# @Last Modified time: 2019-01-10 14:53:57

from __future__ import print_function
from __future__ import absolute_import
import torch
import torch.nn as nn
import torch.nn.functional as F
from .wordsequence import WordSequence

class SentClassifier(nn.Module):
    def __init__(self, data):
        super(SentClassifier, self).__init__()
        print("build sentence classification network...")
        print("use_char: ", data.use_char)
        if data.use_char:
            print("char feature extractor: ", data.char_feature_extractor)
        print("word feature extractor: ", data.word_feature_extractor)

        self.gpu = data.HP_gpu
        self.average_batch = data.average_batch_loss
        ## add two more label for downlayer lstm, use original label size for CRF
        label_size = data.label_alphabet_size
        data.label_alphabet_size += 2
        self.word_hidden = WordSequence(data)



    def neg_log_likelihood_loss(self, word_inputs, feature_inputs, word_seq_lengths, char_inputs, char_seq_lengths, char_seq_recover, batch_label, mask):
        outs = self.word_hidden.sentence_representation(word_inputs,feature_inputs, word_seq_lengths, char_inputs, char_seq_lengths, char_seq_recover)
        batch_size = word_inputs.size(0)
        loss_function = nn.NLLLoss(ignore_index=0, size_average=False)
        outs = outs.view(batch_size, -1)
        score = F.log_softmax(outs, 1)
        # print(score.size(), batch_label.view(batch_size).size())
        print(score)
        print(batch_label.view(batch_size))
        total_loss = loss_function(score, batch_label.view(batch_size))
        _, tag_seq  = torch.max(score, 1)
        if self.average_batch:
            total_loss = total_loss / batch_size
        print("aa")
        print(total_loss)
        exit(0)
        return total_loss, tag_seq


    def forward(self, word_inputs, feature_inputs, word_seq_lengths, char_inputs, char_seq_lengths, char_seq_recover, mask):
        outs = self.word_hidden.sentence_representation(word_inputs,feature_inputs, word_seq_lengths, char_inputs, char_seq_lengths, char_seq_recover)
        batch_size = word_inputs.size(0)
        outs = outs.view(batch_size, -1)
        _, tag_seq  = torch.max(outs, 1)
        return tag_seq


