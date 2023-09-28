import os
import numpy as np
import tqdm
from model import SimCSE
from transformers import BertTokenizer
import torch
from milvus_utils import (
    VecToMilvus
)
from config import (
    embedding_name,
    question_max_len
    )
import time

def convert_example(example, batch_size=1):
    print("*"*27, "start build_dataset")
    print("*"*27, len(example))
    print("*" * 27, "start encoding...")
    tokenizer = BertTokenizer.from_pretrained("ernie-3.0-base-zh")
    x_inputs = tokenizer.batch_encode_plus(example, 
                                    return_tensors='pt', 
                                    add_special_tokens=True, 
                                    max_length=question_max_len,
                                    padding='max_length',  # 默认是False  向batch里最长的句子补齐
                                    truncation='longest_first'
                                    )
    inp_dset = torch.utils.data.TensorDataset(x_inputs['input_ids'], x_inputs['token_type_ids'])
    return torch.utils.data.DataLoader(inp_dset,
                                            batch_size=batch_size,
                                            shuffle=False,
                                            num_workers=2)


class Predictor(object):
    def __init__(
        self,
        model_dir,
        max_seq_length=1024,
        batch_size=32,
    ):
        ngpu = 1
        use_cuda = torch.cuda.is_available()  # 检测是否有可用的gpu
        # device = torch.device("cuda:0" if (use_cuda and ngpu > 0) else "cpu")
        device = torch.device("cpu")
        self.max_seq_length = max_seq_length
        self.batch_size = batch_size
        model = SimCSE(
            margin=0.1,
            scale=20,
            output_emb_size=256,
            device=device)
        model = model.to(device)
        model.eval()
        print('*' * 27, 'Loading model weights...')
        if not os.path.exists(model_dir):
            print(os.getcwd())
            raise ValueError("not find model file path {}".format(os.getcwd()+"/"+model_dir))
        ckpt = torch.load(model_dir)  # dict  save在GPU 加载到 GPU
        model_sd = ckpt['net']
        if device.type == 'cuda' and ngpu > 1:
            model.module.load_state_dict(model_sd)
        else:
            model.load_state_dict(model_sd)
        print('*' * 27, 'Model loaded success!')
        self.model = model

    def predict(self, data, is_batch=True):
        query_embedding = None
        if is_batch:
            inp_dloader = convert_example(data, batch_size=self.batch_size)
            query_embedding = self.model.get_semantic_embedding(inp_dloader)
        else:
            print("*"*27, "start build_dataset")
            print("*"*27, len(data))
            print("*" * 27, "start encoding...")
            tokenizer = BertTokenizer.from_pretrained("ernie-3.0-base-zh")
            x_inputs = tokenizer.batch_encode_plus(data, 
                                    return_tensors='pt', 
                                    add_special_tokens=True, 
                                    max_length=question_max_len,
                                    padding='max_length',  # 默认是False  向batch里最长的句子补齐
                                    truncation='longest_first'
                                    )
            query_embedding = self.model.get_pooled_embedding(
                    x_inputs['input_ids'], token_type_ids=x_inputs['token_type_ids'])
        return query_embedding
    