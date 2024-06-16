#!/bin/bash

cd /opt/neurips-keyword-analysis/tools || exit 1

# tmux_window gpu_num val_fold
paired_values=(
  "1 2023"
  "2 2022"
  "3 2021"
  "4 2020"
  "5 2019"
  "6 2018"
)

my_session=1
tmux new-session -d -s ${my_session}  # 새로운 tmux 세션 생성

for pair in "${paired_values[@]}"
do
  my_window=$(echo "$pair" | cut -d ' ' -f1)
  year=$(echo "$pair" | cut -d ' ' -f2)

  tmux new-window -t "${my_session}:" -n "${my_window}"  # 새로운 윈도우 생성
  tmux send-keys -t "${my_session}:${my_window}" "python3 neurips_csv.py --year ${year}" Enter  # 해당 윈도우로 명령어 전달
done
