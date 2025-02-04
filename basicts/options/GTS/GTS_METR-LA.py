import os
from easydict import EasyDict
# runner
from basicts.runners.GTS_runner import GTSRunner
from basicts.data.base_dataset import BaseDataset
from basicts.metrics.mae import masked_mae
from basicts.metrics.mape import masked_mape
from basicts.metrics.rmse import masked_rmse
from basicts.losses.losses import masked_l1_loss
from basicts.utils.serialization import load_pkl

CFG = EasyDict()

resume = False      # DCRNN does not allow to load parameters since it creates parameters in the first iteration
if not resume:
    import random
    _ = random.randint(-1e6, 1e6)

# ================= general ================= #
CFG.DESCRIPTION = 'GTS model configuration'
CFG.RUNNER  = GTSRunner
CFG.DATASET_CLS   = BaseDataset
CFG.DATASET_NAME  = "METR-LA"
CFG.DATASET_TYPE  = 'Traffic speed'
CFG._       = _
CFG.GPU_NUM = 1
CFG.METRICS = {
    "MAE": masked_mae,
    "RMSE": masked_rmse,
    "MAPE": masked_mape
}

# ================= environment ================= #
CFG.ENV = EasyDict()
CFG.ENV.SEED    = 1
CFG.ENV.CUDNN = EasyDict()
CFG.ENV.CUDNN.ENABLED = True

# ================= model ================= #
CFG.MODEL = EasyDict()
CFG.MODEL.NAME  = 'GTS'
node_feats_full = load_pkl("datasets/{0}/data.pkl".format(CFG.DATASET_NAME))['processed_data'][..., 0]
train_index_list = load_pkl("datasets/{0}/index.pkl".format(CFG.DATASET_NAME))['train']
node_feats = node_feats_full[:train_index_list[-1][-1], ...]
CFG.MODEL.PARAM = {
    "cl_decay_steps"    : 2000,
    "filter_type"       : "dual_random_walk",
    "horizon"           : 12,
    "input_dim"         : 2,
    "l1_decay"          : 0,
    "max_diffusion_step": 3,
    "num_nodes"         : 207,
    "num_rnn_layers"    : 1,
    "output_dim"        : 1,
    "rnn_units"         : 64,
    "seq_len"           : 12,
    "use_curriculum_learning": True,
    "dim_fc"            : 383664,
    "node_feats"        : node_feats,
    "temp"              : 0.5,
    "k"                 : 10
}
CFG.MODEL.FROWARD_FEATURES = [0, 1]            
CFG.MODEL.TARGET_FEATURES  = [0]                

# ================= optim ================= #
CFG.TRAIN = EasyDict()
CFG.TRAIN.LOSS = masked_l1_loss
CFG.TRAIN.OPTIM = EasyDict()
CFG.TRAIN.OPTIM.TYPE = "Adam"
CFG.TRAIN.OPTIM.PARAM= {
    "lr":0.005,
    "eps":1e-3
}
CFG.TRAIN.LR_SCHEDULER = EasyDict()
CFG.TRAIN.LR_SCHEDULER.TYPE = "MultiStepLR"
CFG.TRAIN.LR_SCHEDULER.PARAM= {
    "milestones":[20, 40],
    "gamma":0.1
}

# ================= train ================= #
CFG.TRAIN.CLIP_GRAD_PARAM = {
    'max_norm': 5.0
}
CFG.TRAIN.NUM_EPOCHS    = 200
CFG.TRAIN.CKPT_SAVE_DIR = os.path.join(
    'checkpoints',
    '_'.join([CFG.MODEL.NAME, str(CFG.TRAIN.NUM_EPOCHS)])
)
CFG.TRAIN.SETUP_GRAPH   = True
# train data
CFG.TRAIN.DATA          = EasyDict()
CFG.TRAIN.NULL_VAL      = 0.0
## read data
CFG.TRAIN.DATA.DIR      = 'datasets/' + CFG.DATASET_NAME
## dataloader args, optional
CFG.TRAIN.DATA.BATCH_SIZE   = 64
CFG.TRAIN.DATA.PREFETCH     = False
CFG.TRAIN.DATA.SHUFFLE      = True
CFG.TRAIN.DATA.NUM_WORKERS  = 2
CFG.TRAIN.DATA.PIN_MEMORY   = False

# ================= validate ================= #
CFG.VAL = EasyDict()
CFG.VAL.INTERVAL = 1
# validating data
CFG.VAL.DATA = EasyDict()
## read data
CFG.VAL.DATA.DIR      = 'datasets/' + CFG.DATASET_NAME
## dataloader args, optional
CFG.VAL.DATA.BATCH_SIZE     = 64
CFG.VAL.DATA.PREFETCH       = False
CFG.VAL.DATA.SHUFFLE        = False
CFG.VAL.DATA.NUM_WORKERS    = 2
CFG.VAL.DATA.PIN_MEMORY     = False

# ================= test ================= #
CFG.TEST = EasyDict()
CFG.TEST.INTERVAL = 1
# validating data
CFG.TEST.DATA = EasyDict()
## read data
CFG.TEST.DATA.DIR      = 'datasets/' + CFG.DATASET_NAME
## dataloader args, optional
CFG.TEST.DATA.BATCH_SIZE    = 64
CFG.TEST.DATA.PREFETCH      = False
CFG.TEST.DATA.SHUFFLE       = False
CFG.TEST.DATA.NUM_WORKERS   = 2
CFG.TEST.DATA.PIN_MEMORY    = False
