import numpy as np
import torch
from model import SimCSE
import torch.optim as optim
import time
import random
import data
import os
import copy

# 设置随机种子
def set_seed(seeds):
    np.random.seed(seeds)
    torch.manual_seed(seeds)
    torch.cuda.manual_seed_all(seeds)
    torch.backends.cudnn.deterministic = True  # 保证每次结果一样

def do_train(train_data_loader,last_new_checkpoint, save_dir='checkpoints',learning_rate = 1E-6,  margin=0.1, scale=20, output_emb_size=256, epochs = 3, rdrop_coef = 0.1, dup_rate=0.3):
    ngpu = 1
    use_cuda = torch.cuda.is_available()  # 检测是否有可用的gpu
    device = torch.device("cuda:0" if (use_cuda and ngpu > 0) else "cpu")
    # device = torch.device("cpu")
    print('*' * 8, 'device:', device)
    model = SimCSE(
        margin=margin,
        scale=scale,
        output_emb_size=output_emb_size,
        device=device)
    model = model.to(device)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    init_epoch = 0
    if len(os.listdir(save_dir)) > 0:
        print('*' * 27, 'Loading model weights...')
        ckpt = torch.load(save_dir + '/'+ last_new_checkpoint)  # dict  save在GPU 加载到 GPU
        init_epoch = int(last_new_checkpoint.split('_')[0][-3:])
        print('*' * 27, 'init_epoch=', init_epoch)
        model_sd = ckpt['net']
        if device.type == 'cuda' and ngpu > 1:
            model.module.load_state_dict(model_sd)
        else:
            model.load_state_dict(model_sd)
        print('*' * 27, 'Model loaded success!')
    # if ngpu > 1:
    #     model = torch.nn.DataParallel(model)  # 设置并行执行  device_ids=[0,1]

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    # lr_scheduler = LinearDecayWithWarmup(optimizer, warmup_steps=1000, total_steps=15000, warmup_rate=0.002)
    model.train()  # 设置train mode
    tic_train = time.time()
    min_loss = 0.0
    for epoch in range(init_epoch + 1, init_epoch + epochs + 1):
        loss_sum = 0.0
        for step, batch in enumerate(train_data_loader, start=1):
            query_input_ids, query_token_type_ids, title_input_ids, title_token_type_ids = batch
            if random.random() < 0.2:
                title_input_ids, title_token_type_ids = query_input_ids, query_token_type_ids
                query_input_ids, query_token_type_ids = data.word_repetition(query_input_ids, query_token_type_ids, dup_rate)
                title_input_ids, title_token_type_ids = data.word_repetition(title_input_ids, title_token_type_ids, dup_rate)
            query_input_ids = query_input_ids.to(device)
            query_token_type_ids = query_token_type_ids.to(device)
            title_input_ids = title_input_ids.to(device)
            title_token_type_ids = title_token_type_ids.to(device)
            loss, kl_loss = model(
                query_input_ids=query_input_ids,
                title_input_ids=title_input_ids,
                query_token_type_ids=query_token_type_ids,
                title_token_type_ids=title_token_type_ids)

            loss = loss + kl_loss * rdrop_coef
            loss_sum += loss
            if step % 10 == 0:
                print(
                    "Batchstep epoch: %d, batch: %d, loss: %.5f, speed: %.2f step/s"
                    % (epoch, step, loss_sum/step,
                       10 / (time.time() - tic_train)))
                tic_train = time.time()
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        # lr_scheduler.step()
        if min_loss>loss_sum/step or min_loss==0.0:
            min_loss = loss_sum/step
            save_dir_model = save_dir
            if not os.path.exists(save_dir_model):
                os.makedirs(save_dir_model)
            checkpoint = os.path.join(save_dir_model, f'epoch{epoch:03d}_valacc{loss_sum/step:.3f}_ckpt.tar')
            # if device.type == 'cuda' and ngpu > 1:
            #     model_sd = copy.deepcopy(model.module.state_dict())
            # else:
            model_sd = copy.deepcopy(model.state_dict())
            torch.save({
                'loss': loss_sum / step,
                'epoch': epoch,
                'net': model_sd,
                'opt': optimizer.state_dict(),
            }, checkpoint)
    return

def LinearDecayWithWarmup(optimizer, warmup_steps, total_steps, warmup_rate=0.002):
    """
    设置学习率按照线性衰减方式变化，并在开始训练之前进行预热操作。
    
    参数：
        optimizer: 优化器对象
        warmup_steps: 预热步数
        total_steps: 总步数
        warmup_rate: 预热学习率增加的比例
        min_lr: 最小学习率
    """
    # 计算学习率增加的比例
    linear_rate = (1.0 - warmup_rate) * (total_steps - warmup_steps) / (total_steps - warmup_steps + 1)
    # 计算预热学习率
    warmup_lr = linear_rate * warmup_steps / (warmup_steps + 1)
    # 初始化学习率变量
    lr = optimizer.param_groups[0]['lr'] = warmup_lr
    for i in range(1, len(optimizer.param_groups)):
        optimizer.param_groups[i]['lr'] = lr
    # 定义学习率调度器
    scheduler = optim.lr_scheduler.LambdaLR(optimizer, lambda step: (1.0 - step / warmup_steps) if step < warmup_steps else (linear_rate + (1.0 - linear_rate) * step / total_steps), last_epoch=-1)
    return scheduler



