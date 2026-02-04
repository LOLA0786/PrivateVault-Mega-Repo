#compdef pv

_pv() {
  local -a commands
  commands=(login status tenant quorum approvals evidence demo)

  if (( CURRENT == 2 )); then
    _describe 'command' commands
    return
  fi

  case ${words[2]} in
    tenant)
      _describe 'tenant' 'create list'
      ;;
    quorum)
      _describe 'quorum' 'get set'
      ;;
    approvals)
      _describe 'approvals' 'list'
      ;;
    evidence)
      _describe 'evidence' 'export'
      ;;
    demo)
      _describe 'demo' 'up'
      ;;
  esac
}

_pv "$@"
