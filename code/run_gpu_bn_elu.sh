#!/bin/bash
python test.py --exp_name test --data_names test --data_tag dynamic --gpu_ids 0 --no_eval --fov 22 224 224 --depth 5 --out_channels 17 --dummy --activation elu
