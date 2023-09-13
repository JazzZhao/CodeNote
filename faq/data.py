import random
import numpy as np
import pandas as pd
import torch

def word_repetition(input_ids, token_type_ids, dup_rate=0.32):
    """Word Repetition strategy."""
    input_ids = input_ids.numpy().tolist()
    token_type_ids = token_type_ids.numpy().tolist()

    batch_size, seq_len = len(input_ids), len(input_ids[0])
    repetitied_input_ids = []
    repetitied_token_type_ids = []
    rep_seq_len = seq_len
    for batch_id in range(batch_size):
        cur_input_id = input_ids[batch_id]
        actual_len = np.count_nonzero(cur_input_id)
        dup_word_index = []
        # If sequence length is less than 5, skip it
        if actual_len > 5:
            dup_len = random.randint(a=0, b=max(2, int(dup_rate * actual_len)))
            # Skip cls and sep position
            dup_word_index = random.sample(list(range(1, actual_len - 1)), k=dup_len)

        r_input_id = []
        r_token_type_id = []
        for idx, word_id in enumerate(cur_input_id):
            # Insert duplicate word
            if idx in dup_word_index:
                r_input_id.append(word_id)
                r_token_type_id.append(token_type_ids[batch_id][idx])
            r_input_id.append(word_id)
            r_token_type_id.append(token_type_ids[batch_id][idx])
        after_dup_len = len(r_input_id)
        repetitied_input_ids.append(r_input_id)
        repetitied_token_type_ids.append(r_token_type_id)

        if after_dup_len > rep_seq_len:
            rep_seq_len = after_dup_len
    # Padding the data to the same length
    for batch_id in range(batch_size):
        after_dup_len = len(repetitied_input_ids[batch_id])
        pad_len = rep_seq_len - after_dup_len
        repetitied_input_ids[batch_id] += [0] * pad_len
        repetitied_token_type_ids[batch_id] += [0] * pad_len

    return torch.tensor(repetitied_input_ids, dtype=torch.int64), torch.tensor(
        repetitied_token_type_ids, dtype=torch.int64
    )

def build_dataset(tokenizer,train_path, batch_size):
    print("*"*27, "start build_dataset")
    data = pd.read_excel(train_path, names=['content', 'label'], index_col=False)
    data = data.dropna()
    x_data, y_data = data['content'], data['label']
    print("*"*27, x_data.shape, y_data.shape)
    print("*" * 27, "start encoding...")
    x_inputs = tokenizer.batch_encode_plus(x_data, 
                                    return_tensors='pt', 
                                    add_special_tokens=True, 
                                    max_length=1024,
                                    padding='longest',  # 默认是False  向batch里最长的句子补齐
                                    truncation='longest_first'
                                    )
    y_inputs = tokenizer.batch_encode_plus(y_data, 
                                    return_tensors='pt', 
                                    add_special_tokens=True, 
                                    max_length=1024,
                                    padding='longest',  # 默认是False  向batch里最长的句子补齐
                                    truncation='longest_first'
                                    )
    inp_dset = torch.utils.data.TensorDataset(x_inputs['input_ids'], x_inputs['token_type_ids'], 
                                              y_inputs['input_ids'], y_inputs['token_type_ids'])
    return torch.utils.data.DataLoader(inp_dset,
                                            batch_size=batch_size,
                                            shuffle=False,
                                            num_workers=2)
    

