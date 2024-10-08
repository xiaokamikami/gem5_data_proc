set -x

ulimit -n 4096

export PYTHONPATH=`pwd`

# example_stats_dir=/nfs-nvme/home/share/wkf/SPEC06_EmuTasks_1215_allbump
example_stats_dir=/nfs/home/share/liyanqin/xs-perf/2403-perf-pf/SPEC06_EmuTasks_0313_0139
#example_stats_dir=/nfs/home/fengkehan/gem5_data_proc/ckpt_all_logs

mkdir -p results

tag="xs"

python3 pldm_log_get.py --logfile $example_stats_dir --outfile output_pldm.csv
python3 simpoint_cpt/compute_weighted.py --int-only \
    -r output_pldm.csv \
    -j /nfs/home/fengkehan/gem5_data_proc/cluster-0-0.json \
    --score results/$tag-score.csv
