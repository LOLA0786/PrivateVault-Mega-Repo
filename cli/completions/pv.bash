_pv_completions() {
  local cur prev cmds
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"
  cmds="login status tenant quorum approvals evidence demo"

  if [[ ${COMP_CWORD} -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
    return 0
  fi

  case "${COMP_WORDS[1]}" in
    tenant)
      COMPREPLY=( $(compgen -W "create list" -- "${cur}") )
      ;;
    quorum)
      COMPREPLY=( $(compgen -W "get set" -- "${cur}") )
      ;;
    approvals)
      COMPREPLY=( $(compgen -W "list" -- "${cur}") )
      ;;
    evidence)
      COMPREPLY=( $(compgen -W "export" -- "${cur}") )
      ;;
    demo)
      COMPREPLY=( $(compgen -W "up" -- "${cur}") )
      ;;
  esac
}

complete -F _pv_completions pv
