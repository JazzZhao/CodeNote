from transformers import BertTokenizer
import data
import train
import argparse

parser = argparse.ArgumentParser(description='Chinese Text FAQ')
parser.add_argument('--train_path', type=str, required=True, help='train path')
parser.add_argument('--save_dir', type=str, required=True, help='save dir')
parser.add_argument('--batch_size', type=int, default=10, help='batch_size')
parser.add_argument('--epochs', type=int, default=10, help='epochs')
parser.add_argument('--last_new_checkpoint', type=str, default=None, help='last new checkpoint')
parser.add_argument('--learning_rate', type=float, default=1E-10, help='learning rate')
args = parser.parse_args()

if __name__ == '__main__':
    train.set_seed(1024)
    tokenizer = BertTokenizer.from_pretrained("ernie-3.0-base-zh")
    inp_dloader = data.build_dataset(tokenizer,train_path=args.train_path, batch_size=args.batch_size)
    # inp_dloader = data.build_dataset(tokenizer,train_path="abc.xlsx", batch_size=10)
    x_1, x_2, y_1, y_2 = next(iter(inp_dloader))
    print('sample:', 'x:', x_1[:10], x_1.shape, x_2.shape, x_2.shape, 'y:', y_1[:10], y_1.shape, y_2[:10], y_2.shape) 
    train.do_train(inp_dloader, last_new_checkpoint=args.last_new_checkpoint,save_dir=args.save_dir, margin=0.1,scale=20, output_emb_size=256, epochs = args.epochs, learning_rate =args.learning_rate)
    # train.do_train(inp_dloader, last_new_checkpoint="epoch010_valacc2.169_ckpt.tar",save_dir="checkpoints", margin=0.1,scale=20, output_emb_size=256, epochs = 10)