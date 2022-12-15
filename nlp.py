import torch
from torch import nn
from torch.nn import functional as F
import torchvision
from torchvision import transforms
from torch.utils import data
from tqdm import tqdm
from IPython import display
import matplotlib.pyplot as plt
import sys
import utils
import re
import collections
import random
# sys.path.append('/kaggle/input')
# from myutils import utils

class Vocab:
    """文本词表"""
    def __init__(self, tokens=None, min_freq=0, reserved_tokens=None):
        if tokens is None:
            tokens = []
        if reserved_tokens is None:
            reserved_tokens = []
        ##按出现频率排序
        counter = count_corpus(tokens)
        self._token_freqs = sorted(counter.items(), key=lambda x : x[1], reverse=True)
        #未知词的索引为0
        self.idx_to_token = ['<unk>'] + reserved_tokens
        self.token_to_idx = {token:idx for idx, token in enumerate(self.idx_to_token)}

        for token, freq in self._token_freqs:
            if freq<min_freq:
                break
            if token not in self.token_to_idx:
                self.idx_to_token.append(token)
                self.token_to_idx[token] = len(self.idx_to_token) - 1
    def __len__(self):
        return len(self.idx_to_token)

    def __getitem__(self, tokens):
        if not isinstance(tokens, (list, tuple)):
            return self.token_to_idx.get(tokens, self.unk)
        return [self.__getitem__(token) for token in tokens]
    
    def to_tokens(self, indices):
        if not isinstance(indices, (list, tuple)):
            return self.idx_to_token[indices]
        return [self.idx_to_token[index] for index in indices]

    @property
    def unk(self):
        return 0
    
    @property
    def token_freqs(self):
        return self._token_freqs

def count_corpus(tokens):  #@save
    """统计词元的频率"""
    # 这里的tokens是1D列表或2D列表
    if len(tokens) == 0 or isinstance(tokens[0], list):
        # 将词元列表展平成一个列表
        tokens = [token for line in tokens for token in line]
    return collections.Counter(tokens)    

def read_time_machines():
    with open("timemachine.txt", encoding='utf-8') as f:
        lines = f.readlines()
    return [re.sub('[^A-Za-z]+', ' ', line).strip().lower() for line in lines]

def tokenize(lines, token='word'):
    if token == 'word':
        return  [ line.split() for line in lines]
    elif token == 'char':
        return [list(line) for line in lines]
    else:
        print('错误，未知词元类型'+token)

def read_corpus_time_machine(max_tokens=-1):  #@save
    """返回时光机器数据集的词元索引列表和词表"""
    lines = read_time_machines()
    tokens = tokenize(lines, 'word')
    vocab = Vocab(tokens)
    # 因为时光机器数据集中的每个文本行不一定是一个句子或一个段落，
    # 所以将所有文本行展平到一个列表中
    corpus = [vocab[token] for line in tokens for token in line]
    if max_tokens > 0:
        corpus = corpus[:max_tokens]
    return corpus, vocab

#随机采样
def seq_data_iter_random(corpus,batch_size, num_steps):
    #随机生成一步内的随机数,并截取corpus
    corpus = corpus[random.randint(0, num_steps-1):]
    #减去1，是因为我们需要考虑标签
    num_subseqs = (len(corpus)-1)//num_steps
    initial_indices = list(i for i in range(0, num_subseqs*num_steps, num_steps))
    #打乱排序，形成随机抽样
    random.shuffle(initial_indices)

    def data(pos):
        return corpus[pos:pos+num_steps]

    num_batches = num_subseqs//batch_size
    for i in range(0, num_batches*batch_size, batch_size):
        # 在这里，initial_indices包含子序列的随机起始索引
        initial_indices_per_batch = initial_indices[i: i+batch_size]
        X = [data(j) for j in initial_indices_per_batch]
        Y = [data(j+1) for j in initial_indices_per_batch]
        yield torch.tensor(X), torch.tensor(Y)

#顺序采样
def seq_data_iter_sequential(corpus, batch_size, num_steps):
    #生成一个随机数
    offset = random.randint(0, num_steps)
    #减去1为了减去一个标签
    num_tokens = ((len(corpus)-1-offset)//batch_size)*batch_size
    Xs = torch.tensor(corpus[offset:offset+num_tokens])
    Ys = torch.tensor(corpus[offset+1:offset+num_tokens+1])
    Xs, Ys = Xs.reshape(batch_size, -1), Ys.reshape(batch_size, -1)
    num_batches = Xs.shape[1] // num_steps
    for i in range(0, num_batches*num_steps, num_steps):
        X = Xs[:,i:i+num_steps]
        Y = Ys[:,i:i+num_steps]
        yield X, Y

class SeqDataLoader:
    '''加载序列数据的迭代器'''
    def __init__(self, batch_size, num_steps, use_random_iter, max_tokens):
        if use_random_iter:
            self.data_iter_fn = seq_data_iter_random
        else:
            self.data_iter_fn = seq_data_iter_sequential
        self.corpus, self.vocab = read_corpus_time_machine(max_tokens=max_tokens)
        self.batch_size, self.num_steps = batch_size, num_steps
    def __iter__(self):
      return self.data_iter_fn(self.corpus, self.batch_size, self.num_steps)

def load_corpus_time_machine(batch_size, num_steps, use_random_iter=False, max_tokens = 10000):
    data_iter = SeqDataLoader(batch_size, num_steps, use_random_iter, max_tokens)
    return data_iter, data_iter.vocab

if __name__ == "__main__":
    train_iter, vocab = load_corpus_time_machine(32, 35)
    