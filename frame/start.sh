#!/bin/bash

python3 discoveryServer.py &

IN=$( cat hello );
arrIN=(${IN//@/ });

echo ${arrIN[0]};
echo ${arrIN[1]};