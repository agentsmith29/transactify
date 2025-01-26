# =====================================================================================================================
# Echo formatting functions
# =====================================================================================================================
function echo_ok() {
    echo -e "\e[32m[OK]\e[0m $1"
}

function echo_dbg() {
    echo -e "\e[90m[DBG]\e[0m $1"
}

function echo_err() {
    echo -e "\e[31m[ERR]\e[0m $1"
}

function echo_inf() {
    echo -e "\e[34m[INF]\e[0m $1"
}

function echo_warn() {
    echo -e "\e[33m[WRN]\e[0m $1"
}

function relpath() {
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}