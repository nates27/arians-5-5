# $1:the absolute path of input file
# $2:the absolute path of output file

if [[ -n "$1" && -n "$2" ]]; then
    python tradestrat_final.py $1 $2
else
    echo "Insufficient input parameters!"
fi
