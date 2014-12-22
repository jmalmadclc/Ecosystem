#!/bin/bash

#
# This script installs the bpbroker package (+ associated scripts) including
# any missing dependencies.  This includes a system-wide pip library for
# package management.
#

# Python pre-req
command -v python >/dev/null 2>&1 || { echo >&2 "Cannot locate python, required to pre-requisite"; exit 1; }


# pip pre-req (Python package manager)
command -v pip >/dev/null 2>&1 || { 
	echo >&2 "Cannot locate pip, installing"; 
	python get-pip.py;
	pip install --upgrade pip;
	}

# Installing/Upgrading bpbroker package
pip install --upgrade bpbroker

