#!/bin/bash

# Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# envsubst를 포함하는 gettext 설치
brew install gettext

# Homebrew 경로를 쉘 설정 파일에 추가
if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_CONFIG_FILE="$HOME/.zshrc"
elif [[ -n "$BASH_VERSION" ]]; then
    SHELL_CONFIG_FILE="$HOME/.bashrc"
else
    echo "지원되지 않는 셸입니다. Bash 또는 Zsh에서 실행하십시오."
    exit 1
fi

# PATH 설정 추가
echo 'export PATH=/opt/homebrew/bin:$PATH' >> "$SHELL_CONFIG_FILE"

# 셸 설정 파일을 소스하여 환경 변수 갱신
source "$SHELL_CONFIG_FILE"
