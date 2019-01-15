#!/bin/bash

IN=$( cat hello );
arrIN=(${IN//@/ });

echo ${arrIN[0]};
echo ${arrIN[1]};

python3 discoveryServer.py
