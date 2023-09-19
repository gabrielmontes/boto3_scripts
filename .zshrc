export ZSH="$HOME/.oh-my-zsh"

# Plugins:
plugins=(
  git
)

source $ZSH/oh-my-zsh.sh
eval "$(starship init zsh)"

autoload -Uz vcs_info
precmd() { vcs_info }

zstyle ':vcs_info:git:*' formats '%b '

# Prompt:
setopt PROMPT_SUBST
PROMPT='%F{green}%n%f %F{blue}%~%f %F{red}${vcs_info_msg_0_}%f$ '

# Aliases:
alias bp='vim ~/.zshrc'
alias sa='source ~/.zshrc;echo "ZSH aliases sourced."'
alias awslogin="aws configure sso --profile state-manager"
alias terragrunt-apply="terragrunt plan && terragrunt apply --auto-approve"
