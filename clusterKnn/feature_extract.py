import os

import numpy as np
import paddle
from paddle import inference
from tqdm import tqdm

from paddlenlp.data import Pad, Tuple
from data import gen_text_file

def convert_example(example, tokenizer, max_seq_length=512, pad_to_max_seq_len=False):
    """
    Builds model inputs from a sequence.

    A BERT sequence has the following format:

    - single sequence: ``[CLS] X [SEP]``

    Args:
        example(obj:`list(str)`): The list of text to be converted to ids.
        tokenizer(obj:`PretrainedTokenizer`): This tokenizer inherits from :class:`~paddlenlp.transformers.PretrainedTokenizer`
            which contains most of the methods. Users should refer to the superclass for more information regarding methods.
        max_seq_len(obj:`int`): The maximum total input sequence length after tokenization.
            Sequences longer than this will be truncated, sequences shorter will be padded.
        is_test(obj:`False`, defaults to `False`): Whether the example contains label or not.

    Returns:
        input_ids(obj:`list[int]`): The list of query token ids.
        token_type_ids(obj: `list[int]`): List of query sequence pair mask.
    """

    result = []
    for key, text in example.items():
        encoded_inputs = tokenizer(text=text, max_seq_len=max_seq_length, pad_to_max_seq_len=pad_to_max_seq_len)
        input_ids = encoded_inputs["input_ids"]
        token_type_ids = encoded_inputs["token_type_ids"]
        result += [input_ids, token_type_ids]
    return result


class Predictor(object):
    def __init__(
        self,
        model_dir,
        device="gpu",
        max_seq_length=128,
        batch_size=32,
        use_tensorrt=False,
        precision="fp32",
        cpu_threads=10,
        enable_mkldnn=False,
    ):
        self.max_seq_length = max_seq_length
        self.batch_size = batch_size

        model_file = model_dir + "/inference.get_pooled_embedding.pdmodel"
        params_file = model_dir + "/inference.get_pooled_embedding.pdiparams"
        if not os.path.exists(model_file):
            print(os.getcwd())
            raise ValueError("not find model file path {}".format(model_file))
        if not os.path.exists(params_file):
            raise ValueError("not find params file path {}".format(params_file))
        config = paddle.inference.Config(model_file, params_file)

        if device == "gpu":
            # set GPU configs accordingly
            # such as initialize the gpu memory, enable tensorrt
            config.enable_use_gpu(100, 0)
            precision_map = {
                "fp16": inference.PrecisionType.Half,
                "fp32": inference.PrecisionType.Float32,
                "int8": inference.PrecisionType.Int8,
            }
            precision_mode = precision_map[precision]

            if use_tensorrt:
                config.enable_tensorrt_engine(
                    max_batch_size=batch_size, min_subgraph_size=30, precision_mode=precision_mode
                )
        elif device == "cpu":
            # set CPU configs accordingly,
            # such as enable_mkldnn, set_cpu_math_library_num_threads
            config.disable_gpu()
            if enable_mkldnn:
                # cache 10 different shapes for mkldnn to avoid memory leak
                config.set_mkldnn_cache_capacity(10)
                config.enable_mkldnn()
            config.set_cpu_math_library_num_threads(cpu_threads)
        elif device == "xpu":
            # set XPU configs accordingly
            config.enable_xpu(100)

        config.switch_use_feed_fetch_ops(False)
        self.predictor = paddle.inference.create_predictor(config)
        self.input_handles = [self.predictor.get_input_handle(name) for name in self.predictor.get_input_names()]
        self.output_handle = self.predictor.get_output_handle(self.predictor.get_output_names()[0])

    def predict(self, data, tokenizer):
        """
        Predicts the data labels.

        Args:
            data (obj:`List(str)`): The batch data whose each element is a raw text.
            tokenizer(obj:`PretrainedTokenizer`): This tokenizer inherits from :class:`~paddlenlp.transformers.PretrainedTokenizer`
                which contains most of the methods. Users should refer to the superclass for more information regarding methods.

        Returns:
            results(obj:`dict`): All the predictions labels.
        """

        def batchify_fn(
            samples,
            fn=Tuple(
                Pad(axis=0, pad_val=tokenizer.pad_token_id, dtype="int64"),  # input
                Pad(axis=0, pad_val=tokenizer.pad_token_id, dtype="int64"),  # segment
            ),
        ):
            return fn(samples)

        all_embeddings = []
        examples = []
        for idx, text in enumerate(tqdm(data)):
            input_ids, segment_ids = convert_example(
                text, tokenizer, max_seq_length=self.max_seq_length, pad_to_max_seq_len=True
            )
            examples.append((input_ids, segment_ids))
            if len(examples) >= self.batch_size:
                input_ids, segment_ids = batchify_fn(examples)
                self.input_handles[0].copy_from_cpu(input_ids)
                self.input_handles[1].copy_from_cpu(segment_ids)
                self.predictor.run()
                logits = self.output_handle.copy_to_cpu()
                all_embeddings.append(logits)
                examples = []

        if len(examples) > 0:
            input_ids, segment_ids = batchify_fn(examples)
            self.input_handles[0].copy_from_cpu(input_ids)
            self.input_handles[1].copy_from_cpu(segment_ids)
            self.predictor.run()
            logits = self.output_handle.copy_to_cpu()
            all_embeddings.append(logits)

        all_embeddings = np.concatenate(all_embeddings, axis=0)
        return all_embeddings