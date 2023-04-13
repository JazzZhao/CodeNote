import paddle
import paddlenlp
from paddlenlp.dataaug import WordSubstitute
from paddlenlp.data import Tuple, Pad
from paddlenlp.datasets import load_dataset
import paddle.nn.functional as F

from functools import partial

def creat_dataloader(dataset, trans_fn):
    if trans_fn:
        dataset.


def convert_example(example, tokenizer, max_seq_length=512):
    #文本转化为ID的形式
    result = []

    for key, value in example.items():
        if 'label' in key:
            result += [example['label']]
        else:
            encoded_inputs = tokenizer(text = value, max_seq_length = max_seq_length)
            input_ids = encoded_inputs['input_ids']
            token_type_ids = encoded_inputs['token_type_ids']
            result += [input_ids, token_type_ids]
    return result

##引入模型
modle_name = "rocketqa-zh-base-query-encoder"
tokenizer = paddlenlp.transformers.ErnieTokenizer.from_pretrained(modle_name)

trans_fn = partial(convert_example, tokenizer = tokenizer, max_seq_length = 64)

if __name__ == "__main__":
    creat_dataloader()