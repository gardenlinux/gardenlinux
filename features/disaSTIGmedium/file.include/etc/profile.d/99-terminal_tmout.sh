# shellcheck shell=sh disable=SC2148
if [ -z "${TMOUT+x}" ]; then
    TMOUT=900
    readonly TMOUT
    export TMOUT
fi
