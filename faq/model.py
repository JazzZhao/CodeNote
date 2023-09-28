import torch.nn as nn
import torch
import torch.nn.functional as F
from transformers import ErnieModel

class SimCSE(torch.nn.Module):
    def __init__(self,
                 dropout=None,
                 margin=0.0,
                 scale=20,
                 output_emb_size=None,
                 device = "cpu"):
        super().__init__()
        self.ptm = ErnieModel.from_pretrained("ernie-3.0-base-zh")
        # 显式的加一个dropout来控制
        self.dropout = nn.Dropout(dropout if dropout is not None else 0.1)

        # 考虑到性能和效率，我们推荐把output_emb_size设置成256
        # 向量越大，语义信息越丰富，但消耗资源越多
        self.output_emb_size = output_emb_size
        if output_emb_size > 0:
            self.emb_reduce_linear = torch.nn.Linear(768, output_emb_size)

        self.margin = margin
        
        # 为了使余弦相似度更容易收敛，我们选择把计算出来的余弦相似度扩大scale倍，一般设置成20左右
        self.sacle = scale
        # 二分类计算
        self.classifier = torch.nn.Linear(output_emb_size, 2)
        self.device = device

    def compute_kl_loss (self, p, q, pad_mask=None):
        #Rdrop
        p_loss = F.kl_div(F.log_softmax(p, dim=-1), F.softmax(q, dim=-1), reduction='none')
        q_loss = F.kl_div(F.log_softmax(q, dim=-1), F.softmax(p, dim=-1), reduction='none')
        
        # pad_mask is for seq-level tasks
        if pad_mask is not None:
            p_loss.masked_fill_(pad_mask, 0.)
            q_loss.masked_fill_(pad_mask, 0.)

        # You can choose whether to use function "sum" and "mean" depending on your task
        p_loss = p_loss.sum()
        q_loss = q_loss.sum()

        loss = (p_loss + q_loss) / 2
        return loss

    def get_pooled_embedding(self,
                             input_ids,
                             token_type_ids=None,
                             with_pooler=True):

        # Note: cls_embedding is poolerd embedding with act tanh 
        modle_result = self.ptm(input_ids, token_type_ids)
        sequence_output, cls_embedding = modle_result.last_hidden_state, modle_result.pooler_output
        if with_pooler == False:
            cls_embedding = sequence_output[:, 0, :]

        if self.output_emb_size > 0:
            cls_embedding = self.emb_reduce_linear(cls_embedding)

        cls_embedding = self.dropout(cls_embedding)
        cls_embedding = F.normalize(cls_embedding, p=2, dim=-1)

        return cls_embedding

    def get_semantic_embedding(self, data_loader):
        self.eval()
        with torch.no_grad():
            for batch_data in data_loader:
                input_ids, token_type_ids = batch_data
                text_embeddings = self.get_pooled_embedding(
                    input_ids, token_type_ids=token_type_ids)
                yield text_embeddings
    
    def cosine_sim(self,
                   query_input_ids,
                   title_input_ids,
                   query_token_type_ids=None,
                   title_token_type_ids=None,
                   with_pooler=True):

        query_cls_embedding = self.get_pooled_embedding(
            query_input_ids,
            query_token_type_ids,
            with_pooler=with_pooler)

        title_cls_embedding = self.get_pooled_embedding(
            title_input_ids,
            title_token_type_ids,
            with_pooler=with_pooler)

        cosine_sim = torch.sum(query_cls_embedding * title_cls_embedding,
                                axis=-1)
        return cosine_sim

    def forward(self,
                query_input_ids,
                title_input_ids,
                query_token_type_ids=None,
                title_token_type_ids=None):
        # 第 1 次编码: 文本经过无监督语义索引模型编码后的语义向量 
        # [N, output_emb_size]
        query_cls_embedding = self.get_pooled_embedding(
            query_input_ids, query_token_type_ids)

        # 第 2 次编码: 文本经过无监督语义索引模型编码后的语义向量 
        # [N, output_emb_size]
        title_cls_embedding = self.get_pooled_embedding(
            title_input_ids, title_token_type_ids)

        # 使用R-Drop
        logits1=self.classifier(query_cls_embedding)
        logits2 = self.classifier(title_cls_embedding)
        kl_loss = self.compute_kl_loss(logits1, logits2)

        # 相似度矩阵: [N, N]
        cosine_sim = torch.matmul(
            query_cls_embedding, title_cls_embedding.T)

        # substract margin from all positive samples cosine_sim()
        # 填充self.margin值，比如margin为0.2，query_cls_embedding.shape[0]=2 
        # margin_diag: [0.2,0.2]
        margin_diag = torch.full(
            size=[query_cls_embedding.shape[0]],
            fill_value=self.margin,
            dtype=torch.int64).to(self.device)
        # input paddle.diag(margin_diag): [[0.2,0],[0,0.2]]
        # input cosine_sim : [[1.0,0.6],[0.6,1.0]]
        # output cosine_sim: [[0.8,0.6],[0.6,0.8]]
        cosine_sim = cosine_sim - torch.diag(margin_diag)

        # scale cosine to ease training converge
        cosine_sim *= self.sacle
        # 转化成分类任务: 对角线元素是正例，其余元素为负例
        # labels : [0,1,2,3]
        labels = torch.arange(0, query_cls_embedding.shape[0], dtype=torch.int64)
        labels = labels.to(self.device)
        # labels : [[0],[1],[2],[3]]
        # labels = torch.reshape(labels, shape=[-1, 1])
        # 交叉熵损失函数
        loss = F.cross_entropy(input=cosine_sim, target=labels)
        return loss, kl_loss